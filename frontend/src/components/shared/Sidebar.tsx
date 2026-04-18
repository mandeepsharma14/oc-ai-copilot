"use client";
import { clsx } from "clsx";
import { useAppStore } from "@/store/appStore";

interface NavItem {
  label:    string;
  key:      string;
  badge?:   string;
  icon:     React.ReactNode;
}

interface SidebarProps {
  navItems:  NavItem[];
  segments?: { name: string; count: string }[];
  userName:  string;
  userRole:  string;
  userInitials: string;
  accentColor:  string;    // hex e.g. "#1B2E4A"
  onSwitch?:    () => void;
  switchLabel?: string;
}

export function Sidebar({
  navItems, segments, userName, userRole, userInitials,
  accentColor, onSwitch, switchLabel,
}: SidebarProps) {
  const { currentTab, setCurrentTab } = useAppStore();

  return (
    <aside
      className="flex flex-col h-full text-white"
      style={{ background: accentColor }}
    >
      {/* Brand */}
      <div className="px-3 py-3 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center text-xs font-semibold">
            OC
          </div>
          <div>
            <div className="text-xs font-semibold">AI Copilot</div>
            <div className="text-[10px] text-white/50">Knowledge Assistant</div>
          </div>
        </div>
        {onSwitch && (
          <button
            onClick={onSwitch}
            className="text-[10px] text-white/50 bg-white/10 rounded px-2 py-1 hover:bg-white/20 transition"
          >
            {switchLabel || "Switch"}
          </button>
        )}
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto py-1">
        <p className="px-3 pt-3 pb-1 text-[9px] font-semibold text-white/30 tracking-widest uppercase">
          Navigation
        </p>
        {navItems.map((item) => (
          <button
            key={item.key}
            onClick={() => setCurrentTab(item.key)}
            className={clsx(
              "w-full flex items-center gap-2 px-3 py-1.5 mx-1 rounded-md text-xs transition",
              currentTab === item.key
                ? "bg-white/15 text-white"
                : "text-white/60 hover:bg-white/8 hover:text-white/90"
            )}
          >
            <span className="w-3 h-3 flex-shrink-0 opacity-75">{item.icon}</span>
            <span className="flex-1 text-left">{item.label}</span>
            {item.badge && (
              <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-white/15 text-white/70">
                {item.badge}
              </span>
            )}
          </button>
        ))}

        {segments && segments.length > 0 && (
          <>
            <p className="px-3 pt-3 pb-1 text-[9px] font-semibold text-white/30 tracking-widest uppercase">
              Domains
            </p>
            {segments.map((seg) => (
              <div
                key={seg.name}
                className="px-3 py-1.5 mx-1 rounded-md cursor-pointer hover:bg-white/8"
              >
                <div className="text-[11px] text-white/65">{seg.name}</div>
                <div className="text-[9px] text-white/30">{seg.count}</div>
              </div>
            ))}
          </>
        )}
      </div>

      {/* User footer */}
      <div className="px-3 py-2 border-t border-white/10 flex items-center gap-2">
        <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-[9px] font-semibold flex-shrink-0">
          {userInitials}
        </div>
        <div>
          <div className="text-[11px] font-medium">{userName}</div>
          <div className="text-[9px] text-white/45">{userRole}</div>
        </div>
      </div>
    </aside>
  );
}
