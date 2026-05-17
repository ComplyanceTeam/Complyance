import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, Clock3, Database, ShieldCheck, UploadCloud } from 'lucide-react'
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import Card from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'
import PipelineVisualization from '../components/pipeline/PipelineVisualization'
import { dashboardApi } from '../services/api'
import { dashboardSummary } from '../data/mockData'
import { formatNumber } from '../utils/formatters'

const validationColors = ['#2563eb', '#0f766e', '#f59e0b']

export default function DashboardPage() {
  const [summary, setSummary] = useState(dashboardSummary)

  useEffect(() => {
    let mounted = true

    dashboardApi.getSummary().then((data) => {
      if (mounted) {
        setSummary(data)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <StatCard title="Invoices received" value={formatNumber(summary.totals.invoicesReceived)} change="+11.4%" description="vs previous period" icon={UploadCloud} accent="blue" />
        <StatCard title="Validated" value={formatNumber(summary.totals.invoicesValidated)} change="+9.1%" description="validation throughput" icon={CheckCircle2} accent="emerald" />
        <StatCard title="Transformed" value={formatNumber(summary.totals.invoicesTransformed)} change="+8.7%" description="successful outputs" icon={Database} accent="slate" />
        <StatCard title="Success rate" value={`${summary.totals.successRate}%`} change="+2.1 pts" description="pipeline quality" icon={ShieldCheck} accent="emerald" />
        <StatCard title="Exception rate" value={`${summary.totals.exceptionRate}%`} change="-0.8 pts" description="downward trend" icon={AlertTriangle} accent="amber" />
        <StatCard title="Avg latency" value={summary.totals.averageProcessingTime} change="-0.3s" description="batch response time" icon={Clock3} accent="blue" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <Card header="Processing metrics" subtitle="Daily invoice volume and validation quality across the pipeline.">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary.trendData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="processedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="processed" stroke="#2563eb" fill="url(#processedGradient)" strokeWidth={2} />
                <Area type="monotone" dataKey="valid" stroke="#10b981" fillOpacity={0} strokeWidth={2} />
                <Area type="monotone" dataKey="invalid" stroke="#f59e0b" fillOpacity={0} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card header="Pipeline status" subtitle="Current execution mix across batches.">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={summary.pipelineSplit} dataKey="value" nameKey="name" innerRadius={64} outerRadius={100} paddingAngle={4}>
                  {summary.pipelineSplit.map((entry, index) => (
                    <Cell key={entry.name} fill={validationColors[index % validationColors.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-3">
            {summary.pipelineSplit.map((entry, index) => (
              <div key={entry.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2 text-slate-600">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: validationColors[index % validationColors.length] }} />
                  {entry.name}
                </div>
                <span className="font-semibold text-slate-900">{entry.value}%</span>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <Card header="Pipeline visualization" subtitle="Seven-stage invoice journey from ingestion to output generation.">
          <PipelineVisualization stages={summary.pipelineStages} />
        </Card>

        <Card header="Validation summary" subtitle="Quality indicators across key compliance checks.">
          <div className="space-y-4">
            {summary.validationSummary.map((item) => (
              <div key={item.label}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-600">{item.label}</span>
                  <span className="font-semibold text-slate-900">{item.value}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div className="h-2 rounded-full bg-gradient-to-r from-slate-900 to-blue-600" style={{ width: `${item.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
        <Card header="Recent invoice activity" subtitle="Latest invoices moving through the transformation engine.">
          <div className="space-y-4">
            {summary.recentActivity.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <div>
                  <p className="font-medium text-slate-900">{item.id}</p>
                  <p className="text-sm text-slate-500">{item.owner} - {item.country}</p>
                </div>
                <div className="text-right text-sm text-slate-500">
                  <p className="font-medium text-slate-900 capitalize">{item.status}</p>
                  <p>{item.updatedAt}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card header="Invoice success / failure" subtitle="Batch distribution for the current processing window.">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary.trendData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" tickLine={false} axisLine={false} />
                <YAxis tickLine={false} axisLine={false} />
                <Tooltip />
                <Bar dataKey="valid" fill="#10b981" radius={[8, 8, 0, 0]} />
                <Bar dataKey="invalid" fill="#f59e0b" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </section>
    </div>
  )
}