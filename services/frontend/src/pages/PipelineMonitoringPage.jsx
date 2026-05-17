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
      if (mounted) setStages(data)
    })
    return () => { mounted = false }
  }, [])

  return (
    <div className="space-y-8">
      <Card header="Stage Monitor" subtitle="Real-time execution status across the transformation lifecycle">
        <PipelineVisualization stages={stages} />
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stages.map((stage) => (
          <div key={stage.name} className="bg-white border border-slate-100 rounded-xl p-5 group hover:border-slate-200 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
               <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">{stage.name}</p>
               <div className={`h-1.5 w-1.5 rounded-full ${stage.status === 'completed' ? 'bg-emerald-500' : stage.status === 'active' ? 'bg-blue-500 animate-pulse' : 'bg-slate-200'}`} />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Load</span>
                <span className="text-[10px] font-black text-slate-900">{stage.throughput}%</span>
              </div>
              <div className="h-1 rounded-full bg-slate-50 overflow-hidden">
                <div className="h-full bg-slate-900 transition-all duration-500" style={{ width: `${stage.throughput}%` }} />
              </div>
              <div className="flex items-center justify-between pt-1">
                <span className="text-[10px] font-bold text-slate-500 uppercase">Latency</span>
                <span className="text-[10px] font-black text-slate-900">{stage.latency}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}