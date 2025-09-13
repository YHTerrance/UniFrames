"use client"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { getFramesByUniversity } from "@/lib/universities"
import type { University, Frame } from "@/lib/types"
import { Check } from "lucide-react"
import Image from "next/image"

interface FrameGalleryProps {
  university: University
  onFrameSelect: (frame: Frame) => void
  selectedFrame: Frame | null
}

export function FrameGallery({ university, onFrameSelect, selectedFrame }: FrameGalleryProps) {
  const frames = getFramesByUniversity(university.id)

  return (
    <Card className="p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">Choose Your Frame</h2>
        <p className="text-muted-foreground">Select a frame style for {university.name}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {frames.map((frame) => (
          <div key={frame.id} className="relative">
            <Button
              variant="ghost"
              onClick={() => onFrameSelect(frame)}
              className={`
                h-auto p-0 w-full relative overflow-hidden rounded-lg
                ${
                  selectedFrame?.id === frame.id
                    ? "ring-2 ring-accent ring-offset-2"
                    : "hover:ring-2 hover:ring-accent/50 hover:ring-offset-2"
                }
              `}
            >
              <div className="aspect-square w-full relative">
                <Image
                  src={frame.url || "/placeholder.svg"}
                  alt={`${frame.name} preview`}
                  fill
                  className="object-cover"
                />
                {selectedFrame?.id === frame.id && (
                  <div className="absolute inset-0 bg-accent/20 flex items-center justify-center">
                    <div className="bg-accent text-accent-foreground rounded-full p-2">
                      <Check className="h-4 w-4" />
                    </div>
                  </div>
                )}
              </div>
            </Button>
            <p className="text-sm font-medium text-center mt-2 text-foreground">{frame.name}</p>
          </div>
        ))}
      </div>

      {frames.length === 0 && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">No frames available for {university.name} yet.</p>
        </div>
      )}
    </Card>
  )
}
