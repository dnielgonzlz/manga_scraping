# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import manga_scraper  # Import your existing manga_scraper.py as a module
import os
import json

app = FastAPI()

class MangaTitle(BaseModel):
    title: str

class MangaURL(BaseModel):
    title: str
    url: str

class ChapterRange(BaseModel):
    title: str
    start: int
    end: int

@app.post("/check_local_data")
async def check_local_data(manga: MangaTitle):
    data_path = manga_scraper.get_manga_data_path(manga.title)
    exists = os.path.exists(data_path)
    return {"exists": exists}

@app.post("/scrape_manga")
async def scrape_manga(manga: MangaURL):
    try:
        chapters = manga_scraper.scrape_manga_data(manga.title, manga.url)
        manga_data = manga_scraper.collect_image_links(chapters)
        manga_data["manga-title"] = manga.title
        data_path = manga_scraper.get_manga_data_path(manga.title)
        with open(data_path, 'w') as f:
            json.dump(manga_data, f, indent=4)
        return {"success": True, "message": "Manga data scraped and saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_pdf")
async def generate_pdf(range: ChapterRange):
    try:
        data_path = manga_scraper.get_manga_data_path(range.title)
        with open(data_path, 'r') as file:
            manga_data = json.load(file)
        downloaded_images = manga_scraper.download_images(manga_data, range.title, range.start, range.end)
        manga_scraper.create_pdf_from_images(downloaded_images, range.title, range.start, range.end)
        manga_scraper.delete_downloaded_images_folder()
        return {"success": True, "message": "PDF generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)