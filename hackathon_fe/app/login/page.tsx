"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { userApi } from "@/app/api/userApi";
import Image from "next/image";

type AuthFormData = {
  email: string;
  password: string;
};

export default function AuthPage() {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<AuthFormData>();
  const router = useRouter();

  // ✅ Kiểm tra nếu đã login (check user_id trong localStorage)
  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (userId) router.replace("/chat");
  }, [router]);

  const onSubmit = async (data: AuthFormData) => {
    setError(null);
    try {
      if (mode === "signup") {
        // --- SIGN UP ---
        await userApi.create({
          email: data.email,
          password: data.password,
          role_id: "1", // role mặc định cho user
        });
        alert("Tạo tài khoản thành công! Hãy đăng nhập.");
        setMode("login");
      } else {
        // --- LOGIN ---
        const user = await userApi.login(data.email, data.password);

        // ✅ Lưu user_id vào localStorage
        localStorage.setItem("user_id", String(user.id));
        localStorage.setItem("user_email", user.email);

        // ✅ Redirect sang chat
        router.replace("/chat");
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.message || "Có lỗi xảy ra, vui lòng thử lại.");
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute w-96 h-96 bg-primary/10 rounded-full blur-3xl -top-48 -left-48 animate-pulse"></div>
        <div className="absolute w-96 h-96 bg-primary/10 rounded-full blur-3xl -bottom-48 -right-48 animate-pulse delay-1000"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Image
            src="/logo1.png"
            alt="AlphaCode Logo"
            width={180}
            height={60}
            className="object-contain"
          />
        </div>

        {/* Card */}
        <div className="bg-card/80 backdrop-blur-xl border border-border rounded-2xl p-8 shadow-2xl">
          <h1 className="text-2xl font-semibold text-center text-foreground">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="text-sm text-muted-foreground text-center mt-2">
            {mode === "login"
              ? "Log in to continue to AlphaCode"
              : "Sign up to start chatting with AI"}
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 mt-6">
            <div>
              <label className="block text-sm text-neutral-300 mb-1">Email</label>
              <input
                className="w-full bg-neutral-700/40 border border-neutral-700 rounded px-3 py-2 text-neutral-100 outline-none"
                {...register("email", { required: true })}
                type="email"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm text-neutral-300 mb-1">Password</label>
              <input
                className="w-full bg-neutral-700/40 border border-neutral-700 rounded px-3 py-2 text-neutral-100 outline-none"
                {...register("password", { required: true })}
                type="password"
                placeholder="••••••••"
              />
            </div>

            {error && <p className="text-rose-400 text-sm">{error}</p>}

            <button
              type="submit"
              className="w-full bg-[#10a37f] text-white px-4 py-2 rounded-md hover:bg-[#0e8f6d] disabled:opacity-60"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? "Processing..."
                : mode === "login"
                  ? "Continue"
                  : "Sign up"}
            </button>
          </form>

          <div className="mt-4 text-center text-sm text-neutral-400">
            {mode === "login" ? (
              <>
                Don’t have an account?{" "}
                <button
                  className="text-white underline"
                  onClick={() => setMode("signup")}
                >
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  className="text-white underline"
                  onClick={() => setMode("login")}
                >
                  Sign in
                </button>
              </>
            )}
          </div>

          <p className="mt-6 text-xs text-neutral-500 text-center">
            By continuing, you agree to the Terms and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
}
