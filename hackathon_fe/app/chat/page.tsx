"use client";

import React, { useEffect } from "react";
import ChatLayout from "@/app/components/chat/ChatLayout";
import { getCurrentUserId } from "../lib/authMock";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const router = useRouter();

  useEffect(() => {
    const userId = getCurrentUserId();
    if (!userId) router.replace("/login");
  }, [router]);

  return (
    <div className="fixed inset-0 z-50">
      <ChatLayout />
    </div>
  );
}
