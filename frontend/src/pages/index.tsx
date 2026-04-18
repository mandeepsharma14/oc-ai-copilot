"use client";
import type { NextPage } from "next";
import Head from "next/head";
import { useState } from "react";
import { Sidebar }      from "@/components/shared/Sidebar";
import { ChatWindow }   from "@/components/chat/ChatWindow";
import { Dashboard }    from "@/components/admin/Dashboard";
import { KnowledgeBase }from "@/components/kb/KnowledgeBase";
import { useAppStore }  from "@/store/appStore";

const NAV_ITEMS = [
  {
    key: "chat", label: "Ask Copilot",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  },
  {
    key: "dashboard", label: "Dashboard", badge: "Live",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>,
  },
  {
    key: "kb", label: "Knowledge base", badge: "4,847",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>,
  },
  {
    key: "admin", label: "Admin panel",
    icon: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>,
  },
];

const SEGMENTS = [
  { name: "Safety & EHS",          count: "847 docs · 60 sites" },
  { name: "Engineering & Automation", count: "634 docs" },
  { name: "Quality & Manufacturing",  count: "712 docs" },
  { name: "Maintenance & Reliability",count: "521 docs" },
  { name: "IT & Security",            count: "389 docs" },
  { name: "HR & People",              count: "312 docs" },
  { name: "New Hire Onboarding",      count: "198 docs" },
  { name: "Finance & CapEx",          count: "234 docs" },
];

const TITLES: Record<string, string> = {
  chat:      "Ask Copilot — Internal",
  dashboard: "Dashboard — Internal stream",
  kb:        "Knowledge base — 4,847 documents",
  admin:     "Admin panel",
};

const Home: NextPage = () => {
  const { currentTab } = useAppStore();

  return (
    <>
      <Head>
        <title>OC AI Copilot — Internal Employee Portal</title>
        <meta name="description" content="Owens Corning Internal Knowledge Assistant" />
      </Head>

      <div className="flex h-screen overflow-hidden bg-gray-50">
        {/* Sidebar */}
        <div className="w-52 flex-shrink-0">
          <Sidebar
            navItems={NAV_ITEMS}
            segments={SEGMENTS}
            userName="Andy Sharma"
            userRole="Platform Owner · Charlotte, NC"
            userInitials="AS"
            accentColor="#1B2E4A"
          />
        </div>

        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden border border-gray-200 rounded-xl m-2 bg-white">
          {/* Topbar */}
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-100 flex-shrink-0">
            <span className="text-xs font-medium text-gray-800">
              {TITLES[currentTab] || "OC AI Copilot"}
            </span>
            <div className="flex gap-1.5">
              <span className="text-[9px] px-2 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                4,847 docs · 60 sites
              </span>
              <span className="text-[9px] px-2 py-1 rounded-full bg-green-50 text-green-800 border border-green-200">
                GPT-4o · Azure OpenAI
              </span>
            </div>
          </div>

          {/* Panels */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {currentTab === "chat"      && <ChatWindow streamType="internal" accentColor="#1B2E4A" />}
            {currentTab === "dashboard" && <Dashboard />}
            {currentTab === "kb"        && <KnowledgeBase streamType="internal" />}
            {currentTab === "admin"     && (
              <div className="p-4 text-xs text-gray-500">Admin panel — see Dashboard for live metrics.</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default Home;
