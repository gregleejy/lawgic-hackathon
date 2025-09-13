"use client";

import type React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Home() {
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      setResult(`You entered: "${inputText}"`);
      setIsSubmitted(true);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-slate-50/80 to-indigo-50/60 flex flex-col relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Enhanced gradient mesh background */}
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-100/30 via-transparent to-cyan-100/20"></div>
        <div className="absolute inset-0 bg-gradient-to-bl from-indigo-100/25 via-transparent to-blue-100/30"></div>

        {/* Animated gradient orbs with enhanced colors */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-blue-300/20 via-cyan-200/15 to-indigo-300/10 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute -bottom-40 -left-40 w-96 h-96 bg-gradient-to-tr from-indigo-300/20 via-blue-200/15 to-cyan-300/10 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "3s" }}
        ></div>
        <div
          className="absolute top-1/3 right-1/4 w-80 h-80 bg-gradient-to-r from-slate-200/15 via-blue-200/10 to-cyan-200/15 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "1.5s" }}
        ></div>
        <div
          className="absolute bottom-1/3 left-1/4 w-72 h-72 bg-gradient-to-l from-indigo-200/18 via-blue-100/12 to-slate-200/15 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "4s" }}
        ></div>

        {/* Enhanced geometric patterns */}
        <div className="absolute inset-0 opacity-[0.06]">
          <div
            className="absolute inset-0"
            style={{
              backgroundImage: `
              radial-gradient(circle at 25% 25%, rgba(59, 130, 246, 0.15) 1px, transparent 1px),
              radial-gradient(circle at 75% 75%, rgba(99, 102, 241, 0.12) 1px, transparent 1px),
              linear-gradient(rgba(59, 130, 246, 0.08) 1px, transparent 1px),
              linear-gradient(90deg, rgba(59, 130, 246, 0.08) 1px, transparent 1px)
            `,
              backgroundSize: "80px 80px, 60px 60px, 40px 40px, 40px 40px",
            }}
          ></div>
        </div>

        {/* Enhanced floating particles with varied sizes and colors */}
        <div
          className="absolute top-20 left-20 w-3 h-3 bg-gradient-to-br from-blue-400/50 to-cyan-500/40 rounded-full animate-float shadow-lg"
          style={{ animationDelay: "0s", animationDuration: "8s" }}
        ></div>
        <div
          className="absolute top-40 right-32 w-2 h-2 bg-gradient-to-br from-indigo-400/60 to-blue-500/45 rounded-full animate-float shadow-md"
          style={{ animationDelay: "2s", animationDuration: "6s" }}
        ></div>
        <div
          className="absolute bottom-32 left-40 w-2.5 h-2.5 bg-gradient-to-br from-cyan-400/55 to-blue-400/50 rounded-full animate-float shadow-lg"
          style={{ animationDelay: "4s", animationDuration: "7s" }}
        ></div>
        <div
          className="absolute top-60 left-1/3 w-1.5 h-1.5 bg-gradient-to-br from-slate-400/45 to-blue-400/40 rounded-full animate-float shadow-sm"
          style={{ animationDelay: "1s", animationDuration: "9s" }}
        ></div>
        <div
          className="absolute bottom-20 right-20 w-3 h-3 bg-gradient-to-br from-blue-300/50 to-indigo-400/45 rounded-full animate-float shadow-lg"
          style={{ animationDelay: "3s", animationDuration: "5s" }}
        ></div>
        <div
          className="absolute top-1/2 right-1/3 w-2 h-2 bg-gradient-to-br from-cyan-300/50 to-slate-400/40 rounded-full animate-float shadow-md"
          style={{ animationDelay: "5s", animationDuration: "8s" }}
        ></div>

        {/* Enhanced light rays with gradient effects */}
        <div className="absolute top-0 left-1/4 w-0.5 h-full bg-gradient-to-b from-transparent via-blue-300/25 to-transparent transform rotate-12 shadow-sm"></div>
        <div className="absolute top-0 right-1/3 w-0.5 h-full bg-gradient-to-b from-transparent via-cyan-300/20 to-transparent transform -rotate-12 shadow-sm"></div>
        <div className="absolute top-0 left-2/3 w-px h-full bg-gradient-to-b from-transparent via-indigo-300/15 to-transparent transform rotate-6"></div>

        {/* Enhanced corner accent elements */}
        <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-bl from-blue-200/20 via-cyan-100/15 to-transparent"></div>
        <div className="absolute bottom-0 left-0 w-40 h-40 bg-gradient-to-tr from-indigo-200/20 via-blue-100/15 to-transparent"></div>
        <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-slate-200/15 via-blue-100/10 to-transparent"></div>
        <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-cyan-200/15 via-indigo-100/10 to-transparent"></div>
      </div>

      <header className="w-full py-12 px-4 relative z-10">
        <div className="max-w-2xl mx-auto text-center">
          <img
            src="/logo.png"
            alt="Lawgic Logo"
            className="mx-auto w-64 h-auto"
            style={{ maxHeight: "180px" }}
          />
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center px-4 pb-16 relative z-10">
        <div className="w-full max-w-lg space-y-8">
          <Card className="backdrop-blur-md bg-white/70 border-2 border-blue-200/60 shadow-2xl hover:shadow-3xl transition-all duration-500 hover:scale-[1.02] hover:bg-white/80">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl text-slate-800 text-center">
                Enter Your Query
              </CardTitle>
              <CardDescription className="text-center text-base text-slate-600">
                Type your legal question or document text below
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-4">
                  <Input
                    type="text"
                    placeholder="Enter your legal query here..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    className="h-14 text-lg bg-white/60 border-2 border-blue-200/60 focus:border-blue-400 focus:bg-white/80 transition-all duration-300 shadow-inner placeholder:text-slate-500/60 text-slate-800"
                  />
                  <Button
                    type="submit"
                    size="lg"
                    className="w-full h-14 text-lg font-semibold bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-500 hover:from-blue-600 hover:via-indigo-600 hover:to-cyan-600 hover:scale-[1.02] transition-all duration-300 shadow-lg hover:shadow-xl relative overflow-hidden group text-white"
                    disabled={!inputText.trim()}
                  >
                    <span className="relative z-10">Analyze with lawgic</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card
            className={`backdrop-blur-md bg-blue-100/70 border-2 shadow-2xl transition-all duration-700 ${
              isSubmitted
                ? "opacity-100 translate-y-0 border-blue-400/70 animate-pulse-glow bg-blue-100/80"
                : "opacity-60 translate-y-4 border-blue-200/50"
            }`}
          >
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div
                  className={`w-3 h-3 rounded-full transition-colors duration-500 ${
                    isSubmitted
                      ? "bg-blue-500 animate-pulse shadow-sm"
                      : "bg-blue-300/40"
                  }`}
                ></div>
                <CardTitle className="text-xl text-blue-800">
                  Analysis Results
                </CardTitle>
              </div>
              <CardDescription className="text-blue-700">
                {isSubmitted
                  ? "Your query has been processed"
                  : "Results will appear here after submission"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="min-h-[80px] flex items-center">
                {result ? (
                  <div className="space-y-3">
                    <p className="text-blue-900 text-lg leading-relaxed font-medium">
                      {result}
                    </p>
                    <div className="flex items-center gap-2 text-sm text-blue-700">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-sm"></div>
                      <span>Processed by lawgic AI</span>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-3 text-blue-400">
                    <div className="w-8 h-8 border-2 border-blue-300/40 border-t-blue-500/60 rounded-full animate-spin opacity-50"></div>
                    <p className="italic">
                      Ready to analyze your legal query...
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <footer className="w-full py-8 px-4 text-center relative z-10 border-t border-blue-200/40 bg-white/40 backdrop-blur-md">
        <div className="max-w-2xl mx-auto">
          <p className="text-sm text-slate-700 mb-2">
            <span className="font-semibold text-blue-600">lawgic</span> -
            Intelligent Legal Analysis
          </p>
          <p className="text-xs text-slate-600/80">
            Built with Next.js, TailwindCSS, and shadcn/ui
          </p>
        </div>
      </footer>
    </div>
  );
}
