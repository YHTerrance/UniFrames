"use client"

interface StepNavigationProps {
  currentStep: number;
  totalSteps: number;
  onStepClick?: (stepIndex: number) => void;
}

const stepNames = [
  "Upload Photo",
  "Crop Photo",
  "Select University",
  "Choose Frame",
  "Preview & Download",
];

export function StepNavigation({
  currentStep,
  totalSteps,
  onStepClick,
}: StepNavigationProps) {
  const handleStepClick = (stepIndex: number) => {
    if (onStepClick && stepIndex <= currentStep) {
      onStepClick(stepIndex);
    }
  };

  return (
    <div className="bg-card border-b border-border p-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress indicator */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            {Array.from({ length: totalSteps }, (_, i) => {
              const isClickable = i <= currentStep && onStepClick;
              const isCompleted = i < currentStep;
              const isCurrent = i === currentStep;

              return (
                <div key={i} className="flex items-center">
                  <div
                    className={`
                      w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors
                      ${
                        isCompleted
                          ? "bg-accent text-accent-foreground"
                          : isCurrent
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted text-muted-foreground"
                      }
                      ${
                        isClickable
                          ? "cursor-pointer hover:opacity-80 active:scale-95"
                          : ""
                      }
                    `}
                    onClick={() => handleStepClick(i)}
                    role={isClickable ? "button" : undefined}
                    tabIndex={isClickable ? 0 : -1}
                    onKeyDown={(e) => {
                      if (isClickable && (e.key === "Enter" || e.key === " ")) {
                        e.preventDefault();
                        handleStepClick(i);
                      }
                    }}
                    aria-label={`${isClickable ? "Go to " : ""}Step ${i + 1}: ${stepNames[i]}`}
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
              );
            })}
          </div>

          <div className="text-sm text-muted-foreground">
            Step {currentStep + 1} of {totalSteps}
          </div>
        </div>

        {/* Step name */}
        <h1 className="text-lg font-semibold text-foreground mb-4">
          {stepNames[currentStep]}
        </h1>
      </div>
    </div>
  );
}
