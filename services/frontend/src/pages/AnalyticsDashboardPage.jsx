import { useEffect, useState } from 'react'
import { Area, AreaChart, Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts'
import Card from '../components/ui/Card'
import { analyticsApi } from '../services/api'
import { analyticsData } from '../data/mockData'

const chartPalette = ['#0f172a', '#334155', '#475569', '#94a3b8', '#cbd5e1']

export default function AnalyticsDashboardPage() {
  const [data, setData] = useState(analyticsData)

  useEffect(() => {
    let mounted = true
    analyticsApi.getAnalytics().then((payload) => {
      if (mounted) setData(payload)
    })
    return () => { mounted = false }
  }, [])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <Card header="Process Velocity" subtitle="Ingestion vs. throughput volume">
        <div className="h-80 w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.throughput} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="analyticsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0f172a" stopOpacity={0.08} />
                  <stop offset="95%" stopColor="#0f172a" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} />
              <Tooltip 
                 contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '11px', fontWeight: 'bold' }}
              />
              <Area type="monotone" dataKey="invoices" stroke="#0f172a" strokeWidth={3} fill="url(#analyticsGradient)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Jurisdiction Spread" subtitle="Volume distribution by region">
        <div className="h-80 w-full mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.countryMix} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="4 4" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700, fill: '#94a3b8' }} />
              <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '12px', border: 'none' }} />
              <Bar dataKey="value" fill="#0f172a" radius={[6, 6, 0, 0]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Condition Mix" subtitle="Batch exception severity profiling">
        <div className="h-64 flex items-center justify-center mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.severityBreakdown} dataKey="value" innerRadius={80} outerRadius={110} paddingAngle={8} stroke="none">
                {data.severityBreakdown.map((_, idx) => (
                  <Cell key={idx} fill={chartPalette[idx % chartPalette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-4">
           {data.severityBreakdown.map((item, idx) => (
             <div key={idx} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100/50">
               <div className="h-2 w-2 rounded-full" style={{ backgroundColor: chartPalette[idx % chartPalette.length] }} />
               <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{item.name}</span>
             </div>
           ))}
        </div>
      </Card>

      <Card header="SLA Compliance" subtitle="Latency performance profile">
        <div className="h-64 flex items-center justify-center mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.sla} dataKey="value" innerRadius={80} outerRadius={110} paddingAngle={8} stroke="none">
                {data.sla.map((_, idx) => (
                  <Cell key={idx} fill={chartPalette[(idx + 2) % chartPalette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-8 grid grid-cols-2 gap-4">
           {data.sla.map((item, idx) => (
             <div key={idx} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100/50">
               <div className="h-2 w-2 rounded-full" style={{ backgroundColor: chartPalette[(idx + 2) % chartPalette.length] }} />
               <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{item.name}</span>
             </div>
           ))}
        </div>
      </Card>
    </div>
  )
}
