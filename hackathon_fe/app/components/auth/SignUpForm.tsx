"use client";

import React, { useState } from "react";
import { userApi } from "@/app/api";

export default function SignupForm({ onSuccess }: { onSuccess?: () => void }) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null);

    if (!email || !password || !name) return setErr("Please fill all fields.");
    if (password !== confirm) return setErr("Passwords do not match.");

    setLoading(true);
    try {
      // dùng chung endpoint login (tự tạo user nếu chưa có)
      const user = await userApi.login(email, password, 2);
      console.log("✅ User created or logged in:", user);

      // Lưu lại thông tin
      localStorage.setItem("userId", String(user.id));
      localStorage.setItem("userEmail", user.email);

      alert("Signup successful! Welcome aboard 🚀");
      onSuccess?.();
    } catch (e: any) {
      console.error(e);
      setErr(e.response?.data?.message || "Signup failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-neutral-800/60 rounded-2xl p-8 shadow-md">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-semibold">Create your account</h1>
        <p className="text-sm text-neutral-400 mt-2">
          Sign up to start using ChatGPT Clone
        </p>
      </div>

      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm text-neutral-300 mb-1">Full name</label>
          <input
            className="w-full bg-neutral-700/40 border border-neutral-700 rounded px-3 py-2 text-neutral-100 outline-none"
            value={name}
            onChange={(e) => setName(e.target.value)}
            type="text"
            placeholder="John Doe"
          />
        </div>

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

        <div>
          <label className="block text-sm text-neutral-300 mb-1">
            Confirm Password
          </label>
          <input
            className="w-full bg-neutral-700/40 border border-neutral-700 rounded px-3 py-2 text-neutral-100 outline-none"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
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
          {loading ? "Creating..." : "Sign up"}
        </button>
      </form>

      <div className="mt-4 text-center text-sm text-neutral-400">
        Already have an account?{" "}
        <a href="/login" className="text-white underline">
          Log in
        </a>
      </div>
    </div>
  );
}
