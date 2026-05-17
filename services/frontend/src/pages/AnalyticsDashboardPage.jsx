import { useEffect, useState } from 'react'
import { Area, Bar, BarChart, Cell, ComposedChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from 'recharts'
import Card from '../components/ui/Card'
import { analyticsApi } from '../services/api'
import { analyticsData } from '../data/mockData'

const chartPalette = ['#0f172a', '#1e293b', '#334155', '#475569', '#64748b']

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
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card header="Flow Velocity" subtitle="Throughput volume vs error rate">
        <div className="h-64 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data.throughput}>
              <defs>
                <linearGradient id="analyticsArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0f172a" stopOpacity={0.05} />
                  <stop offset="95%" stopColor="#0f172a" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="name" hide />
              <YAxis hide />
              <Tooltip 
                 contentStyle={{ borderRadius: '8px', border: '1px solid #f1f5f9', fontSize: '10px', fontWeight: 'bold' }}
              />
              <Area type="monotone" dataKey="invoices" stroke="#0f172a" fill="url(#analyticsArea)" strokeWidth={2} dot={false} />
              <Bar dataKey="errors" fill="#10b981" radius={[4, 4, 0, 0]} barSize={12} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Severity Breakdown" subtitle="Distribution of findings">
        <div className="h-64 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.severityBreakdown} dataKey="value" innerRadius={60} outerRadius={80} paddingAngle={8} cornerRadius={4}>
                {data.severityBreakdown.map((_, idx) => (
                  <Cell key={idx} fill={chartPalette[idx % chartPalette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Jurisdiction Spread" subtitle="Batch distribution by region">
        <div className="h-64 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.countryMix}>
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 700, fill: '#cbd5e1' }} />
              <YAxis hide />
              <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '8px', border: 'none' }} />
              <Bar dataKey="value" fill="#0f172a" radius={[4, 4, 0, 0]} barSize={32} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Response Latency" subtitle="SLA performance metrics">
        <div className="h-64 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.sla} dataKey="value" innerRadius={60} outerRadius={80} paddingAngle={8} cornerRadius={4}>
                {data.sla.map((_, idx) => (
                  <Cell key={idx} fill={chartPalette[(idx + 2) % chartPalette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  )
}