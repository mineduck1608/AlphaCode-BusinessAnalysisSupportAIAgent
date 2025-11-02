// app/login/page.tsx
"use client";

import React, { useState } from "react";
import LoginForm from "@/app/components/auth/LoginForm";
import { useRouter } from "next/navigation";
import { getCurrentUser } from "@/app/lib/authMock";

export default function LoginPage() {
  const router = useRouter();
  // if already logged in, redirect to chat
  React.useEffect(() => {
    const u = getCurrentUser();
    if (u) router.replace("/chat");
  }, [router]);

  return (
    <div className="min-h-screen bg-neutral-900 text-neutral-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <LoginForm onSuccess={() => router.replace("/chat")} />
      </div>
    </div>
  );
}
