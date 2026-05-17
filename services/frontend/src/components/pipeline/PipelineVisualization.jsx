const stageClasses = {
  completed: 'bg-emerald-500 border-emerald-500 text-white shadow-emerald-200',
  active: 'bg-slate-900 border-slate-900 text-white shadow-slate-200 animate-pulse',
  queued: 'bg-white border-slate-200 text-slate-400',
}

export default function PipelineVisualization({ stages = [] }) {
  return (
    <div className="flex flex-col gap-6 w-full max-w-2xl">
      {stages.map((stage, index) => (
        <div key={stage.name} className="flex gap-8 group">
          <div className="flex flex-col items-center shrink-0">
             <div className={`h-10 w-10 flex items-center justify-center rounded-xl border-2 text-sm font-black shadow-lg transition-all duration-300 ${stageClasses[stage.status] || stageClasses.queued}`}>
               {index + 1}
             </div>
             {index < stages.length - 1 && (
               <div className="w-0.5 h-16 bg-slate-100 my-2 transition-colors group-hover:bg-slate-200" />
             )}
          </div>
          
          <div className="flex-1">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between p-6 rounded-2xl border border-slate-100 bg-white shadow-sm hover:shadow-md transition-all duration-300">
              <div>
                <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Stage {index + 1}</p>
                <h4 className="text-base font-black text-slate-900 tracking-tight">{stage.name}</h4>
                <div className="mt-3 flex items-center gap-4">
                   <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">Latency: {stage.latency}</span>
                   <div className="h-1 w-1 rounded-full bg-slate-200" />
                   <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">{stage.status}</span>
                </div>
              </div>
              
              <div className="mt-6 sm:mt-0 flex items-center gap-6">
                <div className="flex flex-col items-end">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="text-[11px] font-black text-slate-900">{stage.throughput}%</span>
                  </div>
                  <div className="h-1.5 w-32 rounded-full bg-slate-100 overflow-hidden shadow-inner">
                    <div 
                      className={`h-full transition-all duration-1000 ease-out ${stage.status === 'completed' ? 'bg-emerald-500' : 'bg-slate-900'}`} 
                      style={{ width: `${stage.throughput}%` }} 
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
