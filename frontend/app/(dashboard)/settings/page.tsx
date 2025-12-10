"use client";

import React, { useState } from "react";
import { Settings, User, Bell, Shield, Globe, Moon, Sun, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Header } from "@/components/layout/Header";

export default function SettingsPage() {
  const [theme, setTheme] = useState<"light" | "dark" | "system">("system");
  const [language, setLanguage] = useState<"en" | "ja">("en");
  const [notifications, setNotifications] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex flex-col h-screen">
      <Header title="Settings" subtitle="Manage your account and preferences" />

      <div className="flex-1 overflow-auto">
        <div className="max-w-2xl mx-auto p-6 space-y-6">
          {/* Profile Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Profile
              </CardTitle>
              <CardDescription>
                Manage your account information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Name</label>
                  <Input defaultValue="Dr. Demo User" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium">Email</label>
                  <Input defaultValue="demo@medassist.com" className="mt-1" disabled />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Organization</label>
                  <Input defaultValue="Demo Hospital" className="mt-1" />
                </div>
                <div>
                  <label className="text-sm font-medium">License Number</label>
                  <Input defaultValue="MD123456" className="mt-1" />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Role</label>
                <div className="mt-1">
                  <Badge variant="secondary">Physician</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Appearance Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Moon className="w-5 h-5" />
                Appearance
              </CardTitle>
              <CardDescription>Customize the look and feel</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Theme</label>
                <div className="flex gap-2">
                  <Button
                    variant={theme === "light" ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => setTheme("light")}
                    className="gap-2"
                  >
                    <Sun className="w-4 h-4" />
                    Light
                  </Button>
                  <Button
                    variant={theme === "dark" ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => setTheme("dark")}
                    className="gap-2"
                  >
                    <Moon className="w-4 h-4" />
                    Dark
                  </Button>
                  <Button
                    variant={theme === "system" ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => setTheme("system")}
                  >
                    System
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Language Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="w-5 h-5" />
                Language
              </CardTitle>
              <CardDescription>Set your preferred language</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Button
                  variant={language === "en" ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setLanguage("en")}
                >
                  English
                </Button>
                <Button
                  variant={language === "ja" ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setLanguage("ja")}
                >
                  日本語
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Notification Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notifications
              </CardTitle>
              <CardDescription>Manage notification preferences</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Email Notifications</p>
                  <p className="text-sm text-muted-foreground">
                    Receive updates about new features and alerts
                  </p>
                </div>
                <Button
                  variant={notifications ? "secondary" : "outline"}
                  size="sm"
                  onClick={() => setNotifications(!notifications)}
                >
                  {notifications ? "Enabled" : "Disabled"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security
              </CardTitle>
              <CardDescription>Manage your account security</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Password</p>
                  <p className="text-sm text-muted-foreground">
                    Last changed 30 days ago
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Change Password
                </Button>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Two-Factor Authentication</p>
                  <p className="text-sm text-muted-foreground">
                    Add an extra layer of security
                  </p>
                </div>
                <Button variant="outline" size="sm">
                  Enable
                </Button>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Session Timeout</p>
                  <p className="text-sm text-muted-foreground">
                    Auto-logout after 30 minutes of inactivity
                  </p>
                </div>
                <Badge variant="secondary">30 min</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end">
            <Button onClick={handleSave} className="gap-2">
              {saved ? (
                <>
                  <Check className="w-4 h-4" />
                  Saved
                </>
              ) : (
                "Save Changes"
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

