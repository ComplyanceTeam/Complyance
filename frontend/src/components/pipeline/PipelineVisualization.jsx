const stageClasses = {
  completed: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  active: 'border-blue-200 bg-blue-50 text-blue-700',
  queued: 'border-slate-200 bg-slate-50 text-slate-500',
}

export default function PipelineVisualization({ stages = [] }) {
  return (
    <div className="overflow-x-auto pb-2">
      <div className="flex min-w-max gap-4">
        {stages.map((stage, index) => (
          <div key={stage.name} className="relative w-[180px] shrink-0">
            <div className={`h-full rounded-3xl border p-4 shadow-sm transition ${stageClasses[stage.status] || stageClasses.queued}`}>
              <div className="flex items-start justify-between gap-3">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-current/70">Stage {index + 1}</p>
                <span className="inline-flex items-center rounded-full bg-white/70 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-600 ring-1 ring-inset ring-white/70">
                  {stage.status}
                </span>
              </div>

              <h3 className="mt-3 min-h-10 text-sm font-semibold leading-snug text-slate-900">{stage.name}</h3>

              <div className="mt-4">
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Latency</span>
                  <span className="whitespace-nowrap font-medium text-slate-700">{stage.latency}</span>
                </div>

                <div className="mt-2 h-2 rounded-full bg-white/80 ring-1 ring-inset ring-slate-200">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-blue-600 to-cyan-500"
                    style={{ width: `${stage.throughput}%` }}
                  />
                </div>
              </div>
            </div>

            {index < stages.length - 1 && (
              <div className="absolute right-[-18px] top-1/2 hidden h-px w-9 -translate-y-1/2 bg-slate-200 xl:block" />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}