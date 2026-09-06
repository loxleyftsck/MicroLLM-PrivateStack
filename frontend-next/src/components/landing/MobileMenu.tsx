"use client";

import Link from "next/link";
import { Menu, Star, X } from "lucide-react";
import { useEffect, useId, useState } from "react";
import { NAV_LINKS, REPO_URL } from "@/components/landing/content";
import { GithubMark } from "@/components/landing/GithubMark";

/**
 * The nav links collapse below `lg`, so this reveals them behind a hamburger.
 * Renders the trigger inline and drops the panel out of the sticky header,
 * which is the nearest positioned ancestor.
 */
export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const panelId = useId();

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        setOpen(false);
      }
    }

    // The panel sits over the page, so freeze the scroll behind it. The lock is
    // scoped to the breakpoint that shows the panel, so a viewport that grows
    // past `lg` releases it in CSS even if the listener below never fires.
    document.body.classList.add("max-lg:overflow-hidden");
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.classList.remove("max-lg:overflow-hidden");
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  // A resize past the breakpoint reveals the real nav, so drop the panel.
  useEffect(() => {
    if (!open) return;
    const query = window.matchMedia("(min-width: 1024px)");
    function handleChange(e: MediaQueryListEvent) {
      if (e.matches) setOpen(false);
    }
    query.addEventListener("change", handleChange);
    return () => query.removeEventListener("change", handleChange);
  }, [open]);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={open ? "Close menu" : "Open menu"}
        className="inline-flex h-[38px] w-[38px] items-center justify-center rounded-full border border-[#242a36] text-[#c7ccd6] transition-colors hover:border-[#333a47] hover:bg-[#12151d] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#8B5CF6] lg:hidden"
      >
        {open ? <X size={17} /> : <Menu size={17} />}
      </button>

      {open ? (
        <>
          <button
            type="button"
            tabIndex={-1}
            aria-label="Close menu"
            onClick={() => setOpen(false)}
            className="fixed inset-x-0 bottom-0 top-[68px] z-40 cursor-default bg-black/50 backdrop-blur-sm lg:hidden"
          />

          <div
            id={panelId}
            className="absolute inset-x-0 top-full z-50 border-b border-[#12161f] bg-[#0B0E14] px-4 pb-5 pt-2 shadow-[0_24px_50px_-24px_rgba(0,0,0,0.9)] sm:px-6 lg:hidden"
          >
            <ul className="flex flex-col">
              {NAV_LINKS.map(({ label, href }) => (
                <li key={href}>
                  <a
                    href={href}
                    onClick={() => setOpen(false)}
                    className="block border-b border-[#12161f] py-3.5 text-[15px] text-[#c7ccd6] transition-colors hover:text-[#e8eaf0]"
                  >
                    {label}
                  </a>
                </li>
              ))}
            </ul>

            <div className="mt-5 flex flex-col gap-2.5">
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                onClick={() => setOpen(false)}
                className="inline-flex h-[44px] items-center justify-center gap-2 rounded-full border border-[#242a36] px-4 text-[14px] text-[#c7ccd6] transition-colors hover:border-[#333a47] hover:bg-[#12151d]"
              >
                <GithubMark size={15} />
                Star on GitHub
                <span className="flex items-center gap-1 text-[#8a90a2]">
                  <Star size={12} />
                  MIT
                </span>
              </a>
              <Link
                href="/login"
                onClick={() => setOpen(false)}
                className="inline-flex h-[44px] items-center justify-center rounded-full bg-[#6D3FD6] px-5 text-[14px] font-medium text-white transition-colors hover:bg-[#7B4EE0]"
              >
                Open the workspace
              </Link>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}
