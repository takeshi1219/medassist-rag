"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Loader2,
  Sparkles,
  Copy,
  Check,
  ExternalLink,
  RefreshCw,
  Bookmark,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn, copyToClipboard, formatDuration, generateId } from "@/lib/utils";
import { api, type Citation, type ChatResponse } from "@/lib/api";
import { Header } from "@/components/layout/Header";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Citation[];
  timestamp: Date;
  processingTime?: number;
  isStreaming?: boolean;
}

const suggestedQueries = [
  "What are the first-line treatments for hypertension?",
  "What is the treatment algorithm for type 2 diabetes?",
  "What are the symptoms of acute myocardial infarction?",
  "How should community-acquired pneumonia be treated?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (query: string) => {
    if (!query.trim() || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: query,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Create streaming message placeholder
    const assistantId = generateId();
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // Use regular API for now (streaming would need SSE handling)
      const response: ChatResponse = await api.chat({
        query,
        conversation_id: conversationId || undefined,
        language: "en",
        include_sources: true,
      });

      setConversationId(response.conversation_id);

      // Update the message with the response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content: response.answer,
                sources: response.sources,
                processingTime: response.processing_time_ms,
                isStreaming: false,
              }
            : msg
        )
      );
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? {
                ...msg,
                content:
                  "I apologize, but an error occurred while processing your query. Please try again.",
                isStreaming: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (text: string, id: string) => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const toggleSourceExpanded = (messageId: string) => {
    setExpandedSources((prev) => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(input);
    }
  };

  return (
    <TooltipProvider>
      <div className="flex flex-col h-screen">
        <Header
          title="Medical Chat"
          subtitle="Ask evidence-based medical questions"
        />

        <div className="flex-1 flex overflow-hidden">
          {/* Main chat area */}
          <div className="flex-1 flex flex-col">
            <ScrollArea className="flex-1 px-4">
              <div className="max-w-4xl mx-auto py-6 space-y-6">
                {messages.length === 0 ? (
                  /* Welcome screen */
                  <div className="text-center py-12">
                    <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-primary/10 flex items-center justify-center">
                      <Sparkles className="w-8 h-8 text-primary" />
                    </div>
                    <h2 className="text-2xl font-semibold mb-2">
                      Welcome to MedAssist
                    </h2>
                    <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                      Ask any medical question and get evidence-based answers
                      with citations from medical literature.
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                      {suggestedQueries.map((query) => (
                        <Button
                          key={query}
                          variant="outline"
                          className="h-auto py-3 px-4 text-left justify-start text-sm"
                          onClick={() => handleSubmit(query)}
                        >
                          {query}
                        </Button>
                      ))}
                    </div>
                  </div>
                ) : (
                  /* Messages */
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        "flex gap-4 chat-message",
                        message.role === "user" && "flex-row-reverse"
                      )}
                    >
                      {/* Avatar */}
                      <div
                        className={cn(
                          "w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-medium",
                          message.role === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-secondary text-secondary-foreground"
                        )}
                      >
                        {message.role === "user" ? "U" : "AI"}
                      </div>

                      {/* Content */}
                      <div
                        className={cn(
                          "flex-1 max-w-[80%]",
                          message.role === "user" && "flex flex-col items-end"
                        )}
                      >
                        <Card
                          className={cn(
                            message.role === "user" &&
                              "bg-primary text-primary-foreground"
                          )}
                        >
                          <CardContent className="p-4">
                            {message.isStreaming ? (
                              <div className="flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm">Thinking...</span>
                              </div>
                            ) : (
                              <div
                                className={cn(
                                  "prose prose-sm max-w-none",
                                  message.role === "user" && "prose-invert"
                                )}
                              >
                                <ReactMarkdown>{message.content}</ReactMarkdown>
                              </div>
                            )}
                          </CardContent>
                        </Card>

                        {/* Actions & Sources */}
                        {message.role === "assistant" && !message.isStreaming && (
                          <div className="mt-2 space-y-2">
                            {/* Action buttons */}
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-7 px-2"
                                    onClick={() =>
                                      handleCopy(message.content, message.id)
                                    }
                                  >
                                    {copiedId === message.id ? (
                                      <Check className="w-3 h-3" />
                                    ) : (
                                      <Copy className="w-3 h-3" />
                                    )}
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Copy response</TooltipContent>
                              </Tooltip>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-7 px-2"
                                  >
                                    <RefreshCw className="w-3 h-3" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Regenerate</TooltipContent>
                              </Tooltip>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    className="h-7 px-2"
                                  >
                                    <Bookmark className="w-3 h-3" />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>Bookmark</TooltipContent>
                              </Tooltip>
                              {message.processingTime && (
                                <span>
                                  {formatDuration(message.processingTime)}
                                </span>
                              )}
                            </div>

                            {/* Sources */}
                            {message.sources && message.sources.length > 0 && (
                              <div className="space-y-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 text-xs"
                                  onClick={() => toggleSourceExpanded(message.id)}
                                >
                                  {expandedSources.has(message.id)
                                    ? "Hide"
                                    : "Show"}{" "}
                                  {message.sources.length} sources
                                </Button>
                                {expandedSources.has(message.id) && (
                                  <div className="space-y-2">
                                    {message.sources.map((source) => (
                                      <Card
                                        key={source.id}
                                        className="citation-card"
                                      >
                                        <CardHeader className="p-3 pb-2">
                                          <div className="flex items-start justify-between gap-2">
                                            <CardTitle className="text-sm font-medium leading-tight">
                                              [{source.id}] {source.title}
                                            </CardTitle>
                                            <Badge variant="outline" className="text-xs shrink-0">
                                              {Math.round(source.relevance_score * 100)}%
                                            </Badge>
                                          </div>
                                        </CardHeader>
                                        <CardContent className="p-3 pt-0">
                                          <p className="text-xs text-muted-foreground mb-2">
                                            {source.snippet}
                                          </p>
                                          <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                                            {source.journal && (
                                              <span>{source.journal}</span>
                                            )}
                                            {source.year && (
                                              <span>({source.year})</span>
                                            )}
                                            {source.doi && (
                                              <a
                                                href={`https://doi.org/${source.doi}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-primary hover:underline flex items-center gap-1"
                                              >
                                                DOI
                                                <ExternalLink className="w-3 h-3" />
                                              </a>
                                            )}
                                            {source.pmid && (
                                              <a
                                                href={`https://pubmed.ncbi.nlm.nih.gov/${source.pmid}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-primary hover:underline flex items-center gap-1"
                                              >
                                                PubMed
                                                <ExternalLink className="w-3 h-3" />
                                              </a>
                                            )}
                                          </div>
                                        </CardContent>
                                      </Card>
                                    ))}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Input area */}
            <div className="border-t p-4 bg-background">
              <div className="max-w-4xl mx-auto">
                <div className="relative">
                  <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a medical question..."
                    className="min-h-[60px] max-h-[200px] pr-12 resize-none"
                    disabled={isLoading}
                  />
                  <Button
                    size="icon"
                    className="absolute right-2 bottom-2"
                    onClick={() => handleSubmit(input)}
                    disabled={!input.trim() || isLoading}
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  MedAssist provides information for clinical decision support.
                  Always verify critical information.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </TooltipProvider>
  );
}

