"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  MessageSquare,
  Pill,
  BookOpen,
  Languages,
  Shield,
  Zap,
  Globe,
  ArrowRight,
  Sparkles,
  HeartPulse,
  Brain,
  FileText,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: MessageSquare,
    title: "AI Medical Chat",
    description: "Evidence-based answers with citations from peer-reviewed literature",
    gradient: "from-cyan-500 to-teal-500",
  },
  {
    icon: Pill,
    title: "Drug Interactions",
    description: "Real-time analysis of medication interactions and contraindications",
    gradient: "from-emerald-500 to-green-500",
  },
  {
    icon: BookOpen,
    title: "Code Lookup",
    description: "Instant ICD-10 and SNOMED-CT code search and validation",
    gradient: "from-violet-500 to-purple-500",
  },
  {
    icon: Languages,
    title: "Medical Translation",
    description: "Accurate Japanese-English medical terminology translation",
    gradient: "from-amber-500 to-orange-500",
  },
];

const stats = [
  { value: "GPT-4o", label: "Powered by" },
  { value: "RAG", label: "Architecture" },
  { value: "24/7", label: "Availability" },
  { value: "HIPAA", label: "Compliant" },
];

const benefits = [
  { icon: Shield, text: "Enterprise-grade security & HIPAA compliance" },
  { icon: Zap, text: "Sub-second response times with streaming" },
  { icon: Globe, text: "Multi-language support (EN/JP)" },
  { icon: FileText, text: "Every answer backed by citations" },
];

