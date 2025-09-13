"use client"

import { useState } from "react"
import { Search, Check, ChevronRight } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { universities } from "@/lib/universities";
import type { University } from "@/lib/types";
import Image from "next/image";

interface UniversitySelectorProps {
  onUniversitySelect: (university: University) => void;
  selectedUniversity: University | null;
  onNext: () => void;
  canProceed: boolean;
}

export function UniversitySelector({
  onUniversitySelect,
  selectedUniversity,
  onNext,
  canProceed,
}: UniversitySelectorProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredUniversities = universities.filter((university) =>
    university.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Card className="p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Select Your University
        </h2>
        <p className="text-muted-foreground">
          Choose your university to see available frame options
        </p>
      </div>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search universities..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
        {filteredUniversities.map((university) => (
          <Button
            key={university.id}
            variant={
              selectedUniversity?.id === university.id ? "default" : "outline"
            }
            onClick={() => onUniversitySelect(university)}
            className="h-auto p-4 justify-start"
          >
            <div className="flex items-center gap-3 w-full">
              <Image
                src={university.logo || "/placeholder.svg"}
                alt={`${university.name} logo`}
                width={32}
                height={32}
                className="rounded-full"
              />
              <span className="font-medium text-left flex-1">
                {university.name}
              </span>
              {selectedUniversity?.id === university.id && (
                <Check className="h-4 w-4 text-accent-foreground" />
              )}
            </div>
          </Button>
        ))}
      </div>

      {filteredUniversities.length === 0 && (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No universities found matching "{searchTerm}"
          </p>
        </div>
      )}

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
