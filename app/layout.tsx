import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import Link from "next/link"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "KetQat - The Home for Quantum Error Correction",
  description: "An open-source platform where researchers can share, discover, and collaborate on Quantum Error Correction (QEC) decoders, quantum circuits, and noise data.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-quantum-blue to-quantum-orange bg-clip-text text-transparent">
                KetQat
              </Link>
              <div className="flex items-center gap-6">
                <Link href="/decoders" className="text-sm font-medium hover:text-quantum-blue transition-colors">
                  Decoder Zoo
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main>{children}</main>
        <footer className="border-t mt-20 py-8">
          <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
            <p>KetQat - The Home for Quantum Error Correction</p>
            <p className="mt-2">Open-source platform for QEC decoders, circuits, and noise data</p>
          </div>
        </footer>
      </body>
    </html>
  )
}

