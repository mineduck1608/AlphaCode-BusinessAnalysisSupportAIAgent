import type { Metadata } from "next";
import React from "react";
import { BoxIconLine, ArrowUpIcon } from "@/icons";

export const metadata: Metadata = {
  title: "Welcome - Dashboard",
  description: "Modern dashboard application",
};

export default function WelcomePage() {
  return (
    <div className="min-h-[calc(100vh-200px)] flex flex-col items-center justify-center">
      {/* Hero Section */}
      <div className="max-w-4xl mx-auto text-center space-y-8 px-4">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="w-24 h-24 bg-primary rounded-2xl flex items-center justify-center shadow-lg">
            <BoxIconLine className="w-12 h-12 text-primary-foreground" />
          </div>
        </div>

        {/* Title */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground">
            Welcome to Dashboard
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            A modern, minimal dashboard designed with simplicity and elegance.
            Built with Next.js, Tailwind CSS, and shadcn/ui.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <button className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity">
            Get Started
          </button>
          <button className="px-8 py-3 bg-secondary text-secondary-foreground rounded-lg font-medium hover:bg-accent transition-colors">
            Learn More
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16">
          {/* Feature 1 */}
          <div className="p-6 rounded-xl border border-border bg-card hover:shadow-lg transition-shadow">
            <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
              <ArrowUpIcon className="w-6 h-6 text-primary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-card-foreground mb-2">
              Modern Design
            </h3>
            <p className="text-sm text-muted-foreground">
              Clean and minimalist interface with focus on user experience
            </p>
          </div>

          {/* Feature 2 */}
          <div className="p-6 rounded-xl border border-border bg-card hover:shadow-lg transition-shadow">
            <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
              <BoxIconLine className="w-6 h-6 text-primary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-card-foreground mb-2">
              Fully Responsive
            </h3>
            <p className="text-sm text-muted-foreground">
              Works seamlessly on desktop, tablet, and mobile devices
            </p>
          </div>

          {/* Feature 3 */}
          <div className="p-6 rounded-xl border border-border bg-card hover:shadow-lg transition-shadow">
            <div className="w-12 h-12 bg-primary rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-card-foreground mb-2">
              Fast Performance
            </h3>
            <p className="text-sm text-muted-foreground">
              Built with Next.js for optimal speed and performance
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-16 border-t border-border">
          <div className="text-center">
            <div className="text-3xl font-bold text-foreground">100%</div>
            <div className="text-sm text-muted-foreground mt-1">Responsive</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-foreground">24/7</div>
            <div className="text-sm text-muted-foreground mt-1">Available</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-foreground">∞</div>
            <div className="text-sm text-muted-foreground mt-1">Possibilities</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-foreground">⚡</div>
            <div className="text-sm text-muted-foreground mt-1">Fast</div>
          </div>
        </div>
      </div>
    </div>
  );
}
