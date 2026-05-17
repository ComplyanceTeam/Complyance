import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, Clock3, Database, ShieldCheck, UploadCloud, ChevronRight, ArrowRight } from 'lucide-react'
import { Area, AreaChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts'
import Card from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'
import PipelineVisualization from '../components/pipeline/PipelineVisualization'
import { dashboardApi } from '../services/api'
import { dashboardSummary } from '../data/mockData'
import { formatNumber } from '../utils/formatters'

const validationColors = ['#0f172a', '#10b981', '#f59e0b']

export default function DashboardPage() {
  const [summary, setSummary] = useState(dashboardSummary)

  useEffect(() => {
    let mounted = true
    dashboardApi.getSummary().then((data) => {
      if (mounted) setSummary(data)
    })
    return () => { mounted = false }
  }, [])

  return (
    <div className="space-y-10">
      {/* 1. Statistics Row */}
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6 gap-6">
        <StatCard title="Total Received" value={formatNumber(summary.totals.invoicesReceived)} change="+12.4%" description="Inbound growth" icon={UploadCloud} />
        <StatCard title="Total Validated" value={formatNumber(summary.totals.invoicesValidated)} change="+9.2%" description="Queue capacity" icon={CheckCircle2} />
        <StatCard title="Transformed" value={formatNumber(summary.totals.invoicesTransformed)} change="+8.7%" description="Final outputs" icon={Database} />
        <StatCard title="Success Rate" value={`${summary.totals.successRate}%`} change="+2.1%" description="Accuracy trend" icon={ShieldCheck} />
        <StatCard title="Exception Rate" value={`${summary.totals.exceptionRate}%`} change="-1.4%" description="Review required" icon={AlertTriangle} />
        <StatCard title="Avg Latency" value={summary.totals.averageProcessingTime} change="-0.3s" description="Optimization" icon={Clock3} />
      </section>

      {/* 2. Operational Intelligence */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <Card 
          header="Operational Velocity" 
          subtitle="Processing volume over the last 24 hours" 
          className="lg:col-span-2"
          action={<button className="btn-secondary py-1.5 text-[10px] uppercase tracking-widest">Download Data</button>}
        >
          <div className="h-[350px] w-full mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary.trendData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="velocityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0f172a" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#0f172a" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }} 
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                />
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', fontSize: '12px' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="processed" 
                  stroke="#0f172a" 
                  strokeWidth={3} 
                  fill="url(#velocityGradient)" 
                  dot={{ r: 4, fill: '#0f172a', strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 6, strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card header="Inbound Mix" subtitle="Source format distribution">
          <div className="h-[280px] flex items-center justify-center mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={summary.pipelineSplit} 
                  dataKey="value" 
                  innerRadius={80} 
                  outerRadius={110} 
                  paddingAngle={8}
                  stroke="none"
                >
                  {summary.pipelineSplit.map((_, i) => (
                    <Cell key={i} fill={validationColors[i % validationColors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-4 mt-10">
             {summary.pipelineSplit.map((item, i) => (
               <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100/50">
                 <div className="flex items-center gap-3">
                   <div className="h-2.5 w-2.5 rounded-full shadow-sm" style={{ backgroundColor: validationColors[i % validationColors.length] }} />
                   <span className="text-[11px] font-black text-slate-500 uppercase tracking-widest">{item.name}</span>
                 </div>
                 <span className="text-[12px] font-black text-slate-900">{item.value}%</span>
               </div>
             ))}
          </div>
        </Card>
      </section>

      {/* 3. Pipeline Stepper & KPIs */}
      <section className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <Card header="Pipeline Lifecycle" subtitle="Visual end-to-end monitoring">
          <div className="mt-6">
            <PipelineVisualization stages={summary.pipelineStages} />
          </div>
        </Card>

        <Card header="Validation Metrics" subtitle="Compliance audit performance">
          <div className="space-y-8 mt-6">
             {summary.validationSummary.map((item) => (
               <div key={item.label} className="group">
                 <div className="flex items-center justify-between mb-3">
                   <div className="flex items-center gap-2">
                     <div className="w-1.5 h-1.5 rounded-full bg-slate-900 opacity-20 group-hover:opacity-100 transition-opacity" />
                     <span className="text-[11px] font-black text-slate-500 uppercase tracking-widest leading-none">{item.label}</span>
                   </div>
                   <span className="text-[12px] font-black text-slate-900">{item.value}%</span>
                 </div>
                 <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden border border-slate-200/20 shadow-inner">
                   <div 
                    className="h-full bg-slate-900 rounded-full transition-all duration-1000 ease-out shadow-sm" 
                    style={{ width: `${item.value}%` }} 
                   />
                 </div>
               </div>
             ))}
          </div>
        </Card>
      </section>

      {/* 4. Event Ledger */}
      <Card 
        header="Execution Ledger" 
        subtitle="Chronological history of system events"
        action={<button className="text-[11px] font-black text-slate-900 uppercase tracking-widest flex items-center gap-1.5 hover:gap-2.5 transition-all">Full Audit <ArrowRight className="h-4 w-4" /></button>}
      >
        <div className="mt-4 divide-y divide-slate-100 border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
          {summary.recentActivity.map((item) => (
            <div key={item.id} className="p-4 flex items-center justify-between bg-white hover:bg-slate-50/50 transition-all cursor-pointer group">
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 flex-center bg-slate-900 rounded-xl text-[12px] font-black text-white shadow-lg shadow-slate-900/10 group-hover:scale-110 transition-transform">
                  {item.country}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-black text-slate-900 tracking-tight">{item.id}</p>
                  <p className="text-[11px] text-slate-400 font-bold uppercase tracking-wider mt-0.5">{item.owner}</p>
                </div>
              </div>
              <div className="flex items-center gap-8">
                <div className="hidden sm:flex flex-col items-end">
                  <div className="flex items-center gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full ${item.status === 'validated' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                    <span className="text-[11px] font-black text-slate-900 uppercase tracking-widest">{item.status}</span>
                  </div>
                  <p className="text-[10px] text-slate-300 font-bold mt-1 uppercase">{item.updatedAt}</p>
                </div>
                <div className="w-8 h-8 flex-center rounded-full bg-slate-50 text-slate-300 group-hover:bg-slate-900 group-hover:text-white transition-all">
                  <ChevronRight className="h-4 w-4" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
