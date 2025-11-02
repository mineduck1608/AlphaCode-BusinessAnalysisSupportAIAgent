"use client";
  
import React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useSidebar } from "../context/SidebarContext";
import { BoxIconLine } from "@/app/icon/index";
import { cn } from "@/app/lib/utils";
import { Plus, MessageSquare, Settings, LogOut } from "lucide-react";
import { getCurrentUser, mockLogout } from "@/app/lib/authMock";

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
//   {
//     icon: <BoxIconLine className="w-5 h-5" />,
//     name: "Homepage",
//     path: "/chat",
//   },
];

const AppSidebar: React.FC = () => {
  const { isExpanded, isMobileOpen, isHovered, setIsHovered } = useSidebar();
  const pathname = usePathname();
  const router = useRouter();
  const user = getCurrentUser();

  const isActive = (path: string) => path === pathname;
  const isChatPage = pathname.startsWith('/chat');

  const handleLogout = () => {
    mockLogout();
    router.push('/login');
  };

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
        <Link href="/" className="flex items-center gap-3">
          {isExpanded || isHovered || isMobileOpen ? (
            <div className="flex items-center gap-3">
              <Image 
                src="/logo1.png" 
                alt="AlphaCode Logo" 
                width={50} 
                height={50}
                className="w-30 h-30 object-contain"
              />
            </div>
          ) : (
            <Image 
              src="/logo1.png" 
              alt="AlphaCode Logo" 
              width={50} 
              height={50}
              className="w-8 h-8 object-contain"
            />
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {/* New Chat Button */}
        <Link
          href="/chat"
          className={cn(
            "group flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200",
            "bg-primary text-primary-foreground hover:opacity-90",
            !isExpanded && !isHovered && "lg:justify-center"
          )}
        >
          <Plus className="w-5 h-5 flex-shrink-0" />
          {(isExpanded || isHovered || isMobileOpen) && (
            <span className="flex-1 font-medium text-sm">New Chat</span>
          )}
        </Link>

        {/* Separator */}
        <div className="py-2">
          <div className="border-t border-border"></div>
        </div>

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

        {/* Chat History Section - Only show on chat pages */}
        {isChatPage && (isExpanded || isHovered || isMobileOpen) && (
          <>
            <div className="py-2">
              <div className="border-t border-border"></div>
            </div>
            <div className="space-y-1">
              <div className="px-3 py-2 text-xs text-muted-foreground font-medium">Recent Chats</div>
              <button className="w-full px-3 py-2 rounded-lg hover:bg-accent text-left text-sm text-muted-foreground hover:text-accent-foreground transition-colors flex items-center gap-2">
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">Project ideas</span>
              </button>
              <button className="w-full px-3 py-2 rounded-lg hover:bg-accent text-left text-sm text-muted-foreground hover:text-accent-foreground transition-colors flex items-center gap-2">
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">Study notes</span>
              </button>
              <button className="w-full px-3 py-2 rounded-lg hover:bg-accent text-left text-sm text-muted-foreground hover:text-accent-foreground transition-colors flex items-center gap-2">
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="truncate">Recipes</span>
              </button>
            </div>
          </>
        )}
      </nav>

      {/* User Section - Only show when expanded/hovered */}
      {user && (isExpanded || isHovered || isMobileOpen) && (
        <div className="p-4 border-t border-border space-y-3">
          <div className="text-xs text-muted-foreground px-2">{user.email}</div>
          <div className="flex gap-2">
            <button 
              className="flex-1 flex items-center justify-center gap-2 text-sm text-muted-foreground hover:text-foreground px-3 py-2 rounded-lg hover:bg-accent transition-colors"
              onClick={() => alert("Settings (mock)")}
            >
              <Settings size={16} />
              <span className="text-xs">Settings</span>
            </button>
            <button 
              className="flex items-center justify-center gap-2 text-sm text-rose-500 hover:text-rose-600 px-3 py-2 rounded-lg hover:bg-accent transition-colors"
              onClick={handleLogout}
            >
              <LogOut size={16} />
              <span className="text-xs">Logout</span>
            </button>
          </div>
        </div>
      )}

      {/* User Icon Only - Show when collapsed and user exists */}
      {user && !isExpanded && !isHovered && !isMobileOpen && (
        <div className="p-4 border-t border-border">
          <button 
            className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-accent transition-colors"
            title={user.email}
          >
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <span className="text-primary-foreground font-medium text-sm">
                {user.email.charAt(0).toUpperCase()}
              </span>
            </div>
          </button>
        </div>
      )}
    </aside>
  );
};

export default AppSidebar;
