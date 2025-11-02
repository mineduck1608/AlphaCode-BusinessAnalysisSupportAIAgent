"use client";

import React, { useEffect } from "react";
import ChatLayout from "@/app/components/chat/ChatLayout";
import { getCurrentUser } from "@/app/lib/authMock";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const router = useRouter();
  
  useEffect(() => {
    const u = getCurrentUser();
    if (!u) router.replace("/login");
  }, [router]);

  // Return ChatLayout in a full-screen container, bypassing the default layout wrapper
  return (
    <div className="fixed inset-0 z-50">
      <ChatLayout />
    </div>
  );
}
