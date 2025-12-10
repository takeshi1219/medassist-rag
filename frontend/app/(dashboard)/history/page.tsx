"use client";

import React, { useState, useEffect } from "react";
import { History, Search, Bookmark, Trash2, MessageSquare, Pill, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatDate, truncate } from "@/lib/utils";
import { Header } from "@/components/layout/Header";

interface HistoryItem {
  id: string;
  query_text: string;
  response_text: string;
  query_type: "chat" | "drug_check" | "code_lookup" | "search";
  created_at: string;
  isBookmarked?: boolean;
}

const queryTypeIcons = {
  chat: MessageSquare,
  drug_check: Pill,
  code_lookup: BookOpen,
  search: Search,
};

const queryTypeLabels = {
  chat: "Chat",
  drug_check: "Drug Check",
  code_lookup: "Code Lookup",
  search: "Search",
};

// Demo history data
const demoHistory: HistoryItem[] = [
  {
    id: "1",
    query_text: "What are the first-line treatments for hypertension?",
    response_text: "First-line treatments for hypertension include thiazide diuretics, ACE inhibitors, ARBs, and calcium channel blockers...",
    query_type: "chat",
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    isBookmarked: true,
  },
  {
    id: "2",
    query_text: "Lisinopril + Spironolactone interaction",
    response_text: "Severe interaction - Risk of hyperkalemia",
    query_type: "drug_check",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
  },
  {
    id: "3",
    query_text: "ICD-10 code for type 2 diabetes",
    response_text: "E11.9 - Type 2 diabetes mellitus without complications",
    query_type: "code_lookup",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
  },
  {
    id: "4",
    query_text: "What are the symptoms of acute myocardial infarction?",
    response_text: "Classic symptoms include chest pain/pressure, dyspnea, diaphoresis, and nausea...",
    query_type: "chat",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
    isBookmarked: true,
  },
  {
    id: "5",
    query_text: "Metformin + Iodinated contrast interaction",
    response_text: "Severe interaction - Risk of lactic acidosis",
    query_type: "drug_check",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
  },
];

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>(demoHistory);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string | null>(null);

  const filteredHistory = history.filter((item) => {
    const matchesSearch =
      !searchQuery ||
      item.query_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.response_text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = !filterType || item.query_type === filterType;
    return matchesSearch && matchesType;
  });

  const handleToggleBookmark = (id: string) => {
    setHistory((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, isBookmarked: !item.isBookmarked } : item
      )
    );
  };

  const handleDelete = (id: string) => {
    setHistory((prev) => prev.filter((item) => item.id !== id));
  };

  const bookmarkedCount = history.filter((h) => h.isBookmarked).length;

  return (
    <div className="flex flex-col h-screen">
      <Header
        title="Query History"
        subtitle="View and manage your past queries"
      />

      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">
          {/* Search and filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search history..."
                    className="pl-10"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    variant={filterType === null ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => setFilterType(null)}
                  >
                    All
                  </Button>
                  {Object.entries(queryTypeLabels).map(([type, label]) => (
                    <Button
                      key={type}
                      variant={filterType === type ? "secondary" : "outline"}
                      size="sm"
                      onClick={() => setFilterType(type)}
                    >
                      {label}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{history.length}</div>
                <p className="text-sm text-muted-foreground">Total Queries</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{bookmarkedCount}</div>
                <p className="text-sm text-muted-foreground">Bookmarked</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">
                  {history.filter((h) => h.query_type === "chat").length}
                </div>
                <p className="text-sm text-muted-foreground">Chat Queries</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">
                  {history.filter((h) => h.query_type === "drug_check").length}
                </div>
                <p className="text-sm text-muted-foreground">Drug Checks</p>
              </CardContent>
            </Card>
          </div>

          {/* History list */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>
                {filteredHistory.length} items
                {filterType && ` (filtered by ${queryTypeLabels[filterType as keyof typeof queryTypeLabels]})`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {filteredHistory.length > 0 ? (
                <ScrollArea className="max-h-[500px]">
                  <div className="space-y-3">
                    {filteredHistory.map((item) => {
                      const Icon = queryTypeIcons[item.query_type];
                      return (
                        <div
                          key={item.id}
                          className="p-4 rounded-lg border hover:border-primary/50 transition-colors"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <Badge variant="outline" className="gap-1">
                                  <Icon className="w-3 h-3" />
                                  {queryTypeLabels[item.query_type]}
                                </Badge>
                                {item.isBookmarked && (
                                  <Badge variant="secondary">
                                    <Bookmark className="w-3 h-3 mr-1" />
                                    Saved
                                  </Badge>
                                )}
                                <span className="text-xs text-muted-foreground">
                                  {formatDate(item.created_at)}
                                </span>
                              </div>
                              <p className="font-medium mb-1">{item.query_text}</p>
                              <p className="text-sm text-muted-foreground">
                                {truncate(item.response_text, 150)}
                              </p>
                            </div>
                            <div className="flex gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                onClick={() => handleToggleBookmark(item.id)}
                              >
                                <Bookmark
                                  className={`w-4 h-4 ${
                                    item.isBookmarked
                                      ? "fill-current text-primary"
                                      : ""
                                  }`}
                                />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                                onClick={() => handleDelete(item.id)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>
              ) : (
                <div className="text-center py-12">
                  <History className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="font-semibold mb-2">No History Found</h3>
                  <p className="text-sm text-muted-foreground">
                    {searchQuery || filterType
                      ? "No items match your search criteria"
                      : "Your query history will appear here"}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

