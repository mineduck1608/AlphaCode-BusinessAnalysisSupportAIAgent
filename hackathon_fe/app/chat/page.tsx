"use client";

import React, { Suspense, useEffect } from "react";
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
      <Suspense fallback={<div className="flex items-center justify-center h-full text-white">Loading...</div>}>
        <ChatLayout />
      </Suspense>
    </div>
  );
}
