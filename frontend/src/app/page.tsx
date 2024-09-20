'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import axios from 'axios'

export default function MangaExtractor() {
  const [title, setTitle] = useState('')
  const [websiteUrl, setWebsiteUrl] = useState('')
  const [startChapter, setStartChapter] = useState('')
  const [endChapter, setEndChapter] = useState('')
  const [status, setStatus] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showRangeInput, setShowRangeInput] = useState(false)

  //TODO: This has to do the local check to see if we have data from the manga based on the title inputed. It uses the
  // manga_title variable to be inputted in the get_manga_data_path function, to do this check locally in the computer.
  const checkLocalData = async (mangaTitle: string) => {
    setIsLoading(true)
    try {
      const response = await axios.post('http://localhost:8000/check_local_data', { title: mangaTitle })
      setIsLoading(false)
      return response.data.exists
    } catch (error) {
      console.error('Error checking local data:', error)
      setIsLoading(false)
      return false
    }
  }

  //TODO: if there is no data found on the local computer, this function will be called to scrape the website for the
  // manga title inputed. It will use the websiteUrl variable to scrape the website for the manga chapters and the
  // LLM API will grab the links of all the chapters of the manga.
  // It is using the function called scrape_manga_data.
  // This should be being passed to the Python script in the variable of manga_url.
  const scrapeWebsite = async (websiteUrl: string) => {
    setIsLoading(true)
    setStatus('Scraping website for chapters...')
    try {
      const response = await axios.post('http://localhost:8000/scrape_manga', { title, url: websiteUrl })
      setIsLoading(false)
      setStatus(`Website scraped successfully! Found ${response.data.chapters.length} chapters.`)
      setShowRangeInput(true)
    } catch (error) {
      console.error('Error scraping website:', error)
      setIsLoading(false)
      setStatus('Error occurred while scraping the website.')
    }
  }

  //TODO: this should be passed to the python script on the manga_title variable.
  // After collecting this, it should run the get_manga_data_path to check the local deskptop
  // See if there's some local json file with the matching name, and depending on that it will ask the user to
  // enter the url first to scrape the website or to enter the chapter range.
  const handleTitleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title) {
      setStatus('Please enter a manga title.')
      return
    }
    const hasLocalData = await checkLocalData(title)
    if (hasLocalData) {
      setStatus('Local data found. Please enter chapter range.')
      setShowRangeInput(true)
    } else {
      setStatus('No local data found. Please enter website URL.')
      setShowRangeInput(false)
    }
  }


  //TODO: this should be passed to the python script on the manga_url variable.
  // After collecting this, it should run the scrape_manga_data to run the first scraping function and collect all the chapters.
  // After this, the script should convert the chapters into a dictionary, and then run another scraping of each chapter link.
  // After this, all the images for each chapter will be collected in a JSON with the structure of the chapter number and the page number,
  // indicating what page number is each, in ascending number.
  // enter the url first to scrape the website or to enter the chapter range.
  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!websiteUrl) {
      setStatus('Please enter a website URL.')
      return
    }
    await scrapeWebsite(websiteUrl) 
    //TODO: ERROR!
  }

  //TODO: After storing the database of all the links, you will have stored locally the file of all the links.
  // Now, the user needs to input the range of chapters that he wants to download.
  // This will be passed to the python script on the download_start and download_end variables.
  // After this, the script will run the download_images function and the create_pdf_from_images function.
  // Lastly, it will delete the images from the computer after the PDF is created.
  const handleRangeSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!startChapter || !endChapter) {
      setStatus('Please enter both start and end chapters.')
      return
    }
    setIsLoading(true)
    setStatus('Extracting PDF...')
    try {
      const response = await axios.post('http://localhost:8000/generate_pdf', {
        title,
        start: parseInt(startChapter),
        end: parseInt(endChapter)
      })
      setIsLoading(false)
      setStatus(`PDF extracted successfully! Saved to: ${response.data.pdf_path}`)
    } catch (error) {
      console.error('Error creating PDF:', error)
      setIsLoading(false)
      setStatus('Error occurred while creating the PDF.')
    }
  }


  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-black p-4">
      <Card className="w-full max-w-md bg-gray-800 border-gray-700 shadow-lg">
        <CardHeader className="border-b border-gray-700">
          <CardTitle className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
            Manga PDF Extractor
          </CardTitle>
        </CardHeader>
        <CardContent className="mt-4">
          <form onSubmit={handleTitleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="title" className="text-gray-300">Manga Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter manga title"
                className="bg-gray-700 text-white border-gray-600 focus:border-purple-500 focus:ring-purple-500"
              />
            </div>
            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
            >
              {isLoading ? 'Checking...' : 'Check Title'}
            </Button>
          </form>

          {!showRangeInput && status.includes('Please enter website URL') && (
            <form onSubmit={handleUrlSubmit} className="mt-4 space-y-4">
              <div>
                <Label htmlFor="url" className="text-gray-300">Website URL</Label>
                <Input
                  id="url"
                  value={websiteUrl}
                  onChange={(e) => setWebsiteUrl(e.target.value)}
                  placeholder="Enter website URL"
                  className="bg-gray-700 text-white border-gray-600 focus:border-purple-500 focus:ring-purple-500"
                />
              </div>
              <Button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
              >
                {isLoading ? 'Scraping...' : 'Scrape Website'}
              </Button>
            </form>
          )}

          {showRangeInput && (
            <form onSubmit={handleRangeSubmit} className="mt-4 space-y-4">
              <div>
                <Label htmlFor="startChapter" className="text-gray-300">Start Chapter</Label>
                <Input
                  id="startChapter"
                  value={startChapter}
                  onChange={(e) => setStartChapter(e.target.value)}
                  placeholder="Enter start chapter"
                  type="number"
                  className="bg-gray-700 text-white border-gray-600 focus:border-purple-500 focus:ring-purple-500"
                />
              </div>
              <div>
                <Label htmlFor="endChapter" className="text-gray-300">End Chapter</Label>
                <Input
                  id="endChapter"
                  value={endChapter}
                  onChange={(e) => setEndChapter(e.target.value)}
                  placeholder="Enter end chapter"
                  type="number"
                  className="bg-gray-700 text-white border-gray-600 focus:border-purple-500 focus:ring-purple-500"
                />
              </div>
              <Button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white"
              >
                {isLoading ? 'Extracting...' : 'Extract PDF'}
              </Button>
            </form>
          )}

          {status && (
            <div className={`mt-4 p-3 rounded ${status.includes('successfully') ? 'bg-green-900' : 'bg-yellow-900'} text-white`}>
              {status.includes('successfully') ? (
                <CheckCircle2 className="inline mr-2 text-green-400" />
              ) : (
                <AlertCircle className="inline mr-2 text-yellow-400" />
              )}
              {status}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}