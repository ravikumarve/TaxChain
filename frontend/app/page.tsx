import Navbar from '@/components/landing/Navbar'
import HeroSection from '@/components/landing/HeroSection'
import BentoMatrix from '@/components/landing/BentoMatrix'
import ApiSection from '@/components/landing/ApiSection'
import ArchitectureSection from '@/components/landing/ArchitectureSection'
import PricingSection from '@/components/landing/PricingSection'
import Footer from '@/components/landing/Footer'

/**
 * LandingPage — Composes all marketing sections over the dark void background.
 * Background layers (LedgerCanvas, DotMatrix, AmbientCore) are rendered by
 * LandingBackground in the root layout.
 */
export default function LandingPage() {
  return (
    <>
      <Navbar />
      <HeroSection />
      <BentoMatrix />
      <ApiSection />
      <ArchitectureSection />
      <PricingSection />
      <Footer />
    </>
  )
}
