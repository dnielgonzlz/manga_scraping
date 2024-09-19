import shutil
import requests
import os
import json
import logging
import time
from scrapegraphai.graphs import SmartScraperGraph
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from concurrent.futures import ThreadPoolExecutor, as_completed
# Import the API key

# Define the configuration for the scraping pipeline
graph_config = {
    "llm": {
        "api_key": "OPENAI_API_KEY",
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
}

def get_manga_data_path(manga_title):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    manga_data_folder = os.path.join(desktop_path, "Manga Scraping", "Manga Data")
    os.makedirs(manga_data_folder, exist_ok=True)
    formatted_title = manga_title.replace(' ', '-')
    json_filename = f"{formatted_title}_data.json"
    return os.path.join(manga_data_folder, json_filename)

def scrape_manga_data(manga_title, manga_url):
    smart_scraper_graph = SmartScraperGraph(
        prompt=f"""
        Your goal is to find the chapters of the manga titled "{manga_title}" that are listed in the URL that the user provides you with.
        The structure of the naming will usually be: {manga_title} + Chapter + Number of the chapter.
        Create a JSON file with the link of each chapter and the number of the chapter.    
        """,
        source=manga_url,
        config=graph_config
    )
    result = smart_scraper_graph.run()
    return result.get('chapters', [])

def collect_image_links(chapters):
    manga_data = {"chapters": []}
    for chapter in chapters:
        chapter_number = chapter.get('chapter_number')
        chapter_link = chapter.get('link')
        if chapter_number and chapter_link:
            chapter_scraper = SmartScraperGraph(
                prompt="""
                Your goal is to find all the images in the chapter that are listed in the URL that the user provides you with.
                Create a JSON file with the link of each image.    
                """,
                source=chapter_link,
                config=graph_config
            )
            chapter_result = chapter_scraper.run()
            images = chapter_result.get('images', [])
            pages = {f"page-{i+1}": image for i, image in enumerate(images)}
            manga_data["chapters"].append({
                "chapter": chapter_number,
                "pages": pages
            })
    return manga_data

def download_image(chapter_num, page, url, download_folder):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        page_num = page.split('-')[1]  # Extract the page number
        image_filename = f"chapter_{chapter_num}_page_{page_num}.jpg"
        image_path = os.path.join(download_folder, image_filename)
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: Chapter {chapter_num}, Page {page_num}")
        return (chapter_num, page_num, image_path)
    except requests.RequestException as e:
        print(f"\nFailed to download Chapter {chapter_num}, Page {page}: {e}\n")
        return None
    
def download_images(manga_data, manga_title, download_start, download_end):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, "Manga Scraping", "Downloaded Images", manga_title)
    os.makedirs(download_folder, exist_ok=True)

    total_pages = sum(len(chapter['pages']) for chapter in manga_data['chapters'] if download_start <= int(chapter["chapter"]) <= download_end)
    print(f"Starting to download {total_pages} pages from {download_end - download_start + 1} chapters.")

    start_time = time.time()
    downloaded_pages = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for chapter in sorted(manga_data["chapters"], key=lambda x: int(x["chapter"])):
            chapter_num = int(chapter["chapter"])
            if download_start <= chapter_num <= download_end:
                for page, image_url in sorted(chapter["pages"].items(), key=lambda x: int(x[0].split('-')[1])):
                    futures.append(executor.submit(download_image, chapter_num, page, image_url, download_folder))

        downloaded_images = []
        for future in as_completed(futures):
            result = future.result()
            if result:
                downloaded_images.append(result)
                downloaded_pages += 1
                print(f"Downloaded: {downloaded_pages}/{total_pages} pages")

    end_time = time.time()
    print(f"Total download time: {end_time - start_time:.2f} seconds")
    print(f"Successfully downloaded {downloaded_pages}/{total_pages} pages")

    # Updated sorting function
    def sort_key(x):
        chapter, page, _ = x
        return (int(chapter), int(page.split('_')[-1].split('.')[0]))

    return sorted(downloaded_images, key=sort_key)

