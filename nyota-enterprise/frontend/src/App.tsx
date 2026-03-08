
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Globe, DollarSign, ShieldAlert, Cpu, Settings, Bell } from 'lucide-react';

import './App.css';
import Dashboard from './pages/Dashboard';
import GrowthOS from './pages/GrowthOS';
import RevenueOS from './pages/RevenueOS';
import InfrastructureOS from './pages/InfrastructureOS';

const Layout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  const getBreadcrumb = (path: string) => {
    switch (path) {
      case '/': return 'Command Center';
      case '/growth': return 'Growth OS / SEO Brain';
      case '/revenue': return 'Revenue OS / Sales Sync';
      case '/infrastructure': return 'Infrastructure & Security Teams';
      default: return 'Nyota Core';
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Cpu size={18} />
          </div>
          <div className="brand-title">NYOTA V2</div>
        </div>

        <nav className="nav-links">
          <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Activity />
            <span>Command Center</span>
          </NavLink>
          <NavLink to="/growth" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Globe />
            <span>Growth OS</span>
          </NavLink>
          <NavLink to="/revenue" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <DollarSign />
            <span>Revenue OS</span>
          </NavLink>
          <NavLink to="/infrastructure" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <ShieldAlert />
            <span>Infra & Security</span>
          </NavLink>
        </nav>

        <div className="system-status">
          <div className="status-orb"></div>
          <div className="status-text">Swarm Online (9 Nodes)</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            System <span>/ {getBreadcrumb(location.pathname)}</span>
          </div>
          <div className="topbar-actions">
            <button className="action-btn">
              <Settings size={18} />
            </button>
            <button className="action-btn">
              <Bell size={18} />
            </button>
          </div>
        </header>

        <section className="content-scroll">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </section>
      </main>
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/growth" element={<GrowthOS />} />
          <Route path="/revenue" element={<RevenueOS />} />
          <Route path="/infrastructure" element={<InfrastructureOS />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
