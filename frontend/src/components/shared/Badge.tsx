import { clsx } from "clsx";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "blue" | "green" | "amber" | "gray" | "red";
  size?:    "sm" | "xs";
}

const variants = {
  blue:  "bg-blue-50  text-blue-800  border-blue-200",
  green: "bg-green-50 text-green-800 border-green-200",
  amber: "bg-amber-50 text-amber-800 border-amber-200",
  gray:  "bg-gray-50  text-gray-700  border-gray-200",
  red:   "bg-red-50   text-red-800   border-red-200",
};

export function Badge({ children, variant = "blue", size = "sm" }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border font-medium",
        size === "xs" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs",
        variants[variant]
      )}
    >
      {children}
    </span>
  );
}
