"use client";

import { useState } from "react";
import { PhotoUpload } from "@/components/photo-upload";
import { PhotoCrop } from "@/components/photo-crop";
import { UniversitySelector } from "@/components/university-selector";
import { FrameGallery } from "@/components/frame-gallery";
import { CanvasPreview } from "@/components/canvas-preview";
import { StepNavigation } from "@/components/step-navigation";
import type { PhotoState } from "@/lib/types";

export default function Home() {
  const [currentStep, setCurrentStep] = useState(0);
  const [photoState, setPhotoState] = useState<PhotoState>({
    originalFile: null,
    croppedImage: null,
    selectedUniversity: null,
    selectedFrame: null,
    finalImage: null,
  });

  const totalSteps = 5;

  const handlePhotoSelect = (file: File) => {
    const url = URL.createObjectURL(file);
    setPhotoState((prev) => ({
      ...prev,
      originalFile: file,
      croppedImage: null, // Reset crop when new photo is selected
    }));
  };

  const handleCropComplete = (croppedImage: string) => {
    setPhotoState((prev) => ({
      ...prev,
      croppedImage,
    }));
  };

  const handleUniversitySelect = (university: any) => {
    setPhotoState((prev) => ({
      ...prev,
      selectedUniversity: university,
      selectedFrame: null, // Reset frame when university changes
    }));
  };

  const handleFrameSelect = (frame: any) => {
    setPhotoState((prev) => ({
      ...prev,
      selectedFrame: frame,
    }));
  };

  const handleFinalImageReady = (imageUrl: string) => {
    setPhotoState((prev) => ({
      ...prev,
      finalImage: imageUrl,
    }));
  };

  const canProceedToNextStep = () => {
    switch (currentStep) {
      case 0:
        return photoState.originalFile !== null;
      case 1:
        return photoState.croppedImage !== null;
      case 2:
        return photoState.selectedUniversity !== null;
      case 3:
        return photoState.selectedFrame !== null;
      case 4:
        return photoState.finalImage !== null;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (canProceedToNextStep() && currentStep < totalSteps - 1) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <PhotoUpload
            onPhotoSelect={handlePhotoSelect}
            selectedPhoto={photoState.originalFile}
          />
        );
      case 1:
        return photoState.originalFile ? (
          <PhotoCrop
            imageUrl={URL.createObjectURL(photoState.originalFile)}
            onCropComplete={handleCropComplete}
          />
        ) : null;
      case 2:
        return (
          <UniversitySelector
            onUniversitySelect={handleUniversitySelect}
            selectedUniversity={photoState.selectedUniversity}
          />
        );
      case 3:
        return photoState.selectedUniversity ? (
          <FrameGallery
            university={photoState.selectedUniversity}
            onFrameSelect={handleFrameSelect}
            selectedFrame={photoState.selectedFrame}
          />
        ) : null;
      case 4:
        return photoState.croppedImage &&
          photoState.selectedUniversity &&
          photoState.selectedFrame ? (
          <CanvasPreview
            croppedImage={photoState.croppedImage}
            university={photoState.selectedUniversity}
            frame={photoState.selectedFrame}
            onFinalImageReady={handleFinalImageReady}
          />
        ) : null;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <StepNavigation
        currentStep={currentStep}
        totalSteps={totalSteps}
        onPrevious={handlePrevious}
        onNext={handleNext}
        canProceed={canProceedToNextStep()}
      />

      <main className="max-w-4xl mx-auto p-6">
        <div className="text-center my-12">
          <h1 className="text-4xl font-bold text-foreground mb-8">
            Uni Frames
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Create your profile photo with your university's branding. Upload
            your photo, select your university, and choose from our collection
            of frames.
          </p>
        </div>

        {renderCurrentStep()}
      </main>
    </div>
  );
}
