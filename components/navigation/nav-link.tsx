"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
}

export const NavLink = ({ href, children }: NavLinkProps) => {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <Link
      href={href}
      className={cn(
        "relative px-3 py-2 text-lg font-medium transition-colors duration-200 hover:text-primary",
        isActive ? "text-primary" : "text-gray-700 dark:text-gray-300"
      )}
    >
      {children}
      <span
        className={cn(
          "absolute bottom-0 left-0 h-0.5 w-full transform-gpu transition-all duration-300 ease-in-out",
          isActive ? "bg-primary opacity-100" : "bg-transparent opacity-0"
        )}
      />
    </Link>
  );
};
