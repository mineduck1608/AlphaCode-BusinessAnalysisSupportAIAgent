    import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Login - AlphaCode",
  description: "Sign in to your AlphaCode account",
};

export default function LoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
