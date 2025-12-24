"use client";

import React from "react";
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
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: MessageSquare,
    title: "AI Medical Chat",
    description: "Evidence-based answers with citations from peer-reviewed literature",
    color: "bg-blue-500",
  },
  {
    icon: Pill,
    title: "Drug Interactions",
    description: "Real-time analysis of medication interactions and contraindications",
    color: "bg-emerald-500",
  },
  {
    icon: BookOpen,
    title: "Code Lookup",
    description: "Instant ICD-10 and SNOMED-CT code search and validation",
    color: "bg-violet-500",
  },
  {
    icon: Languages,
    title: "Medical Translation",
    description: "Accurate Japanese-English medical terminology translation",
    color: "bg-amber-500",
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
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <nav className="flex items-center justify-between px-6 lg:px-12 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <HeartPulse className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">
              Med<span className="text-blue-600">Assist</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" className="text-slate-600 hover:text-slate-900">
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/20">
                Get Started
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative px-6 lg:px-12 pt-20 lg:pt-32 pb-20 overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-100 rounded-full blur-3xl opacity-40 -translate-y-1/2 translate-x-1/3" />
          <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-cyan-100 rounded-full blur-3xl opacity-40 translate-y-1/2 -translate-x-1/3" />
        </div>

        <div className="max-w-6xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-8 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-sm font-medium">
            <Sparkles className="w-4 h-4" />
            <span>Powered by GPT-4o & RAG Technology</span>
          </div>

          {/* Main heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 mb-6">
            Clinical Intelligence
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              At Your Fingertips
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg lg:text-xl text-slate-600 max-w-2xl mx-auto mb-12 leading-relaxed">
            AI-powered clinical decision support for healthcare professionals. 
            Get evidence-based answers with citations from peer-reviewed medical literature.
          </p>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-6 lg:gap-12">
            {stats.map((stat) => (
              <div 
                key={stat.label} 
                className="text-center px-6 py-4 bg-white rounded-2xl shadow-sm border border-slate-100"
              >
                <div className="text-2xl font-bold text-slate-900 mb-1">{stat.value}</div>
                <div className="text-xs text-slate-500 uppercase tracking-wider">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 lg:px-12 py-24 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
              Comprehensive Clinical Tools
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto">
              Everything healthcare professionals need in one intelligent platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <Link 
                  key={feature.title} 
                  href="/login"
                  className="group"
                >
                  <div className="h-full p-8 rounded-2xl bg-white border border-slate-200 hover:border-blue-200 hover:shadow-lg hover:shadow-blue-500/5 transition-all duration-300 hover:-translate-y-1">
                    <div className={`w-14 h-14 rounded-xl ${feature.color} flex items-center justify-center mb-5 shadow-lg`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-slate-600 mb-4 leading-relaxed">
                      {feature.description}
                    </p>
                    <div className="flex items-center text-blue-600 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                      <span>Get started</span>
                      <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="px-6 lg:px-12 py-24">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-6">
                Built for Healthcare Professionals
              </h2>
              <p className="text-slate-600 mb-10 text-lg leading-relaxed">
                MedAssist combines cutting-edge AI with rigorous medical literature analysis 
                to provide accurate, reliable clinical decision support you can trust.
              </p>
              
              <div className="space-y-5">
                {benefits.map((benefit) => {
                  const Icon = benefit.icon;
                  return (
                    <div 
                      key={benefit.text}
                      className="flex items-center gap-4 group"
                    >
                      <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center group-hover:bg-blue-100 transition-colors">
                        <Icon className="w-5 h-5 text-blue-600" />
                      </div>
                      <span className="text-slate-700">{benefit.text}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Visual element */}
            <div className="relative hidden lg:block">
              <div className="relative aspect-square max-w-md mx-auto">
                {/* Background circles */}
                <div className="absolute inset-0 rounded-full border-2 border-slate-100" />
                <div className="absolute inset-8 rounded-full border-2 border-slate-100" />
                <div className="absolute inset-16 rounded-full border-2 border-slate-100" />
                
                {/* Center element */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="relative">
                    <div className="w-28 h-28 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-xl shadow-blue-500/30">
                      <Brain className="w-14 h-14 text-white" />
                    </div>
                  </div>
                </div>

                {/* Floating icons */}
                <div className="absolute top-4 left-1/2 -translate-x-1/2 w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-lg flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-blue-500" />
                </div>
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-emerald-500" />
                </div>
                <div className="absolute left-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-lg flex items-center justify-center">
                  <Pill className="w-6 h-6 text-violet-500" />
                </div>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 w-12 h-12 rounded-xl bg-white border border-slate-200 shadow-lg flex items-center justify-center">
                  <Shield className="w-6 h-6 text-amber-500" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 lg:px-12 py-24">
        <div className="max-w-4xl mx-auto">
          <div className="relative rounded-3xl overflow-hidden bg-gradient-to-br from-blue-600 to-cyan-600 p-12 lg:p-16 text-center">
            {/* Pattern overlay */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, white 1px, transparent 0)`,
                backgroundSize: '24px 24px'
              }} />
            </div>
            
            <div className="relative">
              <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">
                Ready to Transform Your Practice?
              </h2>
              <p className="text-blue-100 text-lg mb-8 max-w-xl mx-auto">
                Join healthcare professionals using AI-powered clinical decision support
              </p>
              <Link href="/register">
                <Button 
                  size="lg"
                  className="bg-white text-blue-600 hover:bg-blue-50 shadow-xl"
                >
                  Get Started
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 lg:px-12 py-12 border-t border-slate-200 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <HeartPulse className="w-4 h-4 text-white" />
              </div>
              <span className="font-semibold text-slate-900">MedAssist</span>
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
