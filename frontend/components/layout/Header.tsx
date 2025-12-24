"use client";

import React from "react";
import { Bell, Sun, Moon, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useAuth } from "@/contexts/AuthContext";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  const [isDark, setIsDark] = React.useState(false);
  const { user } = useAuth();

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle("dark");
  };

  // Get user initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  // Format role for display
  const formatRole = (role: string) => {
    return role.charAt(0).toUpperCase() + role.slice(1);
  };

  return (
    <TooltipProvider>
      <header className="flex items-center justify-between h-16 px-6 border-b bg-card">
        {/* Left - Title */}
        <div>
          {title && <h1 className="text-xl font-semibold">{title}</h1>}
          {subtitle && (
            <p className="text-sm text-muted-foreground">{subtitle}</p>
          )}
        </div>

        {/* Right - Actions */}
        <div className="flex items-center gap-2">
          {/* Theme toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={toggleTheme}>
                {isDark ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <span>Toggle theme</span>
            </TooltipContent>
          </Tooltip>

          {/* Notifications */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <span>Notifications</span>
            </TooltipContent>
          </Tooltip>

          {/* User menu */}
          <div className="flex items-center gap-3 ml-2 pl-4 border-l">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium">{user?.name || "Guest"}</p>
              <p className="text-xs text-muted-foreground">
                {user?.role ? formatRole(user.role) : ""}
              </p>
            </div>
            <Avatar className="h-9 w-9">
              <AvatarImage src="" alt={user?.name || "User"} />
              <AvatarFallback className="bg-primary text-primary-foreground">
                {user?.name ? getInitials(user.name) : <User className="h-4 w-4" />}
              </AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>
    </TooltipProvider>
  );
}

