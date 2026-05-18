import { ArrowUpRight } from 'lucide-react'

export default function StatCard({ title, value, change, description, icon: Icon, accent = 'blue' }) {
  const accentMap = {
    blue: 'from-blue-600 to-cyan-500',
    emerald: 'from-emerald-600 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
    slate: 'from-slate-700 to-slate-500',
  }

  return (
    <div className="glass-surface rounded-3xl border-slate-200/70 p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 whitespace-nowrap text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
        </div>
        <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${accentMap[accent] || accentMap.blue} text-white shadow-lg shadow-slate-200`}>
          {Icon ? <Icon className="h-5 w-5" /> : <ArrowUpRight className="h-5 w-5" />}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2 text-sm">
        {change && (
          <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-1 font-medium text-emerald-700">
            {change}
          </span>
        )}
        {description && <span className="text-slate-500">{description}</span>}
      </div>
    </div>
  )
}