import { ActivitySquare, Box, FileText, LayoutDashboard, ShieldCheck, LineChart, Upload, FileJson2, Menu, X } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Invoice Upload', to: '/upload', icon: Upload },
  { label: 'Pipeline Monitoring', to: '/pipeline', icon: ActivitySquare },
  { label: 'Validation Results', to: '/validation', icon: ShieldCheck },
  { label: 'Invoice Viewer', to: '/viewer', icon: FileJson2 },
  { label: 'Analytics', to: '/analytics', icon: LineChart },
  { label: 'Audit Logs', to: '/logs', icon: FileText },
]

function SidebarLink({ item, onClick }) {
  const Icon = item.icon
  return (
    <NavLink
      to={item.to}
      end={item.to === '/'}
      onClick={onClick}
      className={({ isActive }) =>
        [
          'flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition-all duration-200',
          isActive
            ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/10 scale-[1.02]'
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900',
        ].join(' ')
      }
    >
      <Icon className="h-5 w-5 shrink-0" />
      <span>{item.label}</span>
    </NavLink>
  )
}

export default function AppLayout() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="layout-container bg-slate-50/30">
      {/* Mobile Top Bar */}
      <header className="lg:hidden sticky top-0 z-40 h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-slate-900 text-white shadow-lg shadow-slate-900/10">
            <Box className="h-5 w-5" />
          </div>
          <span className="text-sm font-black tracking-tighter text-slate-900 uppercase">Complyance</span>
        </div>
        <button 
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-xl bg-slate-100 text-slate-600 active:scale-90 transition-all"
        >
          {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </header>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-72 border-r border-slate-200 bg-white px-6 py-8 flex flex-col
        transition-transform duration-300 ease-in-out lg:translate-x-0
        ${isMobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}
      `}>
        <div className="flex items-center gap-3 px-3 mb-12">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white shadow-2xl shadow-slate-900/20">
            <Box className="h-6 w-6" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-black tracking-tighter text-slate-900 uppercase leading-none">Complyance</span>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mt-1.5">Control Plane</span>
          </div>
        </div>

        <nav className="flex-1 space-y-1">
          {navItems.map((item) => (
            <SidebarLink key={item.to} item={item} onClick={() => setIsMobileMenuOpen(false)} />
          ))}
        </nav>

        <div className="mt-auto border-t border-slate-50 pt-8">
          <div className="rounded-2xl bg-slate-50 border border-slate-100 p-5">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <p className="text-[10px] font-black text-slate-900 uppercase tracking-widest">Active nodes: 12</p>
            </div>
            <p className="text-[11px] text-slate-500 font-bold leading-relaxed">
              ML Supervisor v2.4 initialized. Ready for ingestion.
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="lg:pl-72 flex flex-col min-h-screen min-w-0">
        {/* Desktop Header */}
        <header className="hidden lg:flex sticky top-0 z-30 h-20 border-b border-slate-200 bg-white/50 backdrop-blur-md px-10 items-center justify-between">
          <div className="flex flex-col min-w-0">
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] leading-none mb-1.5">Management Console</span>
            <h1 className="text-lg font-black text-slate-900 tracking-tighter uppercase truncate">Enterprise Transformation Engine</h1>
          </div>
          
          <div className="flex items-center gap-4 shrink-0">
            <div className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-100 text-[10px] font-black tracking-widest uppercase">
              <span className="h-1 w-1 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,1)]" />
              Operational
            </div>
            <div className="flex items-center gap-2.5 px-4 py-2 rounded-xl bg-slate-100 text-slate-500 border border-slate-200 text-[10px] font-black tracking-widest uppercase">
              ENV: PRD_SHADOW
            </div>
          </div>
        </header>

        <main className="main-content">
          <Outlet />
        </main>
      </div>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-900/10 backdrop-blur-sm lg:hidden transition-all duration-300"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </div>
  )
}
