"use client";

import React, { useState } from "react";
import { Search, Copy, Check, BookOpen, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { copyToClipboard } from "@/lib/utils";
import { api, type ICD10Code, type SNOMEDConcept } from "@/lib/api";
import { Header } from "@/components/layout/Header";

export default function CodesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [icd10Results, setIcd10Results] = useState<ICD10Code[]>([]);
  const [snomedResults, setSnomedResults] = useState<SNOMEDConcept[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("icd10");

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      if (activeTab === "icd10") {
        const results = await api.searchICD10(searchQuery);
        setIcd10Results(results);
      } else {
        const results = await api.searchSNOMED(searchQuery);
        setSnomedResults(results);
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleCopy = async (code: string) => {
    const success = await copyToClipboard(code);
    if (success) {
      setCopiedCode(code);
      setTimeout(() => setCopiedCode(null), 2000);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Medical Code Lookup"
        subtitle="Search ICD-10 and SNOMED-CT codes"
      />

      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {/* Search */}
          <Card>
            <CardContent className="pt-6">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="icd10">ICD-10</TabsTrigger>
                  <TabsTrigger value="snomed">SNOMED-CT</TabsTrigger>
                </TabsList>
              </Tabs>

              <div className="flex gap-2 mt-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={
                      activeTab === "icd10"
                        ? "Search by code (e.g., I10) or description (e.g., hypertension)"
                        : "Search by concept ID or term"
                    }
                    className="pl-10"
                  />
                </div>
                <Button onClick={handleSearch} disabled={isSearching}>
                  {isSearching ? "Searching..." : "Search"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsContent value="icd10" className="mt-0">
              {icd10Results.length > 0 ? (
                <Card>
                  <CardHeader>
                    <CardTitle>ICD-10 Results</CardTitle>
                    <CardDescription>
                      Found {icd10Results.length} codes
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="max-h-[500px]">
                      <div className="space-y-3">
                        {icd10Results.map((code) => (
                          <div
                            key={code.code}
                            className="p-4 rounded-lg border hover:border-primary/50 transition-colors"
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge variant="outline" className="font-mono">
                                    {code.code}
                                  </Badge>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 w-6 p-0"
                                    onClick={() => handleCopy(code.code)}
                                  >
                                    {copiedCode === code.code ? (
                                      <Check className="w-3 h-3 text-green-500" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                </div>
                                <p className="font-medium">{code.description}</p>
                                {code.category && (
                                  <p className="text-sm text-muted-foreground mt-1">
                                    {code.category}
                                    {code.subcategory && ` › ${code.subcategory}`}
                                  </p>
                                )}
                                {code.includes.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs font-medium text-muted-foreground">
                                      Includes:
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                      {code.includes.join(" • ")}
                                    </p>
                                  </div>
                                )}
                                {code.excludes.length > 0 && (
                                  <div className="mt-1">
                                    <p className="text-xs font-medium text-muted-foreground">
                                      Excludes:
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                      {code.excludes.join(" • ")}
                                    </p>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              ) : searchQuery && !isSearching ? (
                <Card className="py-12">
                  <div className="text-center">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="font-semibold mb-2">No Results Found</h3>
                    <p className="text-sm text-muted-foreground">
                      Try a different search term or code
                    </p>
                  </div>
                </Card>
              ) : (
                <Card className="py-12">
                  <div className="text-center">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="font-semibold mb-2">Search ICD-10 Codes</h3>
                    <p className="text-sm text-muted-foreground max-w-md mx-auto">
                      Enter a code like "I10" or search by description like
                      "hypertension" to find relevant ICD-10 codes.
                    </p>
                  </div>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="snomed" className="mt-0">
              {snomedResults.length > 0 ? (
                <Card>
                  <CardHeader>
                    <CardTitle>SNOMED-CT Results</CardTitle>
                    <CardDescription>
                      Found {snomedResults.length} concepts
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="max-h-[500px]">
                      <div className="space-y-3">
                        {snomedResults.map((concept) => (
                          <div
                            key={concept.concept_id}
                            className="p-4 rounded-lg border hover:border-primary/50 transition-colors"
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <Badge variant="outline" className="font-mono">
                                    {concept.concept_id}
                                  </Badge>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-6 w-6 p-0"
                                    onClick={() => handleCopy(concept.concept_id)}
                                  >
                                    {copiedCode === concept.concept_id ? (
                                      <Check className="w-3 h-3 text-green-500" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                </div>
                                <p className="font-medium">{concept.term}</p>
                                {concept.semantic_type && (
                                  <Badge variant="secondary" className="mt-2">
                                    {concept.semantic_type}
                                  </Badge>
                                )}
                                {concept.synonyms.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs font-medium text-muted-foreground">
                                      Synonyms:
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                      {concept.synonyms.join(" • ")}
                                    </p>
                                  </div>
                                )}
                              </div>
                              <a
                                href={`https://browser.ihtsdotools.org/?perspective=full&conceptId1=${concept.concept_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline"
                              >
                                <ExternalLink className="w-4 h-4" />
                              </a>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              ) : searchQuery && !isSearching ? (
                <Card className="py-12">
                  <div className="text-center">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="font-semibold mb-2">No Results Found</h3>
                    <p className="text-sm text-muted-foreground">
                      Try a different search term or concept ID
                    </p>
                  </div>
                </Card>
              ) : (
                <Card className="py-12">
                  <div className="text-center">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="font-semibold mb-2">Search SNOMED-CT</h3>
                    <p className="text-sm text-muted-foreground max-w-md mx-auto">
                      Enter a concept ID or clinical term to find SNOMED-CT
                      concepts with synonyms and semantic types.
                    </p>
                  </div>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

