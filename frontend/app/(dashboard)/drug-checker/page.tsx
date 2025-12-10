"use client";

import React, { useState } from "react";
import {
  Pill,
  Plus,
  X,
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  Ban,
  Search,
  Loader2,
  Info,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn, getSeverityColor } from "@/lib/utils";
import { api, type DrugCheckResponse, type DrugInteraction, type Drug } from "@/lib/api";
import { Header } from "@/components/layout/Header";

const severityIcons = {
  none: CheckCircle,
  mild: Info,
  moderate: AlertCircle,
  severe: AlertTriangle,
  contraindicated: Ban,
};

const severityLabels = {
  none: "No Interaction",
  mild: "Mild",
  moderate: "Moderate",
  severe: "Severe",
  contraindicated: "Contraindicated",
};

export default function DrugCheckerPage() {
  const [drugs, setDrugs] = useState<string[]>([""]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Drug[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [result, setResult] = useState<DrugCheckResponse | null>(null);
  const [activeInput, setActiveInput] = useState<number | null>(null);

  const handleAddDrug = () => {
    if (drugs.length < 10) {
      setDrugs([...drugs, ""]);
    }
  };

  const handleRemoveDrug = (index: number) => {
    if (drugs.length > 1) {
      setDrugs(drugs.filter((_, i) => i !== index));
    }
  };

  const handleDrugChange = async (index: number, value: string) => {
    const newDrugs = [...drugs];
    newDrugs[index] = value;
    setDrugs(newDrugs);
    setActiveInput(index);

    // Search for drugs
    if (value.length >= 2) {
      setIsSearching(true);
      try {
        const response = await api.searchDrugs(value, 5);
        setSearchResults(response.drugs);
      } catch (error) {
        console.error("Drug search error:", error);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    } else {
      setSearchResults([]);
    }
  };

  const handleSelectDrug = (index: number, drug: Drug) => {
    const newDrugs = [...drugs];
    newDrugs[index] = drug.name;
    setDrugs(newDrugs);
    setSearchResults([]);
    setActiveInput(null);
  };

  const handleCheckInteractions = async () => {
    const validDrugs = drugs.filter((d) => d.trim().length > 0);
    if (validDrugs.length < 2) return;

    setIsChecking(true);
    setResult(null);

    try {
      const response = await api.checkDrugInteractions(validDrugs);
      setResult(response);
    } catch (error) {
      console.error("Interaction check error:", error);
    } finally {
      setIsChecking(false);
    }
  };

  const validDrugCount = drugs.filter((d) => d.trim().length > 0).length;

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Drug Interaction Checker"
        subtitle="Check for potential interactions between medications"
      />

      <div className="flex-1 overflow-auto">
        <div className="max-w-6xl mx-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Section */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Pill className="w-5 h-5" />
                    Enter Medications
                  </CardTitle>
                  <CardDescription>
                    Add 2-10 medications to check for interactions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {drugs.map((drug, index) => (
                    <div key={index} className="relative">
                      <div className="flex gap-2">
                        <div className="relative flex-1">
                          <Input
                            value={drug}
                            onChange={(e) =>
                              handleDrugChange(index, e.target.value)
                            }
                            onFocus={() => setActiveInput(index)}
                            onBlur={() => {
                              // Delay to allow click on search results
                              setTimeout(() => setActiveInput(null), 200);
                            }}
                            placeholder={`Medication ${index + 1}`}
                            className="pr-8"
                          />
                          {isSearching && activeInput === index && (
                            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin text-muted-foreground" />
                          )}
                        </div>
                        {drugs.length > 1 && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleRemoveDrug(index)}
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        )}
                      </div>

                      {/* Search results dropdown */}
                      {activeInput === index &&
                        searchResults.length > 0 && (
                          <Card className="absolute z-10 w-full mt-1 shadow-lg">
                            <ScrollArea className="max-h-48">
                              {searchResults.map((result) => (
                                <button
                                  key={result.name}
                                  className="w-full px-4 py-2 text-left hover:bg-muted transition-colors"
                                  onClick={() => handleSelectDrug(index, result)}
                                >
                                  <div className="font-medium">{result.name}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {result.drug_class}
                                    {result.brand_names.length > 0 &&
                                      ` • ${result.brand_names.join(", ")}`}
                                  </div>
                                </button>
                              ))}
                            </ScrollArea>
                          </Card>
                        )}
                    </div>
                  ))}

                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      onClick={handleAddDrug}
                      disabled={drugs.length >= 10}
                      className="flex-1"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Medication
                    </Button>
                    <Button
                      onClick={handleCheckInteractions}
                      disabled={validDrugCount < 2 || isChecking}
                      className="flex-1"
                    >
                      {isChecking ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Search className="w-4 h-4 mr-2" />
                      )}
                      Check Interactions
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Legend */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Severity Legend</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-2">
                  {Object.entries(severityLabels).map(([key, label]) => {
                    const Icon = severityIcons[key as keyof typeof severityIcons];
                    return (
                      <div
                        key={key}
                        className="flex items-center gap-2 text-sm"
                      >
                        <Badge
                          variant={key as "mild" | "moderate" | "severe" | "contraindicated" | "default"}
                          className="gap-1"
                        >
                          <Icon className="w-3 h-3" />
                          {label}
                        </Badge>
                      </div>
                    );
                  })}
                </CardContent>
              </Card>
            </div>

            {/* Results Section */}
            <div className="space-y-4">
              {result ? (
                <>
                  {/* Summary */}
                  <Card
                    className={cn(
                      result.has_contraindications
                        ? "border-purple-500 bg-purple-50 dark:bg-purple-950/20"
                        : result.has_severe_interactions
                        ? "border-red-500 bg-red-50 dark:bg-red-950/20"
                        : result.interactions.length > 0
                        ? "border-orange-500 bg-orange-50 dark:bg-orange-950/20"
                        : "border-green-500 bg-green-50 dark:bg-green-950/20"
                    )}
                  >
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        {result.has_contraindications ? (
                          <>
                            <Ban className="w-5 h-5 text-purple-600" />
                            <span className="text-purple-600">
                              Contraindications Found
                            </span>
                          </>
                        ) : result.has_severe_interactions ? (
                          <>
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                            <span className="text-red-600">
                              Severe Interactions Found
                            </span>
                          </>
                        ) : result.interactions.length > 0 ? (
                          <>
                            <AlertCircle className="w-5 h-5 text-orange-600" />
                            <span className="text-orange-600">
                              Interactions Found
                            </span>
                          </>
                        ) : (
                          <>
                            <CheckCircle className="w-5 h-5 text-green-600" />
                            <span className="text-green-600">
                              No Interactions Found
                            </span>
                          </>
                        )}
                      </CardTitle>
                      <CardDescription>
                        Checked {result.checked_drugs.length} medications:{" "}
                        {result.checked_drugs.join(", ")}
                      </CardDescription>
                    </CardHeader>
                    {result.warnings.length > 0 && (
                      <CardContent className="pt-0">
                        <div className="space-y-2">
                          {result.warnings.map((warning, i) => (
                            <p key={i} className="text-sm font-medium">
                              {warning}
                            </p>
                          ))}
                        </div>
                      </CardContent>
                    )}
                  </Card>

                  {/* Interaction Details */}
                  {result.interactions.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Interaction Details</CardTitle>
                        <CardDescription>
                          {result.interactions.length} interaction(s) found
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ScrollArea className="max-h-[400px]">
                          <div className="space-y-4">
                            {result.interactions.map((interaction, index) => {
                              const Icon =
                                severityIcons[interaction.severity];
                              return (
                                <div key={index}>
                                  {index > 0 && <Separator className="my-4" />}
                                  <div className="space-y-3">
                                    <div className="flex items-start justify-between gap-4">
                                      <div>
                                        <h4 className="font-semibold">
                                          {interaction.drug_a} +{" "}
                                          {interaction.drug_b}
                                        </h4>
                                      </div>
                                      <Badge
                                        variant={interaction.severity as "mild" | "moderate" | "severe" | "contraindicated"}
                                        className="gap-1 shrink-0"
                                      >
                                        <Icon className="w-3 h-3" />
                                        {severityLabels[interaction.severity]}
                                      </Badge>
                                    </div>
                                    <p className="text-sm">
                                      {interaction.description}
                                    </p>
                                    {interaction.mechanism && (
                                      <div className="text-sm">
                                        <span className="font-medium">
                                          Mechanism:{" "}
                                        </span>
                                        {interaction.mechanism}
                                      </div>
                                    )}
                                    {interaction.management && (
                                      <div className="text-sm">
                                        <span className="font-medium">
                                          Management:{" "}
                                        </span>
                                        {interaction.management}
                                      </div>
                                    )}
                                    {interaction.clinical_effects.length > 0 && (
                                      <div className="text-sm">
                                        <span className="font-medium">
                                          Clinical Effects:{" "}
                                        </span>
                                        {interaction.clinical_effects.join(", ")}
                                      </div>
                                    )}
                                    {interaction.source && (
                                      <p className="text-xs text-muted-foreground">
                                        Source: {interaction.source}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </ScrollArea>
                      </CardContent>
                    </Card>
                  )}

                  {/* Alternatives */}
                  {result.alternatives.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Alternative Medications</CardTitle>
                        <CardDescription>
                          Consider these alternatives to avoid interactions
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 gap-2">
                          {result.alternatives.map((drug) => (
                            <div
                              key={drug.name}
                              className="flex items-center justify-between p-2 rounded-lg bg-muted"
                            >
                              <div>
                                <span className="font-medium">{drug.name}</span>
                                {drug.drug_class && (
                                  <span className="text-sm text-muted-foreground ml-2">
                                    ({drug.drug_class})
                                  </span>
                                )}
                              </div>
                              {drug.brand_names.length > 0 && (
                                <span className="text-xs text-muted-foreground">
                                  {drug.brand_names.slice(0, 2).join(", ")}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </>
              ) : (
                /* Empty state */
                <Card className="h-[400px] flex items-center justify-center">
                  <div className="text-center">
                    <Pill className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="font-semibold mb-2">No Results Yet</h3>
                    <p className="text-sm text-muted-foreground max-w-xs">
                      Enter at least 2 medications and click "Check Interactions"
                      to see potential drug interactions.
                    </p>
                  </div>
                </Card>
              )}
            </div>
          </div>

          {/* Disclaimer */}
          <p className="text-xs text-muted-foreground text-center mt-6">
            This tool is for informational purposes only. Always verify drug
            interactions with authoritative sources and consult with a pharmacist
            or physician for clinical decisions.
          </p>
        </div>
      </div>
    </div>
  );
}

