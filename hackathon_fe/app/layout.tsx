import { Outfit } from 'next/font/google';
import type { Metadata } from 'next';
import './globals.css';

import { SidebarProvider } from '../app/context/SidebarContext';
import LayoutWrapper from '@/app/components/common/LayoutWrapper';

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
          <LayoutWrapper>{children}</LayoutWrapper>
        </SidebarProvider>
      </body>
    </html>
  );
}
