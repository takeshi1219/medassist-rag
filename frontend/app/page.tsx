"use client";

import React from "react";
import Link from "next/link";
import {
  MessageSquare,
  Pill,
  BookOpen,
  Languages,
  Search,
  Shield,
  Zap,
  Globe,
  ArrowRight,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: MessageSquare,
    title: "Medical Chat",
    description: "Ask medical questions and get evidence-based answers with citations",
    href: "/login",
    color: "text-blue-500",
  },
  {
    icon: Pill,
    title: "Drug Interaction Checker",
    description: "Check interactions between multiple medications instantly",
    href: "/login",
    color: "text-green-500",
  },
  {
    icon: BookOpen,
    title: "Medical Code Lookup",
    description: "Search ICD-10 and SNOMED-CT codes quickly",
    href: "/login",
    color: "text-purple-500",
  },
  {
    icon: Languages,
    title: "Medical Translation",
    description: "Translate medical terms between Japanese and English",
    href: "/login",
    color: "text-orange-500",
  },
];

const benefits = [
  {
    icon: Shield,
    title: "HIPAA Compliant",
    description: "Enterprise-grade security for sensitive medical data",
  },
  {
    icon: Zap,
    title: "Real-time Responses",
    description: "Get answers in seconds with streaming AI responses",
  },
  {
    icon: Globe,
    title: "Multi-language Support",
    description: "Full support for English and Japanese medical queries",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen gradient-mesh">
      {/* Hero Section */}
      <div className="relative">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 lg:px-12">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-primary-foreground">
              <Activity className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold">MedAssist RAG</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </header>

        {/* Hero Content */}
        <div className="px-6 py-20 lg:px-12 lg:py-32 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 text-sm font-medium rounded-full bg-primary/10 text-primary">
            <Zap className="w-4 h-4" />
            Powered by GPT-4o & RAG Technology
          </div>
          <h1 className="text-4xl lg:text-6xl font-bold tracking-tight mb-6">
            Clinical Decision Support
            <br />
            <span className="text-primary">Powered by AI</span>
          </h1>
          <p className="text-lg lg:text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            MedAssist RAG helps healthcare professionals access medical information
            through natural language queries with accurate, citation-backed answers
            from medical literature.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2">
                Create Free Account
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="gap-2">
                Sign In
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="px-6 py-20 lg:px-12 bg-muted/50">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">Clinical Tools</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Comprehensive suite of AI-powered tools designed for healthcare professionals
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link key={feature.href} href={feature.href}>
                <Card className="h-full transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer">
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-lg bg-background flex items-center justify-center mb-2 ${feature.color}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <span className="text-sm text-primary font-medium flex items-center gap-1">
                      Get started
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Benefits Section */}
      <section className="px-6 py-20 lg:px-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">
                Built for Healthcare Professionals
              </h2>
              <p className="text-muted-foreground mb-8">
                MedAssist RAG is designed with the unique needs of healthcare providers
                in mind. Our platform combines cutting-edge AI technology with medical
                literature to provide accurate, reliable clinical decision support.
              </p>
              <div className="space-y-6">
                {benefits.map((benefit) => {
                  const Icon = benefit.icon;
                  return (
                    <div key={benefit.title} className="flex gap-4">
                      <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{benefit.title}</h3>
                        <p className="text-sm text-muted-foreground">
                          {benefit.description}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square rounded-2xl bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <div className="text-center p-8">
                  <Activity className="w-24 h-24 mx-auto mb-4 text-primary" />
                  <p className="text-xl font-semibold">Evidence-Based Answers</p>
                  <p className="text-muted-foreground">
                    Every response includes citations to medical literature
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20 lg:px-12 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Enhance Your Clinical Practice?
          </h2>
          <p className="text-lg opacity-90 mb-8">
            Join healthcare professionals using AI-powered clinical decision support
          </p>
          <Link href="/register">
            <Button size="lg" variant="secondary" className="gap-2">
              Create Your Account
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-8 lg:px-12 border-t">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary" />
            <span className="font-semibold">MedAssist RAG</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Clinical decision support tool. Not a substitute for professional medical advice.
          </p>
          <p className="text-sm text-muted-foreground">
            © 2024 MedAssist. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

