import { useEffect, useState } from 'react'
import {
  Area, Bar, BarChart, Cell, ComposedChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
  CartesianGrid, Legend,
} from 'recharts'
import Card from '../components/ui/Card'
import { analyticsApi } from '../services/api'

const chartPalette = ['#2563eb', '#f59e0b', '#10b981', '#9333ea', '#14b8a6']

const EMPTY = {
  throughput: [], severityBreakdown: [], errorBreakdown: [], countryMix: [],
}

export default function AnalyticsDashboardPage() {
  const [data, setData] = useState(EMPTY)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    analyticsApi.getAnalytics()
      .then((payload) => { if (mounted) setData(payload && payload.throughput ? payload : EMPTY) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  const empty = (arr) => !Array.isArray(arr) || arr.length === 0

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <Card header="Invoice throughput" subtitle="Volume vs error count for this batch.">
        <div className="h-80">
          {loading || empty(data.throughput) ? (
            <div className="flex h-full items-center justify-center text-slate-400 text-sm">
              {loading ? 'Loading…' : 'No data — upload an invoice first.'}
            </div>
          ) : (
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
          )}
        </div>
      </Card>

      <Card header="Error type breakdown" subtitle="Distribution of mapping errors detected by the ML engine.">
        <div className="h-80">
          {loading || empty(data.errorBreakdown) ? (
            <div className="flex h-full items-center justify-center text-slate-400 text-sm">
              {loading ? 'Loading…' : 'No error data.'}
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.errorBreakdown} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                <XAxis type="number" tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} width={180}
                  tickFormatter={(v) => v.replace(/_/g, ' ')} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#2563eb" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>

      <Card header="Severity mix" subtitle="High / Medium / Low error severity distribution.">
        <div className="h-80">
          {loading || empty(data.severityBreakdown) ? (
            <div className="flex h-full items-center justify-center text-slate-400 text-sm">
              {loading ? 'Loading…' : 'No severity data.'}
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data.severityBreakdown} dataKey="value" nameKey="name" innerRadius={60} outerRadius={100} paddingAngle={5}>
                  {data.severityBreakdown.map((entry, i) => (
                    <Cell key={entry.name} fill={chartPalette[i % chartPalette.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>

      <Card header="Country mix" subtitle="Invoice target countries in this batch.">
        <div className="h-80">
          {loading || empty(data.countryMix) ? (
            <div className="flex h-full items-center justify-center text-slate-400 text-sm">
              {loading ? 'Loading…' : 'No country data available.'}
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.countryMix} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#0f766e" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </Card>
    </div>
  )
}