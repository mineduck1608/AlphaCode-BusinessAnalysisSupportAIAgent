// components/auth/LoginForm.tsx
"use client";

import React, { useState } from "react";
import { mockLogin } from "@/app/lib/authMock";

export default function LoginForm({ onSuccess }: { onSuccess?: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);
    if (!email || !password) return setErr("Please provide email and password.");
    setLoading(true);
    try {
      await mockLogin(email, password);
      onSuccess?.();
    } catch (e) {
      setErr("Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-neutral-800/60 rounded-2xl p-8 shadow-md">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-semibold">Welcome back</h1>
        <p className="text-sm text-neutral-400 mt-2">Log in to continue to ChatGPT Clone</p>
      </div>

      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm text-neutral-300 mb-1">Email</label>
          <input
            className="w-full bg-neutral-700/40 border border-neutral-700 rounded px-3 py-2 text-neutral-100 outline-none"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label className="block text-sm text-neutral-300 mb-1">Password</label>
          <input
            className="w-full bg-neutral-700/40 border border-neutral-700 rounded px-3 py-2 text-neutral-100 outline-none"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            placeholder="••••••••"
          />
        </div>

        {err && <div className="text-rose-400 text-sm">{err}</div>}

        <button
          type="submit"
          className="w-full bg-[#10a37f] text-white px-4 py-2 rounded-md hover:bg-[#0e8f6d] disabled:opacity-60"
          disabled={loading}
        >
          {loading ? "Signing in..." : "Continue"}
        </button>
      </form>

      <div className="mt-4 text-center text-sm text-neutral-400">
        Don’t have an account? <button className="text-white underline" onClick={() => alert("This is a mock signup flow.")}>Sign up</button>
      </div>

      <p className="mt-6 text-xs text-neutral-500 text-center">By continuing, you agree to the Terms and Privacy Policy (mock).</p>
    </div>
  );
}
