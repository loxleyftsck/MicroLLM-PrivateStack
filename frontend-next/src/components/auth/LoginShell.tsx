import { BrandPanel } from "@/components/auth/BrandPanel";
import { LoginForm } from "@/components/auth/LoginForm";
import { ConnectionStatus } from "@/components/auth/ConnectionStatus";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { MicroLLMLogo } from "@/components/branding/MicroLLMLogo";

export function LoginShell() {
  return (
    <main className="relative flex min-h-screen w-full items-center justify-center overflow-hidden bg-[#080B12] px-4 py-10 sm:px-6">
      <div
        className="pointer-events-none absolute inset-0 [background:radial-gradient(60%_50%_at_50%_35%,rgba(93,58,196,0.10),rgba(20,25,45,0.06)_45%,transparent_75%)]"
        aria-hidden="true"
      />

      <div className="relative z-10 flex w-full max-w-[1360px] min-h-0 md:min-h-[760px] flex-col overflow-hidden rounded-none border-0 sm:rounded-[16px] sm:border sm:border-[#1a1f2b] shadow-[0_20px_60px_-20px_rgba(0,0,0,0.6)] md:flex-row">
        <BrandPanel />

        <div className="flex w-full md:w-[60%] flex-col bg-[#0B0E14] px-5 py-8 sm:px-10 sm:py-10 md:px-16 md:py-14 lg:px-20">
          <div className="mb-8 flex items-center justify-between md:hidden">
            <div className="flex items-center gap-2">
              <MicroLLMLogo className="h-6 w-6" />
              <span className="text-[15px] font-semibold text-[#e8eaf0]">
                MicroLLM
              </span>
            </div>
            <ThemeToggle />
          </div>

          <div className="hidden justify-end md:flex">
            <ThemeToggle />
          </div>

          <div className="flex flex-1 items-center">
            <div className="w-full max-w-[620px] mx-auto md:mx-0">
              <LoginForm />
            </div>
          </div>

          <p className="mb-6 text-center text-[12px] text-[#565d6e] md:hidden">
            Private AI · Runs locally · No cloud traffic
          </p>

          <ConnectionStatus />
        </div>
      </div>
    </main>
  );
}
