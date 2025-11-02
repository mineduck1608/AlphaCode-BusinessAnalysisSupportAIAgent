"use client";

import { useSidebar } from "@/app/context/SidebarContext";
import AppFooter from "@/app/icon/layout/AppFooter";
import AppHeader from "@/app/icon/layout/AppHeader";
import AppSidebar from "@/app/icon/layout/AppSidebar";
import Backdrop from "@/app/icon/layout/Backdrop";
import React from "react";


export default function LayoutWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isExpanded, isHovered, isMobileOpen } = useSidebar();

  // Dynamic class for main content margin based on sidebar state
  const mainContentMargin = isMobileOpen
    ? "ml-0"
    : isExpanded || isHovered
    ? "lg:ml-[290px]"
    : "lg:ml-[90px]";

  return (
    <div className="min-h-screen flex">
      {/* Sidebar and Backdrop */}
      <AppSidebar />
      <Backdrop />
      
      {/* Main Content Area */}
      <div
        className={`flex flex-1 flex-col transition-all duration-300 ease-in-out ${mainContentMargin}`}
      >
        {/* Header */}
        <AppHeader />
        
        {/* Page Content */}
        <main className="flex-1 p-4 mx-auto w-full max-w-[1920px] md:p-6">
          {children}
        </main>
        
        {/* Footer */}
        <AppFooter />
      </div>
    </div>
  );
}