export default function HomePage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-teal-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl animate-pulse delay-500" />
        {/* Grid pattern */}
        <div 
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), 
                             linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
            backgroundSize: '60px 60px'
          }}
        />
      </div>

      {/* Header */}
      <header className="relative z-50">
        <nav className="flex items-center justify-between px-6 lg:px-12 py-5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-teal-500 flex items-center justify-center">
                <HeartPulse className="w-5 h-5 text-white" />
              </div>
              <div className="absolute -inset-1 bg-gradient-to-br from-cyan-400 to-teal-500 rounded-xl blur opacity-30" />
            </div>
            <span className="text-xl font-bold tracking-tight">
              Med<span className="text-cyan-400">Assist</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button 
                variant="ghost" 
                className="text-slate-300 hover:text-white hover:bg-white/10"
              >
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-white border-0 shadow-lg shadow-cyan-500/25">
                Get Started
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative px-6 lg:px-12 pt-16 lg:pt-24 pb-20">
        <div className="max-w-6xl mx-auto">
          <div className={`transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            {/* Badge */}
            <div className="flex justify-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium">
                <Sparkles className="w-4 h-4" />
                <span>Powered by GPT-4o & RAG Technology</span>
              </div>
            </div>

            {/* Main heading */}
            <h1 className="text-center text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight mb-6">
              <span className="text-white">Clinical Intelligence</span>
              <br />
              <span className="bg-gradient-to-r from-cyan-400 via-teal-400 to-emerald-400 bg-clip-text text-transparent">
                At Your Fingertips
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-center text-lg lg:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              AI-powered clinical decision support for healthcare professionals. 
              Get evidence-based answers with citations from peer-reviewed medical literature.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-16">
              <Link href="/register">
                <Button 
                  size="lg" 
                  className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-white border-0 shadow-xl shadow-cyan-500/30 text-base px-8 h-12"
                >
                  Start Free Trial
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <Link href="/login">
                <Button 
                  size="lg" 
                  variant="outline"
                  className="border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white text-base px-8 h-12"
                >
                  Sign In to Dashboard
                </Button>
              </Link>
            </div>

            {/* Stats */}
            <div className="flex flex-wrap justify-center gap-8 lg:gap-16">
              {stats.map((stat, i) => (
                <div 
                  key={stat.label} 
                  className={`text-center transition-all duration-700 delay-${i * 100} ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}
                >
                  <div className="text-2xl lg:text-3xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-sm text-slate-500 uppercase tracking-wider">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative px-6 lg:px-12 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              Comprehensive <span className="text-cyan-400">Clinical Tools</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Everything healthcare professionals need in one intelligent platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Link 
                  key={feature.title} 
                  href="/login"
                  className={`group relative transition-all duration-500 delay-${index * 100}`}
                >
                  <div className="relative p-8 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all duration-300 hover:transform hover:-translate-y-1">
                    {/* Gradient glow on hover */}
                    <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
                    
                    <div className="relative z-10">
                      <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 shadow-lg`}>
                        <Icon className="w-7 h-7 text-white" />
                      </div>
                      <h3 className="text-xl font-semibold mb-3 text-white group-hover:text-cyan-400 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-slate-400 mb-4 leading-relaxed">
                        {feature.description}
                      </p>
                      <div className="flex items-center text-cyan-400 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                        <span>Get started</span>
                        <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="relative px-6 lg:px-12 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold mb-6">
                Built for <span className="text-cyan-400">Healthcare</span> Professionals
              </h2>
              <p className="text-slate-400 mb-10 text-lg leading-relaxed">
                MedAssist combines cutting-edge AI with rigorous medical literature analysis 
                to provide accurate, reliable clinical decision support you can trust.
              </p>
              
              <div className="space-y-5">
                {benefits.map((benefit, index) => {
                  const Icon = benefit.icon;
                  return (
                    <div 
                      key={benefit.text}
                      className="flex items-center gap-4 group"
                    >
                      <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center group-hover:bg-cyan-500/20 transition-colors">
                        <Icon className="w-5 h-5 text-cyan-400" />
                      </div>
                      <span className="text-slate-300">{benefit.text}</span>
                    </div>
                  );
                })}
              </div>

              <div className="mt-10">
                <Link href="/register">
                  <Button 
                    size="lg"
                    className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 text-white border-0"
                  >
                    Create Free Account
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>

            {/* Visual element */}
            <div className="relative">
              <div className="relative aspect-square max-w-md mx-auto">
                {/* Outer ring */}
                <div className="absolute inset-0 rounded-full border border-slate-800" />
                <div className="absolute inset-4 rounded-full border border-slate-800/50" />
                <div className="absolute inset-8 rounded-full border border-slate-800/30" />
                
                {/* Center element */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative">
                    <div className="w-32 h-32 rounded-full bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center">
                      <Brain className="w-16 h-16 text-white" />
                    </div>
                    <div className="absolute -inset-4 bg-gradient-to-br from-cyan-500 to-teal-500 rounded-full blur-2xl opacity-30" />
                  </div>
                </div>

                {/* Floating icons */}
                <div className="absolute top-8 left-1/2 -translate-x-1/2 w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center animate-float">
                  <MessageSquare className="w-6 h-6 text-cyan-400" />
                </div>
                <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center animate-float-delayed">
                  <FileText className="w-6 h-6 text-emerald-400" />
                </div>
                <div className="absolute left-8 top-1/2 -translate-y-1/2 w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center animate-float">
                  <Pill className="w-6 h-6 text-violet-400" />
                </div>
                <div className="absolute right-8 top-1/2 -translate-y-1/2 w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center animate-float-delayed">
                  <Shield className="w-6 h-6 text-amber-400" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-6 lg:px-12 py-24">
        <div className="max-w-4xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden">
            {/* Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-600 via-teal-600 to-emerald-600" />
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMtOS45NDEgMC0xOCA4LjA1OS0xOCAxOHM4LjA1OSAxOCAxOCAxOCAxOC04LjA1OSAxOC0xOC04LjA1OS0xOC0xOC0xOHptMCAzMmMtNy43MzIgMC0xNC02LjI2OC0xNC0xNHM2LjI2OC0xNCAxNC0xNCAxNCA2LjI2OCAxNCAxNC02LjI2OCAxNC0xNCAxNHoiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4xKSIvPjwvZz48L3N2Zz4=')] opacity-20" />
            
            <div className="relative px-8 lg:px-16 py-16 text-center">
              <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
                Ready to Transform Your Practice?
              </h2>
              <p className="text-white/80 text-lg mb-8 max-w-xl mx-auto">
                Join healthcare professionals using AI-powered clinical decision support
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link href="/register">
                  <Button 
                    size="lg"
                    className="bg-white text-teal-600 hover:bg-slate-100 shadow-xl"
                  >
                    Create Free Account
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
                <Link href="/login">
                  <Button 
                    size="lg"
                    variant="outline"
                    className="border-white/30 text-white hover:bg-white/10"
                  >
                    Sign In
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative px-6 lg:px-12 py-12 border-t border-slate-800">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-teal-500 flex items-center justify-center">
                <HeartPulse className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold">MedAssist</span>
            </div>
            <p className="text-sm text-slate-500 text-center">
              Clinical decision support tool. Not a substitute for professional medical advice.
            </p>
            <p className="text-sm text-slate-500">
              © 2024 MedAssist. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
