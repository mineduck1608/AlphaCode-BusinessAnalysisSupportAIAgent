// app/chat/page.tsx
"use client";

import React, { useEffect } from "react";
import ChatLayout from "@/components/chat/ChatLayout";
import { getCurrentUser } from "@/lib/authMock";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const router = useRouter();
  useEffect(() => {
    const u = getCurrentUser();
    if (!u) router.replace("/login");
  }, [router]);

  return <ChatLayout />;
}
