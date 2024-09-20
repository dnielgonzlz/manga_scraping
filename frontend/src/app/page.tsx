'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import axios from 'axios'
import { Progress } from '@radix-ui/react-progress'

export default function MangaExtractor() {
  const [title, setTitle] = useState('')
  const [websiteUrl, setWebsiteUrl] = useState('')
  const [startChapter, setStartChapter] = useState('')
  const [endChapter, setEndChapter] = useState('')
  const [status, setStatus] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showRangeInput, setShowRangeInput] = useState(false)
  const [progress, setProgress] = useState(0)
  const [totalChapters, setTotalChapters] = useState(0)
  const [scrapedChapters, setScrapedChapters] = useState(0)

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8000/scrape-progress')
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setProgress(data.progress)
      setScrapedChapters(data.scraped_chapters)
      setTotalChapters(data.total_chapters)
    }
    return () => eventSource.close()
  }, [])


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

  const scrapeWebsite = async (websiteUrl: string) => {
    setIsLoading(true)
    setStatus('Scraping website for chapters...')
    try {
      const response = await axios.post('http://localhost:8000/scrape_manga', { title, url: websiteUrl })
      setIsLoading(false)
      setTotalChapters(response.data.total_chapters)
      setStatus(`Website scraped successfully! Found ${response.data.total_chapters} chapters. Starting detailed scraping...`)
      setShowRangeInput(true)
    } catch (error) {
      console.error('Error scraping website:', error)
      setIsLoading(false)
      setStatus('Error occurred while scraping the website.')
    }
  }

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

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!websiteUrl) {
      setStatus('Please enter a website URL.')
      return
    }
    await scrapeWebsite(websiteUrl) 
  }

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
      setStatus(`PDF extracted successfully! ${response.data.message}
      
      We recommend installing Calibre https://calibre-ebook.com/ for e-book management.
      To reduce file size for smooth Kindle transfer, consider using a PDF compression tool like https://www.ilovepdf.com/compress_pdf.`)
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

          {totalChapters > 0 && (
            <div className="mt-4">
              <p className="text-white mb-2">Scraping Progress: {scrapedChapters}/{totalChapters} chapters</p>
              <Progress value={(scrapedChapters / totalChapters) * 100} className="w-full" />
              <p className="text-gray-400 mt-2 text-sm">This process may take an hour or more depending on the number of chapters. Please keep this window open.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )

}