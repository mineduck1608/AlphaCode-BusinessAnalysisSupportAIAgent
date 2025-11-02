import { Outfit } from 'next/font/google';
import './globals.css';

import { SidebarProvider } from '../app/context/SidebarContext';
import LayoutWrapper from '@/app/components/common/LayoutWrapper';

const outfit = Outfit({
  subsets: ["latin"],
});

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
