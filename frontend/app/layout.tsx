import type { Metadata } from 'next'
import { Plus_Jakarta_Sans, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import LandingBackground from '@/components/landing/LandingBackground'

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-ui',
  display: 'swap',
})

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-data',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'TaxChain - Crypto Tax & Portfolio P&L',
  description: 'Multi-wallet, multi-chain crypto tax calculations and portfolio tracking',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${jakarta.variable} ${jetbrains.variable}`}>
      <head>
        <script
          src="https://checkout.razorpay.com/v1/checkout.js"
          async
        ></script>
      </head>
      <body className="font-ui bg-void text-main">
        <LandingBackground />
        {children}
      </body>
    </html>
  )
}