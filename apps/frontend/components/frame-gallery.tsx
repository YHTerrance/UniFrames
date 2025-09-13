"use client"

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getFramesByUniversity } from "@/lib/universities";
import { Check } from "lucide-react";
import Image from "next/image";

interface FrameGalleryProps {
  university: string;
  onFrameSelect: (frame: string) => void;
  selectedFrame: string | null;
  onNext: () => void;
  onPrev: () => void;
  canProceed: boolean;
}

export function FrameGallery({
  university,
  onFrameSelect,
  selectedFrame,
  onNext,
  onPrev,
  canProceed,
}: FrameGalleryProps) {
  const [frames, setFrames] = useState<string[]>([]);

  useEffect(() => {
    const fetchFrames = async () => {
      const frames = await getFramesByUniversity(university);
      setFrames(frames);
    };
    fetchFrames();
  }, [university]);

  return (
    <Card className="p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Choose Your Frame
        </h2>
        <p className="text-muted-foreground">
          Select a frame style for {university}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {frames.map((frame) => (
          <div key={frame} className="relative">
            <Button
              variant="ghost"
              onClick={() => onFrameSelect(frame)}
              className={`
                h-auto p-0 w-full relative overflow-hidden rounded-lg
                ${
                  selectedFrame === frame
                    ? "ring-2 ring-accent ring-offset-2"
                    : "hover:ring-2 hover:ring-accent/50 hover:ring-offset-2"
                }
              `}
            >
              <div className="aspect-square w-full relative">
                <Image
                  src={frame || "/placeholder.svg"}
                  alt={`${frame} preview`}
                  fill
                  className="object-cover"
                />
                {selectedFrame === frame && (
                  <div className="absolute inset-0 bg-accent/20 flex items-center justify-center">
                    <div className="bg-accent text-accent-foreground rounded-full p-2">
                      <Check className="h-4 w-4" />
                    </div>
                  </div>
                )}
              </div>
            </Button>
          </div>
        ))}
      </div>

      {frames.length === 0 && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No frames available for {university} yet.
          </p>
        </div>
      )}

      <div className="space-y-4">
        <div className="flex justify-between space-x-8">
          <Button
            variant="outline"
            onClick={onPrev}
            className="flex items-center gap-2 grow"
          >
            Previous
          </Button>
          <Button
            onClick={onNext}
            disabled={!canProceed}
            className="flex items-center gap-2 grow"
          >
            Next
          </Button>
        </div>
      </div>
    </Card>
  );
}
