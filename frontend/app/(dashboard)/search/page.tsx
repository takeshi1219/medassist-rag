"use client";

import React, { useState } from "react";
import { Search, FileText, BookOpen, Pill, ExternalLink, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { Header } from "@/components/layout/Header";

interface SearchResult {
  id: string;
  content: string;
  title?: string;
  source_type: string;
  score: number;
  metadata?: Record<string, unknown>;
}

const sourceTypeIcons = {
  paper: FileText,
  guideline: BookOpen,
  drug_info: Pill,
  unknown: FileText,
};

const sourceTypeLabels = {
  paper: "Research Paper",
  guideline: "Clinical Guideline",
  drug_info: "Drug Information",
  unknown: "Document",
};

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [sourceFilter, setSourceFilter] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const response = await api.search(query, 20, sourceFilter || undefined);
      setResults(response.results);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const filteredResults = sourceFilter
    ? results.filter((r) => r.source_type === sourceFilter)
    : results;

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Search Medical Literature"
        subtitle="Search through medical papers, guidelines, and drug information"
      />

      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {/* Search input */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Search medical literature..."
                    className="pl-10"
                  />
                </div>
                <Button onClick={handleSearch} disabled={isSearching}>
                  {isSearching ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    "Search"
                  )}
                </Button>
              </div>

              {/* Source type filters */}
              <div className="flex gap-2 mt-4">
                <Button
                  variant={sourceFilter === null ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setSourceFilter(null)}
                >
                  All Sources
                </Button>
                {Object.entries(sourceTypeLabels).map(([type, label]) => (
                  type !== "unknown" && (
                    <Button
                      key={type}
                      variant={sourceFilter === type ? "secondary" : "outline"}
                      size="sm"
                      onClick={() => setSourceFilter(type)}
                    >
                      {label}
                    </Button>
                  )
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {results.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Search Results</CardTitle>
                <CardDescription>
                  Found {filteredResults.length} results for "{query}"
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="max-h-[600px]">
                  <div className="space-y-4">
                    {filteredResults.map((result) => {
                      const Icon = sourceTypeIcons[result.source_type as keyof typeof sourceTypeIcons] || sourceTypeIcons.unknown;
                      const label = sourceTypeLabels[result.source_type as keyof typeof sourceTypeLabels] || sourceTypeLabels.unknown;
                      
                      return (
                        <div
                          key={result.id}
                          className="p-4 rounded-lg border hover:border-primary/50 transition-colors"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className="gap-1">
                                  <Icon className="w-3 h-3" />
                                  {label}
                                </Badge>
                                <Badge variant="secondary">
                                  {Math.round(result.score * 100)}% match
                                </Badge>
                              </div>
                              {result.title && (
                                <h3 className="font-semibold mb-2">{result.title}</h3>
                              )}
                              <p className="text-sm text-muted-foreground">
                                {result.content.length > 300
                                  ? result.content.slice(0, 300) + "..."
                                  : result.content}
                              </p>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          ) : query && !isSearching ? (
            <Card className="py-12">
              <div className="text-center">
                <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-semibold mb-2">No Results Found</h3>
                <p className="text-sm text-muted-foreground">
                  Try different search terms or broaden your query
                </p>
              </div>
            </Card>
          ) : (
            <Card className="py-12">
              <div className="text-center">
                <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-semibold mb-2">Search Medical Literature</h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto">
                  Enter a search query to find relevant medical papers, clinical
                  guidelines, and drug information from our knowledge base.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => {
                      setQuery("hypertension treatment guidelines");
                      handleSearch();
                    }}
                  >
                    hypertension treatment
                  </Badge>
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => {
                      setQuery("diabetes management");
                      handleSearch();
                    }}
                  >
                    diabetes management
                  </Badge>
                  <Badge
                    variant="outline"
                    className="cursor-pointer hover:bg-muted"
                    onClick={() => {
                      setQuery("antibiotic guidelines pneumonia");
                      handleSearch();
                    }}
                  >
                    pneumonia antibiotics
                  </Badge>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

