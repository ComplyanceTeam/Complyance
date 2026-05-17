import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

export default function StatCard({ title, value, change, description, icon: Icon, accent = 'blue' }) {
  const isPositive = change.startsWith('+')
  
  return (
    <div className="bg-white border border-slate-100 rounded-xl p-5 flex flex-col justify-between transition-all duration-300 hover:border-slate-300 hover:shadow-[0_10px_40px_-10px_rgba(0,0,0,0.04)] hover:-translate-y-0.5 group">
      <div className="flex items-start justify-between mb-4">
        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">{title}</p>
          <p className="mt-1 text-2xl font-bold text-slate-900 tracking-tight">{value}</p>
        </div>
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-50 text-slate-900 border border-slate-100 transition-colors group-hover:bg-slate-900 group-hover:text-white group-hover:border-slate-900">
          {Icon ? <Icon className="h-5 w-5" /> : <ArrowUpRight className="h-5 w-5" />}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className={`flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-bold transition-transform group-hover:scale-105 ${
          isPositive 
            ? 'bg-emerald-50 text-emerald-600' 
            : 'bg-rose-50 text-rose-600'
        }`}>
          {isPositive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
          {change}
        </div>
        {description && <span className="text-[10px] font-medium text-slate-400 truncate">{description}</span>}
      </div>
    </div>
  )
}
