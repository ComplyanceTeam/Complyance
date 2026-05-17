export default function Card({ children, className = '', header, subtitle, action }) {
  return (
    <section className={`bg-white border border-slate-100 rounded-xl overflow-hidden transition-all duration-300 hover:border-slate-200 hover:shadow-[0_8px_30px_rgb(0,0,0,0.02)] ${className}`}>
      {(header || subtitle || action) && (
        <div className="px-6 py-5 border-b border-slate-50 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between bg-white transition-colors">
          <div className="min-w-0">
            {header && <h2 className="text-sm font-bold text-slate-900 tracking-tight">{header}</h2>}
            {subtitle && <p className="mt-0.5 text-[11px] font-medium text-slate-400">{subtitle}</p>}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className="p-6 min-w-0">
        {children}
      </div>
    </section>
  )
}
