import type { Metadata } from "next";
import "./globals.css";


export const metadata: Metadata = {
  title: "AI Lung Health - Premium Diagnostics",
  description: "Advanced AI-powered lung health analysis for everyone.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body
        className="antialiased font-sans text-neutral-900 bg-neutral-50 dark:bg-black dark:text-white"
        style={{ fontFamily: "'Inter', sans-serif" }}
      >
        {children}
      </body>
    </html>
  );
}
