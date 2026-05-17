import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import PipelineVisualization from '../components/pipeline/PipelineVisualization'
import { dashboardApi } from '../services/api'
import { dashboardSummary } from '../data/mockData'

export default function PipelineMonitoringPage() {
  const [stages, setStages] = useState(dashboardSummary.pipelineStages)

  useEffect(() => {
    let mounted = true

    dashboardApi.getPipelineStages().then((data) => {
      if (mounted) {
        setStages(data)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="space-y-6">
      <Card header="Pipeline monitoring" subtitle="Track execution across ingestion, validation, transformation, correction, and output stages.">
        <PipelineVisualization stages={stages} />
      </Card>

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
    </div>
  )
}