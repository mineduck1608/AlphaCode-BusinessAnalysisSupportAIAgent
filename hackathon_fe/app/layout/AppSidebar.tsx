"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useSidebar } from "../context/SidebarContext";
import { BoxIconLine } from "@/app/icon/index";
import { cn } from "@/app/lib/utils";

type NavItem = {
  name: string;
  icon: React.ReactNode;
  path: string;
};

const navItems: NavItem[] = [
  {
    icon: <BoxIconLine className="w-5 h-5" />,
    name: "Welcome",
    path: "/",
  },
];

const AppSidebar: React.FC = () => {
  const { isExpanded, isMobileOpen, isHovered, setIsHovered } = useSidebar();
  const pathname = usePathname();

  const isActive = (path: string) => path === pathname;

  return (
    <aside
      className={cn(
        "fixed mt-16 flex flex-col lg:mt-0 top-0 left-0 h-screen transition-all duration-300 ease-in-out z-50",
        "bg-background border-r border-border",
        isExpanded || isMobileOpen ? "w-[280px]" : isHovered ? "w-[280px]" : "w-[80px]",
        isMobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}
      onMouseEnter={() => !isExpanded && setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-border px-4">
        <Link href="/" className="flex items-center gap-2">
          {isExpanded || isHovered || isMobileOpen ? (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg">D</span>
              </div>
              <span className="font-bold text-lg text-foreground">Dashboard</span>
            </div>
          ) : (
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">D</span>
            </div>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((nav) => (
          <Link
            key={nav.name}
            href={nav.path}
            className={cn(
              "group relative flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200",
              isActive(nav.path)
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              !isExpanded && !isHovered && "lg:justify-center"
            )}
          >
            {/* Icon */}
            <span className="flex-shrink-0">
              {nav.icon}
            </span>

            {/* Text */}
            {(isExpanded || isHovered || isMobileOpen) && (
              <span className="flex-1 font-medium text-sm">{nav.name}</span>
            )}
          </Link>
        ))}
      </nav>

    </aside>
  );
};

export default AppSidebar;
