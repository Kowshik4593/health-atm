'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  Building2,
  ScanLine,
  FileText,
  ShieldCheck,
  Clock,
  Languages,
  ArrowRight
} from 'lucide-react';

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false);
  const { scrollYProgress } = useScroll();

  // Transform values for hero section
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-black selection:bg-neutral-900 selection:text-white dark:selection:bg-white dark:selection:text-black">

      {/* Navigation */}
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
            ? 'bg-white/80 dark:bg-black/80 backdrop-blur-md border-b border-neutral-200 dark:border-neutral-800 py-4'
            : 'bg-transparent py-6'
          }`}
      >
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 rounded-xl bg-black dark:bg-white text-white dark:text-black flex items-center justify-center transition-transform group-hover:scale-105">
              <ScanLine size={24} strokeWidth={2.5} />
            </div>
            <span className="font-bold text-xl tracking-tight">LungAI</span>
          </Link>

          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-neutral-600 dark:text-neutral-400">
            <Link href="#features" className="hover:text-black dark:hover:text-white transition-colors">Features</Link>
            <Link href="#how-it-works" className="hover:text-black dark:hover:text-white transition-colors">How it Works</Link>
            <Link href="#testimonials" className="hover:text-black dark:hover:text-white transition-colors">Trust</Link>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="hidden sm:inline-flex">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Get Started</Button>
            </Link>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              style={{ opacity, scale }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <span className="inline-block py-1 px-3 rounded-full bg-neutral-100 dark:bg-neutral-900 text-neutral-600 dark:text-neutral-400 text-sm font-medium mb-6 border border-neutral-200 dark:border-neutral-800">
                Revolutionizing Rural Healthcare
              </span>
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-b from-neutral-900 to-neutral-500 dark:from-white dark:to-neutral-500 pb-2">
                Advanced Lung Diagnostics, <br />
                Right at Your Village.
              </h1>
              <p className="text-xl md:text-2xl text-neutral-500 dark:text-neutral-400 mb-10 max-w-2xl mx-auto leading-relaxed">
                Using state-of-the-art AI to detect lung abnormalities from CT scans in seconds.
                Accessible, affordable, and accurate.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/signup">
                  <Button size="lg" className="h-14 px-8 text-lg rounded-full w-full sm:w-auto">
                    Start Diagnosis <ArrowRight className="ml-2 w-5 h-5" />
                  </Button>
                </Link>
                <Link href="#how-it-works">
                  <Button variant="secondary" size="lg" className="h-14 px-8 text-lg rounded-full w-full sm:w-auto">
                    Learn More
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Abstract Background Shapes */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 -z-10 w-[800px] h-[800px] opacity-30 dark:opacity-20 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-tr from-blue-500 to-purple-500 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }} />
        </div>
      </section>

      {/* Features Grid (Bento) */}
      <section id="features" className="py-24 bg-white dark:bg-black relative">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Why Choose LungAI?</h2>
            <p className="text-lg text-neutral-500 max-w-2xl mx-auto">
              We combine cutting-edge technology with compassionate care to deliver world-class diagnostics.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="md:col-span-2 md:row-span-2 bg-gradient-to-br from-neutral-50 to-white dark:from-neutral-900 dark:to-neutral-950 flex flex-col justify-center items-center text-center p-12">
              <div className="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 rounded-2xl flex items-center justify-center mb-6 text-blue-600 dark:text-blue-400">
                <Building2 size={40} />
              </div>
              <h3 className="text-3xl font-bold mb-4">Village-Level Access</h3>
              <p className="text-lg text-neutral-500 max-w-lg mx-auto">
                No need to travel to the city. We bring hospital-grade diagnostics to your local health center,
                saving time and money for rural communities.
              </p>
            </Card>

            <Card className="flex flex-col items-start">
              <div className="w-12 h-12 bg-green-50 dark:bg-green-900/20 rounded-xl flex items-center justify-center mb-4 text-green-600 dark:text-green-400">
                <Clock size={24} />
              </div>
              <h3 className="text-xl font-bold mb-2">Instant Results</h3>
              <p className="text-neutral-500">Get detailed reports in under 5 minutes, powered by our optimized AI engine.</p>
            </Card>

            <Card className="flex flex-col items-start">
              <div className="w-12 h-12 bg-purple-50 dark:bg-purple-900/20 rounded-xl flex items-center justify-center mb-4 text-purple-600 dark:text-purple-400">
                <Languages size={24} />
              </div>
              <h3 className="text-xl font-bold mb-2">Multi-Language</h3>
              <p className="text-neutral-500">Reports rendered in your local language for better understanding and care.</p>
            </Card>

            <Card className="md:col-span-3 flex flex-col md:flex-row items-center gap-8 bg-neutral-900 text-white dark:bg-white dark:text-black">
              <div className="flex-1 text-left">
                <div className="flex items-center gap-2 mb-4 text-neutral-400 dark:text-neutral-600 font-medium">
                  <ShieldCheck size={20} />
                  <span>Privacy First</span>
                </div>
                <h3 className="text-3xl font-bold mb-4">Secure & Confidential</h3>
                <p className="text-neutral-400 dark:text-neutral-600 text-lg mb-8">
                  Your health data is encrypted and stored locally. We adhere to the highest standards of data privacy.
                </p>
              </div>
              <div className="w-full md:w-1/3 aspect-video bg-neutral-800 dark:bg-neutral-100 rounded-xl overflow-hidden relative group">
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-neutral-600 dark:text-neutral-400 font-medium">Encrypted Vault</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-24 bg-neutral-50 dark:bg-black border-t border-neutral-200 dark:border-neutral-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Simple 3-Step Process</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-12 relative">
            <div className="hidden md:block absolute top-12 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-neutral-300 dark:via-neutral-700 to-transparent z-0" />

            {[
              { icon: Building2, title: "Visit Center", desc: "Walk into your nearest village health center." },
              { icon: ScanLine, title: "Get Scanned", desc: "Quick 5-minute chest CT scan." },
              { icon: FileText, title: "Receive Report", desc: "Instant AI analysis reviewed by doctors." }
            ].map((step, i) => (
              <div key={i} className="relative z-10 flex flex-col items-center text-center">
                <div className="w-24 h-24 bg-white dark:bg-neutral-900 rounded-full border-4 border-neutral-50 dark:border-black shadow-xl flex items-center justify-center mb-8">
                  <step.icon size={32} className="text-black dark:text-white" />
                </div>
                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                <p className="text-neutral-500">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 bg-black text-white dark:bg-white dark:text-black text-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] mix-blend-overlay"></div>
        <div className="max-w-4xl mx-auto px-6 relative z-10">
          <h2 className="text-4xl md:text-6xl font-bold mb-8 tracking-tight">Ready to prioritize your health?</h2>
          <p className="text-xl text-neutral-400 dark:text-neutral-600 mb-10">Join thousands of patients receiving world-class care.</p>
          <Link href="/signup">
            <Button size="lg" className="bg-white text-black hover:bg-neutral-200 dark:bg-black dark:text-white dark:hover:bg-neutral-800 h-16 px-10 text-xl rounded-full">
              Get Started Now
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-white dark:bg-black border-t border-neutral-200 dark:border-neutral-800">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-black dark:bg-white flex items-center justify-center text-white dark:text-black">
              <ScanLine size={18} />
            </div>
            <span className="font-bold text-lg">LungAI</span>
          </div>
          <p className="text-neutral-500 text-sm">© 2025 AI Lung Health. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}