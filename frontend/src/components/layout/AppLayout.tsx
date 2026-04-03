import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    return localStorage.getItem('sidebar_collapsed') === 'true';
  });

  const toggleSidebar = () => {
    setSidebarCollapsed((prev) => {
      localStorage.setItem('sidebar_collapsed', String(!prev));
      return !prev;
    });
  };

  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />

      <div
        className="flex-1 flex flex-col transition-[margin-left] duration-300"
        style={{ marginLeft: sidebarCollapsed ? 68 : 256 }}
      >
        <Header />

        <main className="flex-1 p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
