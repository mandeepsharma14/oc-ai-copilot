/**
 * Global app state using Zustand.
 */
import { create } from "zustand";
import type { StreamType } from "@/types";

interface AppState {
  streamType:    StreamType;
  currentTab:    string;
  domainFilter:  string | null;
  productFilter: string | null;
  sidebarOpen:   boolean;
  setStreamType:    (t: StreamType) => void;
  setCurrentTab:    (t: string) => void;
  setDomainFilter:  (d: string | null) => void;
  setProductFilter: (p: string | null) => void;
  toggleSidebar:    () => void;
}

export const useAppStore = create<AppState>((set) => ({
  streamType:    "internal",
  currentTab:    "chat",
  domainFilter:  null,
  productFilter: null,
  sidebarOpen:   true,
  setStreamType:    (streamType)    => set({ streamType }),
  setCurrentTab:    (currentTab)    => set({ currentTab }),
  setDomainFilter:  (domainFilter)  => set({ domainFilter }),
  setProductFilter: (productFilter) => set({ productFilter }),
  toggleSidebar:    ()              => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));
