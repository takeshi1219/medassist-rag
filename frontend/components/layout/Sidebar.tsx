"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  Pill,
  Search,
  History,
  Settings,
  BookOpen,
  Languages,
  Activity,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const navItems = [
  {
    title: "Chat",
    href: "/chat",
    icon: MessageSquare,
    description: "Ask medical questions",
  },
  {
    title: "Drug Checker",
    href: "/drug-checker",
    icon: Pill,
    description: "Check drug interactions",
  },
  {
    title: "Code Lookup",
    href: "/codes",
    icon: BookOpen,
    description: "ICD-10 & SNOMED codes",
  },
  {
    title: "Translate",
    href: "/translate",
    icon: Languages,
    description: "Medical term translation",
  },
  {
    title: "Search",
    href: "/search",
    icon: Search,
    description: "Search medical literature",
  },
  {
    title: "History",
    href: "/history",
    icon: History,
    description: "Query history",
  },
];

const bottomItems = [
  {
    title: "Settings",
    href: "/settings",
    icon: Settings,
    description: "App settings",
  },
];

export function Sidebar({ isCollapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "flex flex-col h-screen bg-card border-r transition-all duration-300 relative",
          isCollapsed ? "w-16" : "w-64"
        )}
      >
        {/* Logo */}
        <div className="flex items-center h-16 px-4 border-b">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary text-primary-foreground">
              <Activity className="w-5 h-5" />
            </div>
            {!isCollapsed && (
              <span className="font-semibold text-lg">MedAssist</span>
            )}
          </Link>
        </div>

        {/* Toggle button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute -right-3 top-20 h-6 w-6 rounded-full border bg-background shadow-md z-10"
          onClick={onToggle}
        >
          {isCollapsed ? (
            <ChevronRight className="h-3 w-3" />
          ) : (
            <ChevronLeft className="h-3 w-3" />
          )}
        </Button>

        {/* Navigation */}
        <nav className="flex-1 py-4 overflow-y-auto">
          <div className="space-y-1 px-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;

              return isCollapsed ? (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link href={item.href}>
                      <Button
                        variant={isActive ? "secondary" : "ghost"}
                        size="icon"
                        className={cn(
                          "w-full h-10",
                          isActive && "bg-primary/10 text-primary"
                        )}
                      >
                        <Icon className="h-5 w-5" />
                      </Button>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="flex flex-col">
                    <span className="font-medium">{item.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {item.description}
                    </span>
                  </TooltipContent>
                </Tooltip>
              ) : (
                <Link key={item.href} href={item.href}>
                  <Button
                    variant={isActive ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start gap-3",
                      isActive && "bg-primary/10 text-primary"
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.title}</span>
                  </Button>
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Bottom section */}
        <div className="p-2 border-t">
          <Separator className="mb-2" />
          {bottomItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return isCollapsed ? (
              <Tooltip key={item.href}>
                <TooltipTrigger asChild>
                  <Link href={item.href}>
                    <Button
                      variant={isActive ? "secondary" : "ghost"}
                      size="icon"
                      className="w-full h-10"
                    >
                      <Icon className="h-5 w-5" />
                    </Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent side="right">
                  <span>{item.title}</span>
                </TooltipContent>
              </Tooltip>
            ) : (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className="w-full justify-start gap-3"
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.title}</span>
                </Button>
              </Link>
            );
          })}

          {/* Logout */}
          {isCollapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="w-full h-10 text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  <LogOut className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <span>Logout</span>
              </TooltipContent>
            </Tooltip>
          ) : (
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-destructive hover:text-destructive hover:bg-destructive/10"
            >
              <LogOut className="h-5 w-5" />
              <span>Logout</span>
            </Button>
          )}
        </div>
      </aside>
    </TooltipProvider>
  );
}

