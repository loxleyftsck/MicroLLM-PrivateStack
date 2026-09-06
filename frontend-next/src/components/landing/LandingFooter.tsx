import Link from "next/link";
import { MicroLLMLogo } from "@/components/branding/MicroLLMLogo";
import { REPO_URL } from "@/components/landing/content";

const LINKS = [
  { label: "Documentation", href: `${REPO_URL}/tree/main/docs`, external: true },
  { label: "Changelog", href: `${REPO_URL}/blob/main/CHANGELOG.md`, external: true },
  { label: "Security", href: `${REPO_URL}/blob/main/SECURITY.md`, external: true },
  { label: "Sign in", href: "/login", external: false },
];

export function LandingFooter() {
  return (
    <footer className="mx-auto w-full max-w-[1280px] px-4 pb-10 sm:px-6">
      <div className="flex flex-col gap-6 border-t border-[#12161f] pt-8 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2.5">
          <MicroLLMLogo className="h-6 w-6" />
          <span className="text-[14px] font-semibold text-[#c7ccd6]">
            MicroLLM-PrivateStack
          </span>
          <span className="text-[12px] text-[#565d6e]">v1.2.0 · MIT</span>
        </div>

        <ul className="flex flex-wrap items-center gap-x-6 gap-y-2">
          {LINKS.map(({ label, href, external }) => (
            <li key={label}>
              {external ? (
                <a
                  href={href}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[13px] text-[#8a90a2] transition-colors hover:text-[#e8eaf0]"
                >
                  {label}
                </a>
              ) : (
                <Link
                  href={href}
                  className="text-[13px] text-[#8a90a2] transition-colors hover:text-[#e8eaf0]"
                >
                  {label}
                </Link>
              )}
            </li>
          ))}
        </ul>
      </div>
    </footer>
  );
}
