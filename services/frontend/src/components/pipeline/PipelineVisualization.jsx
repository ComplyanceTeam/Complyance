const stageClasses = {
  completed: 'bg-emerald-50 text-emerald-700 border-emerald-100',
  active: 'bg-slate-900 text-white border-slate-900',
  queued: 'bg-slate-50 text-slate-400 border-slate-100',
}

export default function PipelineVisualization({ stages = [] }) {
  return (
    <div className="flex flex-col space-y-4">
      {stages.map((stage, index) => (
        <div key={stage.name} className="flex items-center gap-4">
          <div className="flex flex-col items-center">
             <div className={`h-8 w-8 flex-center rounded-full border text-xs font-bold ${stageClasses[stage.status] || stageClasses.queued}`}>
               {index + 1}
             </div>
             {index < stages.length - 1 && (
               <div className="h-10 w-px bg-slate-100 my-1" />
             )}
          </div>
          
          <div className="flex-1 flex items-center justify-between p-4 rounded-xl border border-slate-50 bg-slate-50/30">
            <div>
              <p className="text-xs font-bold text-slate-900">{stage.name}</p>
              <p className="text-[10px] font-medium text-slate-400">Latency: {stage.latency}</p>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="hidden sm:flex flex-col items-end">
                <span className="text-[10px] font-bold text-slate-900">{stage.throughput}%</span>
                <div className="mt-1.5 h-1 w-24 rounded-full bg-slate-200 overflow-hidden">
                  <div className="h-full bg-slate-900" style={{ width: `${stage.throughput}%` }} />
                </div>
              </div>
              <span className={`text-[10px] font-bold uppercase tracking-widest ${stage.status === 'active' ? 'text-blue-600' : 'text-slate-400'}`}>
                {stage.status}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
