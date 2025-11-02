import { Outfit } from 'next/font/google';
import type { Metadata } from 'next';
import './globals.css';

import { SidebarProvider } from '../app/context/SidebarContext';
import { Toaster } from 'sonner';

const outfit = Outfit({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: 'AlphaCode - AI Coding Assistant',
  description: 'An AI-powered coding assistant designed to help you write better code faster',
  icons: {
    icon: '/logo2.png',
    apple: '/logo2.png',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={outfit.className}>
        <SidebarProvider>
          {children}
        </SidebarProvider>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
