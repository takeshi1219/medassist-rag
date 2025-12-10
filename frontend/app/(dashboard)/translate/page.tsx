"use client";

import React, { useState } from "react";
import { Languages, ArrowRightLeft, Loader2, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type MedicalTermTranslation } from "@/lib/api";
import { Header } from "@/components/layout/Header";

const exampleTerms = [
  { ja: "高血圧", en: "Hypertension" },
  { ja: "糖尿病", en: "Diabetes mellitus" },
  { ja: "肺炎", en: "Pneumonia" },
  { ja: "心筋梗塞", en: "Myocardial infarction" },
];

export default function TranslatePage() {
  const [term, setTerm] = useState("");
  const [fromLang, setFromLang] = useState<"en" | "ja">("ja");
  const [toLang, setToLang] = useState<"en" | "ja">("en");
  const [isTranslating, setIsTranslating] = useState(false);
  const [result, setResult] = useState<MedicalTermTranslation | null>(null);

  const handleSwapLanguages = () => {
    setFromLang(toLang);
    setToLang(fromLang);
    setResult(null);
  };

  const handleTranslate = async () => {
    if (!term.trim()) return;

    setIsTranslating(true);
    try {
      const translation = await api.translateTerm(term, fromLang, toLang);
      setResult(translation);
    } catch (error) {
      console.error("Translation error:", error);
    } finally {
      setIsTranslating(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleTranslate();
    }
  };

  const handleExampleClick = (example: { ja: string; en: string }) => {
    const termToUse = fromLang === "ja" ? example.ja : example.en;
    setTerm(termToUse);
  };

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Medical Term Translation"
        subtitle="Translate medical terms between Japanese and English"
      />

      <div className="flex-1 overflow-auto">
        <div className="max-w-2xl mx-auto p-6 space-y-6">
          {/* Translation Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Languages className="w-5 h-5" />
                Translate Medical Terms
              </CardTitle>
              <CardDescription>
                Get accurate translations with medical context and ICD-10 codes
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Language selector */}
              <div className="flex items-center justify-center gap-4">
                <div className="flex-1 text-center">
                  <Badge variant="outline" className="text-lg px-4 py-2">
                    {fromLang === "ja" ? "日本語 (Japanese)" : "English"}
                  </Badge>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleSwapLanguages}
                  className="rounded-full"
                >
                  <ArrowRightLeft className="w-5 h-5" />
                </Button>
                <div className="flex-1 text-center">
                  <Badge variant="outline" className="text-lg px-4 py-2">
                    {toLang === "ja" ? "日本語 (Japanese)" : "English"}
                  </Badge>
                </div>
              </div>

              {/* Input */}
              <div className="flex gap-2">
                <Input
                  value={term}
                  onChange={(e) => setTerm(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    fromLang === "ja"
                      ? "医学用語を入力してください..."
                      : "Enter a medical term..."
                  }
                  className="text-lg"
                />
                <Button onClick={handleTranslate} disabled={isTranslating}>
                  {isTranslating ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    "Translate"
                  )}
                </Button>
              </div>

              {/* Example terms */}
              <div className="pt-2">
                <p className="text-sm text-muted-foreground mb-2">
                  Try these examples:
                </p>
                <div className="flex flex-wrap gap-2">
                  {exampleTerms.map((example) => (
                    <Button
                      key={example.ja}
                      variant="outline"
                      size="sm"
                      onClick={() => handleExampleClick(example)}
                    >
                      {fromLang === "ja" ? example.ja : example.en}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Result */}
          {result && (
            <Card>
              <CardHeader>
                <CardTitle>Translation Result</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Main translation */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-muted">
                    <p className="text-xs text-muted-foreground mb-1">
                      {result.from_language === "ja" ? "Japanese" : "English"}
                    </p>
                    <p className="text-lg font-medium">{result.original_term}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-primary/10">
                    <p className="text-xs text-muted-foreground mb-1">
                      {result.to_language === "ja" ? "Japanese" : "English"}
                    </p>
                    <p className="text-lg font-medium text-primary">
                      {result.translated_term}
                    </p>
                  </div>
                </div>

                {/* Medical context */}
                {result.medical_context && (
                  <div className="p-4 rounded-lg border">
                    <p className="text-sm font-medium mb-1">Medical Context</p>
                    <p className="text-sm text-muted-foreground">
                      {result.medical_context}
                    </p>
                  </div>
                )}

                {/* ICD-10 codes */}
                {result.icd10_codes.length > 0 && (
                  <div className="p-4 rounded-lg border">
                    <p className="text-sm font-medium mb-2">Related ICD-10 Codes</p>
                    <div className="flex flex-wrap gap-2">
                      {result.icd10_codes.map((code) => (
                        <Badge key={code} variant="secondary" className="font-mono">
                          {code}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Layman explanation */}
                {result.layman_explanation && (
                  <div className="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                    <div className="flex items-center gap-2 mb-2">
                      <Info className="w-4 h-4 text-secondary" />
                      <p className="text-sm font-medium">Patient-Friendly Explanation</p>
                    </div>
                    <p className="text-sm">{result.layman_explanation}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Empty state */}
          {!result && !isTranslating && (
            <Card className="py-12">
              <div className="text-center">
                <Languages className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-semibold mb-2">Enter a Medical Term</h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  Type a medical term in{" "}
                  {fromLang === "ja" ? "Japanese" : "English"} to get its
                  translation with medical context and related codes.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

