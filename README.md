# Manga Scraping Tool


Distribute your weekly calories by using a slider to increase or decrease the calories from a day, and it will automatically adjust the other days of the week.
Features

## Requirements
LLM Token API (I tested all the prompts using GPT 4o-mini)

## Features 

Creates a database of the manga chapters and the pages in a JSON file.

It compiles ranges of chapters into a single PDF to make it easier to send to a Kindle.

It compresses the PDF to reduce PDF size *(to be implemented soon)*

You only need to do the big scraping once, after you have the JSON file locally the program will check that and only ask for the range of chapters


## Usage

Enter the link of the website you want to scrape

Give it time to scrape the chapters and create the JSON file (this can take quite some time so leave the window open and go do something else. This will only happen once, since after this the chapters are created by using the JSON database).

Input the range of chapters you want to join into a single PDF (eg. Chapter 5 to 45).

The file will be created and correctly organized in your Desktop inside the Folder "Manga Scraping".

## Installation

npm i

**START THE FRONTEND**
cd frontend

npm run dev

**START THE BACKEND IN ANOTHER TERMINAL**
cd backend

uvicorn main:app --reload

## Future Features

*Weekly Scraper to download weekly chapters from these websites*
*Implementation of ILovePDF API to integrate compression in the merging of the PDFs*
