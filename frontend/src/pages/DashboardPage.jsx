import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2, Clock3, Database, ShieldCheck, UploadCloud } from 'lucide-react'
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell,
  Pie, PieChart, ResponsiveContainer, Tooltip, Legend, XAxis, YAxis,
} from 'recharts'
import Card from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'
import PipelineVisualization from '../components/pipeline/PipelineVisualization'
import { dashboardApi } from '../services/api'
import { formatNumber } from '../utils/formatters'

const PIE_COLORS = ['#2563eb', '#f59e0b', '#10b981']

const EMPTY_SUMMARY = {
  totals: {
    invoicesReceived: 0, invoicesValidated: 0, invoicesTransformed: 0,
    successRate: 0, exceptionRate: 0, averageProcessingTime: 'N/A',
  },
  validationSummary: [],
  pipelineStages: [],
  pipelineSplit: [],
  recentActivity: [],
  trendData: [],
}

export default function DashboardPage() {
  const [summary, setSummary] = useState(EMPTY_SUMMARY)
  const [stages, setStages] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    Promise.all([
      dashboardApi.getSummary(),
      dashboardApi.getPipelineStages(),
      dashboardApi.getRecentActivity(),
    ])
      .then(([sum, stg, act]) => {
        if (!mounted) return
        // Backend returns {ready:false} until a file is uploaded
        if (sum && sum.ready === false) {
          setSummary(null)  // null = "not uploaded yet"
        } else {
          setSummary(sum?.totals ? sum : EMPTY_SUMMARY)
        }
        setStages(Array.isArray(stg) ? stg : [])
        setActivity(Array.isArray(act) ? act : [])
      })
      .catch((e) => { if (mounted) setError(e.message) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  // summary===null means backend is up but no upload done yet
  const notUploaded = !loading && !error && summary === null


  const t = (summary && summary.totals) ? summary.totals : EMPTY_SUMMARY.totals

  if (loading) return <div className="p-8 text-slate-500">Loading dashboard data…</div>
  if (error) return (
    <div className="rounded-2xl bg-red-50 p-6 text-red-700">
      <strong>Backend not reachable:</strong> {error}
      <p className="mt-2 text-sm">Make sure the FastAPI server is running: <code className="font-mono">uvicorn server:app --port 8000</code></p>
    </div>
  )
  if (notUploaded) return (
    <div className="flex flex-col items-center justify-center gap-6 py-24 text-center">
      <div className="rounded-full bg-blue-50 p-6">
        <svg className="h-12 w-12 text-blue-400" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
      </div>
      <div>
        <h2 className="text-xl font-semibold text-slate-800">No invoice data yet</h2>
        <p className="mt-2 text-slate-500 max-w-md">Upload an invoice file on the <strong>Invoice Upload</strong> page to run the pipeline. The dashboard will populate with real results.</p>
      </div>
      <a href="/upload" className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 transition">
        Go to Invoice Upload →
      </a>
    </div>
  )


  // Build a pie from validationSummary if present
  const pieSplit = (summary.validationSummary && summary.validationSummary.length > 0)
    ? summary.validationSummary.map((s) => ({ name: s.label, value: s.value }))
    : [{ name: 'Valid', value: t.successRate }, { name: 'Invalid', value: t.exceptionRate }]

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
        <StatCard title="Invoices received" value={formatNumber(t.invoicesReceived)} icon={UploadCloud} accent="blue" />
        <StatCard title="Validated" value={formatNumber(t.invoicesValidated)} icon={CheckCircle2} accent="emerald" />
        <StatCard title="Transformed" value={formatNumber(t.invoicesTransformed)} icon={Database} accent="slate" />
        <StatCard title="Success rate" value={`${t.successRate}%`} icon={ShieldCheck} accent="emerald" />
        <StatCard title="Exception rate" value={`${t.exceptionRate}%`} icon={AlertTriangle} accent="amber" />
        <StatCard title="Avg latency" value={t.averageProcessingTime} icon={Clock3} accent="blue" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.6fr_1fr]">
        <Card header="Pipeline visualization" subtitle="Seven-stage invoice journey from ingestion to output.">
          <PipelineVisualization stages={stages} />
        </Card>

        <Card header="Mapping quality" subtitle="Success vs exception rate for this batch.">
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieSplit} dataKey="value" nameKey="name" innerRadius={64} outerRadius={100} paddingAngle={4}>
                  {pieSplit.map((entry, i) => (
                    <Cell key={entry.name} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => `${v}%`} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </section>

      <section>
        <Card header="Recent invoice activity" subtitle="Latest invoices processed by the ML engine.">
          {activity.length === 0 ? (
            <p className="py-6 text-center text-slate-400">No activity yet. Upload an invoice to begin.</p>
          ) : (
            <div className="space-y-3">
              {activity.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <div>
                    <p className="font-medium text-slate-900">{item.id}</p>
                    <p className="text-sm text-slate-500">{item.owner}</p>
                  </div>
                  <div className="text-right text-sm">
                    <p className={`font-semibold capitalize ${item.status === 'flagged' ? 'text-amber-600' : 'text-emerald-600'}`}>
                      {item.status}
                    </p>
                    {item.errors && <p className="text-xs text-slate-400">{item.errors}</p>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </section>
    </div>
  )
}