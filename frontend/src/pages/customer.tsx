"use client";
import type { NextPage } from "next";
import Head from "next/head";
import { Sidebar }      from "@/components/shared/Sidebar";
import { ChatWindow }   from "@/components/chat/ChatWindow";
import { KnowledgeBase }from "@/components/kb/KnowledgeBase";
import { useAppStore }  from "@/store/appStore";

const NAV_ITEMS = [
  {
    key: "chat", label: "Product Advisor",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  },
  {
    key: "kb", label: "Product catalog", badge: "2,097",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>,
  },
];

const SEGMENTS = [
  { name: "Roofing shingles & accessories",  count: "Duration · Oakridge · WeatherBond" },
  { name: "Insulation products",             count: "EcoTouch · Thermafiber · ProPink" },
  { name: "Composites & glass fiber",        count: "WindStrand · AdvantexAQ" },
  { name: "Doors & entry systems",           count: "Belleville · fiberglass · steel" },
];

const Customer: NextPage = () => {
  const { currentTab } = useAppStore();

  return (
    <>
      <Head>
        <title>OC Product Advisor — Customer Portal</title>
        <meta name="description" content="Owens Corning Customer Product Knowledge Assistant" />
      </Head>

      <div className="flex h-screen overflow-hidden bg-gray-50">
        <div className="w-52 flex-shrink-0">
          <Sidebar
            navItems={NAV_ITEMS}
            segments={SEGMENTS}
            userName="Lowe's Pro Account"
            userRole="Retail Partner · National"
            userInitials="LP"
            accentColor="#0E5C3A"
          />
        </div>

        <div className="flex-1 flex flex-col overflow-hidden border border-gray-200 rounded-xl m-2 bg-white">
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-100 flex-shrink-0">
            <span className="text-xs font-medium text-gray-800">OC Product Advisor</span>
            <div className="flex gap-1.5">
              <span className="text-[9px] px-2 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                2,097 product docs
              </span>
              <span className="text-[9px] px-2 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                GPT-4o-mini · CDN scaled
              </span>
            </div>
          </div>

          <div className="flex-1 overflow-hidden flex flex-col">
            {currentTab === "chat" && <ChatWindow streamType="external" accentColor="#0E5C3A" />}
            {currentTab === "kb"   && <KnowledgeBase streamType="external" />}
          </div>
        </div>
      </div>
    </>
  );
};

export default Customer;
