import { ActivitySquare, Box, FileText, LayoutDashboard, ShieldCheck, LineChart, Upload, FileJson2 } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Invoice Upload', to: '/upload', icon: Upload },
  { label: 'Monitoring', to: '/pipeline', icon: ActivitySquare },
  { label: 'Validation', to: '/validation', icon: ShieldCheck },
  { label: 'Viewer', to: '/viewer', icon: FileJson2 },
  { label: 'Analytics', to: '/analytics', icon: LineChart },
  { label: 'Audit Logs', to: '/logs', icon: FileText },
]

function SidebarLink({ item }) {
  const Icon = item.icon

  return (
    <NavLink
      to={item.to}
      end={item.to === '/'}
      className={({ isActive }) =>
        [
          'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
          isActive
            ? 'bg-slate-100 text-slate-900'
            : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900',
        ].join(' ')
      }
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span>{item.label}</span>
    </NavLink>
  )
}

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-100 bg-white px-4 py-6 hidden lg:flex lg:flex-col">
        <div className="flex items-center gap-2.5 px-2 mb-10">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
            <Box className="h-5 w-5" />
          </div>
          <span className="text-sm font-bold tracking-tight text-slate-900 uppercase">Complyance</span>
        </div>

        <nav className="flex-1 space-y-1">
          {navItems.map((item) => (
            <SidebarLink key={item.to} item={item} />
          ))}
        </nav>

        <div className="mt-auto border-t border-slate-50 pt-6">
          <div className="rounded-lg bg-slate-50 p-4">
            <p className="text-xs font-bold text-slate-900 uppercase tracking-wider">System Status</p>
            <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
              <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              <span>Pipeline Operational</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <header className="sticky top-0 z-30 h-16 border-b border-slate-100 bg-white/80 backdrop-blur-md px-6 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none">Management Console</span>
            <h1 className="mt-1 text-sm font-bold text-slate-900 tracking-tight">E-Invoice Transcoder</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-100 text-[10px] font-bold text-slate-500">
              <span>ENV: PRODUCTION</span>
            </div>
          </div>
        </header>

        <main className="p-6 lg:p-8 flex-1">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
