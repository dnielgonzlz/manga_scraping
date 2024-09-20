# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import manga_scraper  # Import your existing manga_scraper.py as a module
import os
import json
import asyncio

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

progress = 0
scraped_chapters = 0
total_chapters = 0

@app.post("/check_local_data")
async def check_local_data(manga: MangaTitle):
    data_path = manga_scraper.get_manga_data_path(manga.title)
    exists = os.path.exists(data_path)
    return {"exists": exists}

@app.post("/scrape_manga")
def scrape_manga(manga: MangaURL):
    global progress, scraped_chapters, total_chapters
    try:
        print(f"Attempting to scrape manga: {manga.title} from URL: {manga.url}")
        chapters = manga_scraper.scrape_manga_data(manga.title, manga.url)
        total_chapters = len(chapters)
        print(f"Chapters found: {total_chapters}")

        manga_data = {"chapters": []}
        for i, chapter in enumerate(chapters):
            chapter_data = manga_scraper.collect_image_links([chapter])
            manga_data["chapters"].extend(chapter_data["chapters"])
            scraped_chapters = i + 1
            progress = (scraped_chapters / total_chapters) * 100
            print(f"Scraped chapter {scraped_chapters}/{total_chapters}")

        manga_data["manga-title"] = manga.title
        data_path = manga_scraper.get_manga_data_path(manga.title)
        with open(data_path, 'w') as f:
            json.dump(manga_data, f, indent=4)
        print(f"Manga data saved to {data_path}")
        return {"success": True, "message": "Manga data scraped and saved successfully", "total_chapters": total_chapters}
    except Exception as e:
        print(f"Error in scrape_manga: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/scrape-progress")
async def scrape_progress(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            yield f"data: {json.dumps({'progress': progress, 'scraped_chapters': scraped_chapters, 'total_chapters': total_chapters})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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