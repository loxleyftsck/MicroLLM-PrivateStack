import Link from "next/link";
import { Star } from "lucide-react";
import { MicroLLMLogo } from "@/components/branding/MicroLLMLogo";
import { NAV_LINKS, REPO_URL } from "@/components/landing/content";
import { GithubMark } from "@/components/landing/GithubMark";
import { MobileMenu } from "@/components/landing/MobileMenu";

export function LandingNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-[#12161f] bg-[#080B12]/85 backdrop-blur-md">
      <nav className="mx-auto flex h-[68px] w-full max-w-[1280px] items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <MicroLLMLogo className="h-7 w-7" />
          <span className="text-[16px] font-semibold tracking-tight text-[#e8eaf0]">
            MicroLLM
          </span>
          <span className="hidden rounded-full border border-[#242a36] px-2 py-0.5 text-[10px] font-medium uppercase tracking-[0.1em] text-[#7a8194] sm:inline">
            PrivateStack
          </span>
        </Link>

        <ul className="hidden items-center gap-8 lg:flex">
          {NAV_LINKS.map(({ label, href }) => (
            <li key={href}>
              <a
                href={href}
                className="text-[14px] text-[#8a90a2] transition-colors hover:text-[#e8eaf0]"
              >
                {label}
              </a>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2.5">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="hidden h-[38px] items-center gap-2 rounded-full border border-[#242a36] px-4 text-[13px] text-[#c7ccd6] transition-colors hover:border-[#333a47] hover:bg-[#12151d] sm:inline-flex"
          >
            <GithubMark size={15} />
            <span className="flex items-center gap-1 text-[#8a90a2]">
              <Star size={12} />
              MIT
            </span>
          </a>
          <Link
            href="/login"
            className="inline-flex h-[38px] items-center rounded-full bg-[#6D3FD6] px-5 text-[13px] font-medium text-white transition-colors hover:bg-[#7B4EE0] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8B5CF6]"
          >
            Sign in
          </Link>

          <MobileMenu />
        </div>
      </nav>
    </header>
  );
}
