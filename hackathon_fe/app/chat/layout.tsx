import LayoutWrapper from "@/app/components/common/LayoutWrapper";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <LayoutWrapper>{children}</LayoutWrapper>;
}
