import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LancerAI",
  description: "Trợ lý sự nghiệp — giao diện web (Next.js).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
