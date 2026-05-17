const stageClasses = {
  completed: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  active: 'border-blue-200 bg-blue-50 text-blue-700',
  queued: 'border-slate-200 bg-slate-50 text-slate-500',
}

export default function PipelineVisualization({ stages = [] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-7">
      {stages.map((stage, index) => (
        <div key={stage.name} className="relative">
          <div className={`rounded-3xl border p-4 shadow-sm ${stageClasses[stage.status] || stageClasses.queued}`}>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-current/70">Stage {index + 1}</p>
            <h3 className="mt-3 text-sm font-semibold text-slate-900">{stage.name}</h3>
            <p className="mt-2 text-xs text-slate-500">Latency {stage.latency}</p>

            <div className="mt-4 h-2 rounded-full bg-white/80 ring-1 ring-inset ring-slate-200">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-blue-600 to-cyan-500"
                style={{ width: `${stage.throughput}%` }}
              />
            </div>

            <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
              <span>{stage.throughput}% throughput</span>
              <span className="capitalize">{stage.status}</span>
            </div>
          </div>

          {index < stages.length - 1 && (
            <div className="absolute right-[-18px] top-1/2 hidden h-px w-9 -translate-y-1/2 bg-slate-200 xl:block" />
          )}
        </div>
      ))}
    </div>
  )
}