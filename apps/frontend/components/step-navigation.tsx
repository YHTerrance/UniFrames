"use client"

import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface StepNavigationProps {
  currentStep: number
  totalSteps: number
  onPrevious: () => void
  onNext: () => void
  canProceed: boolean
}

const stepNames = ["Upload Photo", "Crop Photo", "Select University", "Choose Frame", "Preview & Download"]

export function StepNavigation({ currentStep, totalSteps, onPrevious, onNext, canProceed }: StepNavigationProps) {
  return (
    <div className="bg-card border-b border-border p-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress indicator */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            {Array.from({ length: totalSteps }, (_, i) => (
              <div key={i} className="flex items-center">
                <div
                  className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${
                      i < currentStep
                        ? "bg-accent text-accent-foreground"
                        : i === currentStep
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                    }
                  `}
                >
                  {i + 1}
                </div>
                {i < totalSteps - 1 && (
                  <div
                    className={`
                      w-12 h-0.5 mx-2
                      ${i < currentStep ? "bg-accent" : "bg-muted"}
                    `}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="text-sm text-muted-foreground">
            Step {currentStep + 1} of {totalSteps}
          </div>
        </div>

        {/* Step name */}
        <h1 className="text-lg font-semibold text-foreground mb-4">{stepNames[currentStep]}</h1>

        {/* Navigation buttons */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={onPrevious}
            disabled={currentStep === 0}
            className="flex items-center gap-2 bg-transparent"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>

          <Button
            onClick={onNext}
            disabled={!canProceed || currentStep === totalSteps - 1}
            className="flex items-center gap-2"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
