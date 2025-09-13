"use client"

import { useState, useCallback, useRef } from "react";
import Cropper from "react-easy-crop";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { RotateCcw, ZoomIn } from "lucide-react";

interface PhotoCropProps {
  imageUrl: string;
  onCropComplete: (croppedImage: string) => void;
}

interface CropArea {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function PhotoCrop({ imageUrl, onCropComplete }: PhotoCropProps) {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [lastProcessedCrop, setLastProcessedCrop] = useState<CropArea | null>(null);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const areCropAreasEqual = useCallback((a: CropArea, b: CropArea) => {
    return a.x === b.x && a.y === b.y && a.width === b.width && a.height === b.height;
  }, []);

  const createCroppedImage = useCallback(
    async (cropAreaPixels: CropArea) => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
      const image = new Image();

      image.crossOrigin = "anonymous";

      return new Promise<void>((resolve) => {
        image.onload = () => {
          canvas.width = cropAreaPixels.width;
          canvas.height = cropAreaPixels.height;

          ctx?.drawImage(
            image,
            cropAreaPixels.x,
            cropAreaPixels.y,
            cropAreaPixels.width,
            cropAreaPixels.height,
            0,
            0,
            cropAreaPixels.width,
            cropAreaPixels.height
          );

          const croppedImageUrl = canvas.toDataURL("image/jpeg", 0.9);
          onCropComplete(croppedImageUrl);
          resolve();
        };

        image.src = imageUrl;
      });
    },
    [imageUrl, onCropComplete]
  );

  const onCropCompleteCallback = useCallback(
    (croppedArea: any, croppedAreaPixels: CropArea) => {
      // Skip if crop area hasn't changed
      if (lastProcessedCrop && areCropAreasEqual(lastProcessedCrop, croppedAreaPixels)) {
        return;
      }

      // Clear existing timeout
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }

      // Set new timeout for debounced auto-crop
      debounceRef.current = setTimeout(() => {
        createCroppedImage(croppedAreaPixels);
        setLastProcessedCrop(croppedAreaPixels);
      }, 300);
    },
    [createCroppedImage, lastProcessedCrop, areCropAreasEqual, setLastProcessedCrop]
  );
  return (
    <Card className="p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Crop Your Photo
        </h2>
        <p className="text-muted-foreground">
          Adjust your photo to fit perfectly in the square frame
        </p>
      </div>

      <div className="relative h-96 bg-muted rounded-lg mb-6">
        <Cropper
          image={imageUrl}
          crop={crop}
          zoom={zoom}
          aspect={1}
          onCropChange={setCrop}
          onZoomChange={setZoom}
          onCropComplete={onCropCompleteCallback}
          cropShape="rect"
          showGrid={true}
        />
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <ZoomIn className="h-4 w-4 text-muted-foreground" />
          <Slider
            value={[zoom]}
            onValueChange={(value) => setZoom(value[0])}
            min={1}
            max={3}
            step={0.1}
            className="flex-1"
          />
        </div>

        <div className="flex justify-center">
          <Button
            variant="outline"
            onClick={() => {
              setCrop({ x: 0, y: 0 });
              setZoom(1);
            }}
            className="flex items-center gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            Reset
          </Button>
        </div>
      </div>
    </Card>
  );
}
