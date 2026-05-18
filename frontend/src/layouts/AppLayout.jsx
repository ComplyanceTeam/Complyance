import { ActivitySquare, Box, FileText, LayoutDashboard, ShieldCheck, LineChart, LogOut, Upload, FileJson2 } from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Invoice Upload', to: '/upload', icon: Upload },
  { label: 'Pipeline Monitoring', to: '/pipeline', icon: ActivitySquare },
  { label: 'Validation Results', to: '/validation', icon: ShieldCheck },
  { label: 'Invoice Viewer', to: '/viewer', icon: FileJson2 },
//   { label: 'Analytics', to: '/analytics', icon: LineChart },
//   { label: 'Logs & Audit', to: '/logs', icon: FileText },
]

function SidebarLink({ item }) {
  const Icon = item.icon

  return (
    <NavLink
      to={item.to}
      end={item.to === '/'}
      className={({ isActive }) =>
        [
          'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition',
          isActive
            ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/15'
            : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900',
        ].join(' ')
      }
    >
      <Icon className="h-4 w-4" />
      {item.label}
    </NavLink>
  )
}

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-transparent text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[1800px] gap-0 p-4 lg:p-6 xl:p-8">
        <aside className="glass-surface hidden w-72 shrink-0 rounded-[2rem] p-5 lg:flex lg:flex-col">
          <div className="flex items-center gap-3 rounded-3xl bg-slate-900 px-4 py-4 text-white shadow-lg shadow-slate-900/10">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10">
              <Box className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold">Complyance</p>
              <p className="text-xs text-white/70">E-Invoice Transformation</p>
            </div>
          </div>

          <div className="mt-8 space-y-2">
            {navItems.map((item) => (
              <SidebarLink key={item.to} item={item} />
            ))}
          </div>

          <div className="mt-auto rounded-3xl bg-slate-50 p-4 text-sm text-slate-600">
            <p className="font-semibold text-slate-900">Pipeline health</p>
            <p className="mt-1">All major stages are operating within the validation SLA.</p>
            <button type="button" className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-white px-3 py-2 text-xs font-semibold text-slate-700 ring-1 ring-slate-200 transition hover:bg-slate-100">
              <LogOut className="h-4 w-4" />
              Export audit bundle
            </button>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col gap-4 lg:gap-6">
          <header className="glass-surface rounded-[2rem] px-5 py-4 lg:px-6">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Enterprise Invoice Control Plane</p>
                <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">E-Invoice Transformation & Validation System</h1>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="rounded-2xl bg-slate-100 px-4 py-2 text-sm text-slate-600">
                  Environment: <span className="font-semibold text-slate-900">Development</span>
                </div>
                <div className="rounded-2xl bg-emerald-50 px-4 py-2 text-sm font-semibold text-emerald-700">
                  Pipeline stable
                </div>
              </div>
            </div>
          </header>

          <main className="min-w-0 flex-1 pb-4">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}