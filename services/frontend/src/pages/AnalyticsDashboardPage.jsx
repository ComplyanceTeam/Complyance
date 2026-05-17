import { useEffect, useState } from 'react'
import { Area, Bar, BarChart, Cell, ComposedChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Legend } from 'recharts'
import Card from '../components/ui/Card'
import { analyticsApi } from '../services/api'
import { analyticsData } from '../data/mockData'

const chartPalette = ['#2563eb', '#0f766e', '#f59e0b', '#9333ea', '#14b8a6']

export default function AnalyticsDashboardPage() {
  const [data, setData] = useState(analyticsData)

  useEffect(() => {
    let mounted = true

    analyticsApi.getAnalytics().then((payload) => {
      if (mounted) {
        setData(payload)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <Card header="Invoice throughput" subtitle="Volume trend with error signal overlay.">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data.throughput} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="analyticsArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.28} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="invoices" stroke="#2563eb" fill="url(#analyticsArea)" strokeWidth={2} />
              <Bar dataKey="errors" fill="#f59e0b" radius={[8, 8, 0, 0]} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Severity mix" subtitle="Distribution of validation findings.">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.severityBreakdown} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100} paddingAngle={5}>
                {data.severityBreakdown.map((entry, index) => (
                  <Cell key={entry.name} fill={chartPalette[index % chartPalette.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="Country mix" subtitle="Volume spread across supported invoice jurisdictions.">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.countryMix} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#0f766e" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card header="SLA distribution" subtitle="Processing time profile across the current batch.">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data.sla} dataKey="value" nameKey="name" outerRadius={100} innerRadius={50} paddingAngle={4}>
                {data.sla.map((entry, index) => (
                  <Cell key={entry.name} fill={chartPalette[(index + 1) % chartPalette.length]} />
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