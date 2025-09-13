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
    if (!canvasRef.current) return;

    setIsGenerating(true);
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    if (!ctx) return;

    // Set high-resolution canvas size (3x higher than display)
    const pixelRatio = window.devicePixelRatio || 1;
    const baseSize = 400;
    const highResSize = baseSize * 3; // 1200x1200 for much higher quality

    canvas.width = highResSize * pixelRatio;
    canvas.height = highResSize * pixelRatio;

    // Scale context for high-DPI displays
    ctx.scale(pixelRatio, pixelRatio);

    // Clear canvas
    ctx.clearRect(0, 0, highResSize, highResSize);

    try {
      // Load both the cropped image and frame image concurrently
      const [croppedImg, frameImg] = await Promise.all([
        new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = "anonymous";
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = croppedImage;
        }),
        new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = "anonymous";
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = frame.url;
        })
      ]);

      // Save the current context state
      ctx.save();

      // Create circular clipping path for the photo
      const centerX = highResSize / 2;
      const centerY = highResSize / 2;
      const radius = highResSize / 2;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.clip();

      // Draw the photo at high resolution within the circular clip
      ctx.drawImage(croppedImg, 0, 0, highResSize, highResSize);

      // Restore context to remove clipping path
      ctx.restore();

      // Draw the frame image as an overlay on top
      ctx.drawImage(frameImg, 0, 0, highResSize, highResSize);

      // Generate final image URL
      const finalImageUrl = canvas.toDataURL("image/png", 1.0);
      setPreviewUrl(finalImageUrl);
      onFinalImageReady(finalImageUrl);
    } catch (error) {
      console.error("Error generating framed image:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    generateFramedImage();
  }, [croppedImage, university, frame]);

  const downloadImage = () => {
    if (!previewUrl) return;

    const link = document.createElement("a");
    link.download = `${university.name.replace(/\s+/g, "_")}_profile_photo.png`;
    link.href = previewUrl;
    link.click();
  };

  return (
    <Card className="p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Preview & Download
        </h2>
        <p className="text-muted-foreground">
          Your {university.name} profile photo is ready!
        </p>
      </div>

      <div className="flex flex-col items-center space-y-6">
        <div className="relative">
          <canvas
            ref={canvasRef}
            className="max-w-full h-auto border border-border shadow-lg"
            style={{ maxWidth: "300px", borderRadius: "50%" }}
          />
          {isGenerating && (
            <div className="absolute inset-0 bg-background/80 flex items-center justify-center rounded-lg">
              <RefreshCw className="h-6 w-6 animate-spin text-accent" />
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            onClick={downloadImage}
            disabled={!previewUrl || isGenerating}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Download Image
          </Button>
        </div>
      </div>
    </Card>
  );
}