def process_image(image_path):
    img = Image.open(image_path)
    kindle_width, kindle_height = 600, 800
    img_width, img_height = img.size
    aspect_ratio = img_height / float(img_width)
    if aspect_ratio > 1:
        new_height = kindle_height
        new_width = int(kindle_height / aspect_ratio)
    else:
        new_width = kindle_width
        new_height = int(kindle_width * aspect_ratio)
    img = img.resize((new_width, new_height), Image.LANCZOS)
    return ImageReader(img), new_height

def download_images(manga_data, manga_title, download_start, download_end):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, "Manga Scraping", "Downloaded Images", manga_title)
    os.makedirs(download_folder, exist_ok=True)

    total_pages = sum(len(chapter['pages']) for chapter in manga_data['chapters'] if download_start <= int(chapter["chapter"]) <= download_end)
    print(f"Starting to download {total_pages} pages from {download_end - download_start + 1} chapters.")

    start_time = time.time()
    downloaded_pages = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for chapter in sorted(manga_data["chapters"], key=lambda x: int(x["chapter"])):
            chapter_num = int(chapter["chapter"])
            if download_start <= chapter_num <= download_end:
                for page, image_url in sorted(chapter["pages"].items(), key=lambda x: int(x[0].split('-')[1])):
                    futures.append(executor.submit(download_image, chapter_num, page, image_url, download_folder))

        downloaded_images = []
        for future in as_completed(futures):
            result = future.result()
            if result:
                downloaded_images.append(result)
                downloaded_pages += 1
                print(f"Downloaded: {downloaded_pages}/{total_pages} pages")

    end_time = time.time()
    print(f"Total download time: {end_time - start_time:.2f} seconds")
    print(f"Successfully downloaded {downloaded_pages}/{total_pages} pages")

    def sort_key(x):
        chapter, page, _ = x
        return (int(chapter), int(page))

    return sorted(downloaded_images, key=sort_key)

def create_pdf_from_images(downloaded_images, manga_title, download_start, download_end):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    pdf_output_folder = os.path.join(desktop_path, "Manga Scraping", "Mangas PDFs")
    os.makedirs(pdf_output_folder, exist_ok=True)

    formatted_title = manga_title.replace(' ', '-')
    pdf_filename = os.path.join(pdf_output_folder, f"{formatted_title}, {download_start}-{download_end}.pdf")

    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    total_pages = len(downloaded_images)
    print(f"Starting to create PDF with {total_pages} pages.")

    start_time = time.time()
    processed_pages = 0

    for chapter_num, page, image_path in downloaded_images:
        try:
            img_reader, new_height = process_image(image_path)
            c.drawImage(img_reader, 0, height - new_height, width, new_height)
            c.showPage()
            processed_pages += 1
            print(f"Processed: Chapter {chapter_num}, Page {page} ({processed_pages}/{total_pages})")
        except Exception as e:
            print(f"Failed to process Chapter {chapter_num}, Page {page}: {e}")

    c.save()
    end_time = time.time()
    print(f"Saved {pdf_filename}")
    print(f"Total PDF creation time: {end_time - start_time:.2f} seconds")
    print(f"Successfully processed {processed_pages}/{total_pages} pages")

def delete_downloaded_images_folder():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    download_folder = os.path.join(desktop_path, "Manga Scraping", "Downloaded Images")
    
    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)

    else:
        print("No Downloaded Images folder found")

def main():
    manga_title = input("Enter the title of the manga as it's described on the website: ")
    manga_data_path = get_manga_data_path(manga_title)

    if os.path.exists(manga_data_path):
        print(f"Found existing data for {manga_title}")
        with open(manga_data_path, 'r') as file:
            manga_data = json.load(file)
    else:
        print(f"No existing data found for {manga_title}. Starting scraping process.")
        manga_url = input("Enter the URL of the manga: ")
        chapters = scrape_manga_data(manga_title, manga_url)
        manga_data = collect_image_links(chapters)
        manga_data["manga-title"] = manga_title
        with open(manga_data_path, 'w') as f:
            json.dump(manga_data, f, indent=4)
        print(f"Saved manga data to {manga_data_path}")

    download_start = int(input("Download chapters starting from number: "))
    download_end = int(input("To number: "))

    downloaded_images = download_images(manga_data, manga_title, download_start, download_end)
    create_pdf_from_images(downloaded_images, manga_title, download_start, download_end)
    
    # Delete the entire Downloaded Images folder
    delete_downloaded_images_folder()    

if __name__ == "__main__":
    main()