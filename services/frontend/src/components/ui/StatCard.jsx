import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

export default function StatCard({ title, value, change, description, icon: Icon }) {
  const isPositive = change.startsWith('+')
  
  return (
    <div className="surface-card surface-card-hover p-6 flex flex-col justify-between min-h-[160px] group">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-[11px] font-black uppercase tracking-[0.15em] text-slate-400 mb-2">{title}</p>
          <p className="text-3xl font-black text-slate-900 tracking-tighter">{value}</p>
        </div>
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-50 text-slate-900 border border-slate-100 group-hover:bg-slate-900 group-hover:text-white group-hover:border-slate-900 transition-all duration-300">
          {Icon ? <Icon className="h-6 w-6" /> : <ArrowUpRight className="h-6 w-6" />}
        </div>
      </div>

      <div className="mt-6 flex items-center gap-3">
        <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-black ${
          isPositive 
            ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' 
            : 'bg-rose-50 text-rose-600 border border-rose-100'
        }`}>
          {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
          {change}
        </div>
        <span className="text-[11px] font-bold text-slate-400 truncate">{description}</span>
      </div>
    </div>
  )
}
