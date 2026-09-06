import { LandingNav } from "@/components/landing/LandingNav";
import { Hero } from "@/components/landing/Hero";
import { OneLine } from "@/components/landing/OneLine";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Capabilities } from "@/components/landing/Capabilities";
import { Metrics } from "@/components/landing/Metrics";
import { Comparison } from "@/components/landing/Comparison";
import { Faq } from "@/components/landing/Faq";
import { FinalCta } from "@/components/landing/FinalCta";
import { LandingFooter } from "@/components/landing/LandingFooter";

export function LandingPage() {
  return (
    <div className="flex min-h-screen w-full flex-col bg-[#080B12]">
      <LandingNav />

      <main className="flex flex-1 flex-col gap-5 px-2 py-5 sm:px-6 sm:py-8">
        <Hero />
        <OneLine />
        <HowItWorks />
        <Capabilities />
        <Metrics />
        <Comparison />
        <Faq />
        <FinalCta />
      </main>

      <LandingFooter />
    </div>
  );
}
