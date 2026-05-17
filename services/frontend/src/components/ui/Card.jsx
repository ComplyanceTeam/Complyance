export default function Card({ children, className = '', header, subtitle, action }) {
  return (
    <section className={`surface-card ${className}`}>
      {(header || subtitle || action) && (
        <div className="px-8 py-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="min-w-0">
            {header && <h2 className="text-lg font-black text-slate-900 tracking-tight">{header}</h2>}
            {subtitle && <p className="mt-1 text-xs font-bold text-slate-400 uppercase tracking-widest">{subtitle}</p>}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}
      <div className="p-8">
        {children}
      </div>
    </section>
  )
}
