"use client"

import { useEffect, useRef, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Download, RefreshCw } from "lucide-react"
import type { University, Frame } from "@/lib/types"

interface CanvasPreviewProps {
  croppedImage: string
  university: University
  frame: Frame
  onFinalImageReady: (imageUrl: string) => void
}

export function CanvasPreview({ croppedImage, university, frame, onFinalImageReady }: CanvasPreviewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string>("")

  const generateFramedImage = async () => {
    if (!canvasRef.current) return

    setIsGenerating(true)
    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")

    if (!ctx) return

    // Set canvas size
    canvas.width = 400
    canvas.height = 400

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    try {
      // Load and draw the cropped image
      const img = new Image()
      img.crossOrigin = "anonymous"

      await new Promise<void>((resolve, reject) => {
        img.onload = () => {
          // Draw the photo
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
          resolve()
        }

        img.onerror = reject
        img.src = croppedImage
      })

      // Generate final image URL
      const finalImageUrl = canvas.toDataURL("image/png", 1.0)
      setPreviewUrl(finalImageUrl)
      onFinalImageReady(finalImageUrl)
    } catch (error) {
      console.error("Error generating framed image:", error)
    } finally {
      setIsGenerating(false)
    }
  }

  useEffect(() => {
    generateFramedImage()
  }, [croppedImage, university, frame])

  const downloadImage = () => {
    if (!previewUrl) return

    const link = document.createElement("a")
    link.download = `${university.name.replace(/\s+/g, "_")}_profile_photo.png`
    link.href = previewUrl
    link.click()
  }

  return (
    <Card className="p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">Preview & Download</h2>
        <p className="text-muted-foreground">Your {university.name} profile photo is ready!</p>
      </div>

      <div className="flex flex-col items-center space-y-6">
        <div className="relative">
          <canvas
            ref={canvasRef}
            className="max-w-full h-auto border border-border rounded-lg shadow-lg"
            style={{ maxWidth: "300px" }}
          />
          {isGenerating && (
            <div className="absolute inset-0 bg-background/80 flex items-center justify-center rounded-lg">
              <RefreshCw className="h-6 w-6 animate-spin text-accent" />
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={generateFramedImage}
            disabled={isGenerating}
            className="flex items-center gap-2 bg-transparent"
          >
            <RefreshCw className={`h-4 w-4 ${isGenerating ? "animate-spin" : ""}`} />
            Regenerate
          </Button>

          <Button onClick={downloadImage} disabled={!previewUrl || isGenerating} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Download Image
          </Button>
        </div>
      </div>
    </Card>
  )
}
