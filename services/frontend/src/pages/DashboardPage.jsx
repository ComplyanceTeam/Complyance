import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, Clock3, Database, ShieldCheck, UploadCloud, ChevronRight } from 'lucide-react'
import { Area, AreaChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
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
    <div className="space-y-8">
      {/* 1. Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard title="Total Received" value={formatNumber(summary.totals.invoicesReceived)} change="+12%" description="Period growth" icon={UploadCloud} />
        <StatCard title="Validated" value={formatNumber(summary.totals.invoicesValidated)} change="+9%" description="Flow capacity" icon={CheckCircle2} />
        <StatCard title="Transformed" value={formatNumber(summary.totals.invoicesTransformed)} change="+10%" description="Output rate" icon={Database} />
        <StatCard title="Success Rate" value={`${summary.totals.successRate}%`} change="+2%" description="Accuracy" icon={ShieldCheck} />
        <StatCard title="Error Rate" value={`${summary.totals.exceptionRate}%`} change="-1%" description="Decline" icon={AlertTriangle} />
        <StatCard title="Avg Latency" value={summary.totals.averageProcessingTime} change="-0.2s" description="Optimization" icon={Clock3} />
      </div>

      {/* 2. Primary Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card header="Operational Throughput" subtitle="Daily processing volume" className="lg:col-span-2">
          <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary.trendData}>
                <defs>
                  <linearGradient id="areaColor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0f172a" stopOpacity={0.05} />
                    <stop offset="95%" stopColor="#0f172a" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" hide />
                <YAxis hide />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: '1px solid #f1f5f9', boxShadow: 'none', fontSize: '10px', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="processed" stroke="#0f172a" fill="url(#areaColor)" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card header="Batch Status" subtitle="Current distribution">
          <div className="h-48 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={summary.pipelineSplit} dataKey="value" innerRadius={60} outerRadius={80} paddingAngle={5}>
                  {summary.pipelineSplit.map((_, i) => (
                    <Cell key={i} fill={validationColors[i % validationColors.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 mt-4">
             {summary.pipelineSplit.map((item, i) => (
               <div key={i} className="flex items-center justify-between">
                 <div className="flex items-center gap-2">
                   <div className="h-2 w-2 rounded-full" style={{ backgroundColor: validationColors[i % validationColors.length] }} />
                   <span className="text-[10px] font-bold text-slate-500 uppercase">{item.name}</span>
                 </div>
                 <span className="text-[10px] font-black text-slate-900">{item.value}%</span>
               </div>
             ))}
          </div>
        </Card>
      </div>

      {/* 3. Pipeline & KPIs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card header="Pipeline Lifecycle" subtitle="Visual stage monitoring">
          <div className="mt-4">
            <PipelineVisualization stages={summary.pipelineStages} />
          </div>
        </Card>

        <Card header="Quality Performance" subtitle="Compliance audit metrics">
          <div className="space-y-6 mt-4">
             {summary.validationSummary.map((item) => (
               <div key={item.label}>
                 <div className="flex items-center justify-between mb-1.5">
                   <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{item.label}</span>
                   <span className="text-[10px] font-black text-slate-900">{item.value}%</span>
                 </div>
                 <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden">
                   <div className="h-full bg-slate-900 rounded-full" style={{ width: `${item.value}%` }} />
                 </div>
               </div>
             ))}
          </div>
        </Card>
      </div>

      {/* 4. Recent Events */}
      <Card header="Recent Processing Events" subtitle="Latest invoice activity log">
        <div className="divide-y divide-slate-50">
          {summary.recentActivity.map((item) => (
            <div key={item.id} className="py-3 flex items-center justify-between hover:bg-slate-50/80 px-3 -mx-3 rounded-xl transition-all duration-200 cursor-pointer group hover:translate-x-1">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 flex-center bg-slate-50 rounded-lg text-[10px] font-black text-slate-400 group-hover:bg-slate-900 group-hover:text-white group-hover:shadow-lg group-hover:shadow-slate-200 transition-all">
                  {item.country}
                </div>
                <div>
                  <p className="text-[11px] font-bold text-slate-900">{item.id}</p>
                  <p className="text-[10px] text-slate-400 font-medium group-hover:text-slate-500 transition-colors">{item.owner}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-[10px] font-black text-slate-900 uppercase tracking-widest">{item.status}</p>
                  <p className="text-[10px] text-slate-300 font-bold group-hover:text-slate-400 transition-colors">{item.updatedAt}</p>
                </div>
                <ChevronRight className="h-4 w-4 text-slate-200 group-hover:text-slate-900 transition-all group-hover:translate-x-0.5" />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
