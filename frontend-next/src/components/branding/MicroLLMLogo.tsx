import Image from "next/image";

export function MicroLLMLogo({ className = "h-8 w-8" }: { className?: string }) {
  return (
    <Image
      src="/microllm-mark.png"
      alt="MicroLLM"
      width={362}
      height={368}
      priority
      className={`${className} object-contain`}
    />
  );
}
