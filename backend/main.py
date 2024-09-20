# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import manga_scraper  # Import your existing manga_scraper.py as a module
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your Next.js frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

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
def scrape_manga(manga: MangaURL):
    try:
        print(f"Attempting to scrape manga: {manga.title} from URL: {manga.url}")
        chapters = manga_scraper.scrape_manga_data(manga.title, manga.url)
        print(f"Chapters scraped: {len(chapters)}")
        manga_data = manga_scraper.collect_image_links(chapters)
        print(f"Image links collected for {len(manga_data['chapters'])} chapters")
        manga_data["manga-title"] = manga.title
        data_path = manga_scraper.get_manga_data_path(manga.title)
        with open(data_path, 'w') as f:
            json.dump(manga_data, f, indent=4)
        print(f"Manga data saved to {data_path}")
        return {"success": True, "message": "Manga data scraped and saved successfully"}
    except Exception as e:
        print(f"Error in scrape_manga: {str(e)}")
        import traceback
        print(traceback.format_exc())
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
    uvicorn.run(app, host="0.0.0.0", port=8000) #Maybe it should be 3000?