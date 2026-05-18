import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import PipelineVisualization from '../components/pipeline/PipelineVisualization'
import { dashboardApi, pipelineApi } from '../services/api'
import { Terminal, RefreshCw } from 'lucide-react'

export default function PipelineMonitoringPage() {
  const [stages, setStages] = useState([])
  const [loading, setLoading] = useState(true)
  const [logs, setLogs] = useState('')
  const [logsLoading, setLogsLoading] = useState(false)

  const fetchLogs = () => {
    setLogsLoading(true)
    pipelineApi.getLogs()
      .then((res) => { setLogs(res.logs || 'No terminal output available.') })
      .catch((err) => { setLogs('Error loading terminal output: ' + err.message) })
      .finally(() => { setLogsLoading(false) })
  }

  useEffect(() => {
    let mounted = true
    dashboardApi.getPipelineStages()
      .then((data) => { if (mounted) setStages(Array.isArray(data) ? data : []) })
      .finally(() => { if (mounted) setLoading(false) })
    fetchLogs()
    return () => { mounted = false }
  }, [])

  return (
    <div className="space-y-6">
      <Card header="Pipeline monitoring" subtitle="Track execution across ingestion, validation, transformation, correction, and output stages.">
        {loading ? (
          <p className="py-6 text-center text-slate-400">Loading pipeline status…</p>
        ) : stages.length === 0 ? (
          <p className="py-6 text-center text-slate-400">No pipeline data. Upload an invoice to begin.</p>
        ) : (
          <PipelineVisualization stages={stages} />
        )}
      </Card>

      {/* Terminal Output Card */}
      <Card 
        header={
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-slate-700" />
              <span>Pipeline Terminal Console Output</span>
            </div>
            <button
              onClick={fetchLogs}
              disabled={logsLoading}
              className="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 disabled:opacity-50 px-2.5 py-1.5 text-xs font-semibold text-slate-700 transition"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${logsLoading ? 'animate-spin' : ''}`} />
              Refresh Console
            </button>
          </div>
        }
        subtitle="Real-time standard output (stdout) from the ML-powered invoice transcoding pipeline."
      >
        <div className="rounded-2xl bg-slate-950 p-4 font-mono text-xs text-slate-200 overflow-x-auto max-h-96 shadow-inner border border-slate-800">
          {logsLoading ? (
            <span className="text-slate-400">Loading terminal streams...</span>
          ) : (
            <pre className="whitespace-pre-wrap leading-relaxed select-text">
              {logs}
            </pre>
          )}
        </div>
      </Card>

      {stages.length > 0 && (
        <div className="grid gap-6 lg:grid-cols-3">
          {stages.map((stage) => (
            <Card key={stage.name} header={stage.name} subtitle={`Status: ${stage.status}`}>
              <div className="space-y-3 text-sm text-slate-600">
                <div className="flex items-center justify-between">
                  <span>Throughput</span>
                  <span className="font-semibold text-slate-900">{stage.throughput}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div className="h-2 rounded-full bg-gradient-to-r from-blue-600 to-cyan-500" style={{ width: `${stage.throughput}%` }} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Latency</span>
                  <span className="font-semibold text-slate-900">{stage.latency}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}