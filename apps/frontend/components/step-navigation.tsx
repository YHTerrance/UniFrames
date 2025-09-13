"use client"

interface StepNavigationProps {
  currentStep: number;
  stepNames: string[];
  onStepClick?: (stepIndex: number) => void;
}

export function StepNavigation({
  currentStep,
  stepNames,
  onStepClick,
}: StepNavigationProps) {
  const handleStepClick = (stepIndex: number) => {
    if (onStepClick && stepIndex <= currentStep) {
      onStepClick(stepIndex);
    }
  };

  const totalSteps = stepNames.length;

  return (
    <div className="bg-card border-b border-border p-4">
      <div className="max-w-4xl mx-auto">
        {/* Progress indicator */}
        <div className="flex items-center justify-center">
          <div className="flex items-center space-x-2">
            {Array.from({ length: totalSteps }, (_, i) => {
              const isClickable = i <= currentStep && onStepClick;
              const isCompleted = i < currentStep;
              const isCurrent = i === currentStep;

              return (
                <div key={i} className="flex items-center">
                  <div className="flex flex-col items-center">
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
                        if (
                          isClickable &&
                          (e.key === "Enter" || e.key === " ")
                        ) {
                          e.preventDefault();
                          handleStepClick(i);
                        }
                      }}
                      aria-label={`${isClickable ? "Go to " : ""}Step ${
                        i + 1
                      }: ${stepNames[i]}`}
                    >
                      {i + 1}
                    </div>
                    <div
                      className={`
                        mt-2 text-xs text-center max-w-16 leading-tight
                        ${
                          isCurrent
                            ? "text-primary font-semibold"
                            : isCompleted
                            ? "text-accent-foreground font-medium"
                            : "text-muted-foreground"
                        }
                      `}
                    >
                      {stepNames[i]}
                    </div>
                  </div>
                  {i < totalSteps - 1 && (
                    <div
                      className={`
                        w-12 h-0.5 mx-2 mt-[-16px]
                        ${i < currentStep ? "bg-accent" : "bg-muted"}
                      `}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
