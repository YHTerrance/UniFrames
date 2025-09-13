"use client"

import { useCallback, useState, useEffect } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface PhotoUploadProps {
  onPhotoSelect: (file: File) => void;
  selectedPhoto: File | null;
  onNext: () => void;
  canProceed: boolean;
}

export function PhotoUpload({
  onPhotoSelect,
  selectedPhoto,
  onNext,
  canProceed,
}: PhotoUploadProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (selectedPhoto) {
      const url = URL.createObjectURL(selectedPhoto);
      setPreviewUrl(url);

      return () => {
        URL.revokeObjectURL(url);
      };
    } else {
      setPreviewUrl(null);
    }
  }, [selectedPhoto]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onPhotoSelect(acceptedFiles[0]);
      }
    },
    [onPhotoSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif", ".bmp", ".webp"],
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <Card className="p-8">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Upload Your Photo
        </h2>
        <p className="text-muted-foreground">
          Choose a high-quality photo to create your university profile frame
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`
          flex justify-center items-center h-[400px] border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors
          ${
            isDragActive
              ? "border-accent bg-accent/5"
              : "border-border hover:border-accent hover:bg-accent/5"
          }
        `}
      >
        <input {...getInputProps()} />

        {selectedPhoto ? (
          <div className="space-y-4">
            {previewUrl && (
              <img
                src={previewUrl}
                alt="Preview"
                className="mx-auto h-32 w-32 object-cover rounded-lg shadow-md"
              />
            )}
            <div>
              <p className="text-lg font-medium text-foreground">
                {selectedPhoto.name}
              </p>
              <p className="text-sm text-muted-foreground">
                {(selectedPhoto.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <Button variant="outline" size="sm">
              Choose Different Photo
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
            <div>
              <p className="text-lg font-medium text-foreground">
                {isDragActive
                  ? "Drop your photo here"
                  : "Drag & drop your photo here"}
              </p>
              <p className="text-sm text-muted-foreground">
                or click to browse files
              </p>
            </div>
            <p className="text-xs text-muted-foreground">
              Supports: JPEG, PNG, GIF, BMP, WebP (max 10MB)
            </p>
          </div>
        )}
      </div>

      <div className="flex justify-end mt-6">
        <Button
          onClick={onNext}
          disabled={!canProceed}
          className="flex items-center gap-2"
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  );
}
