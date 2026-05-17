export default function Card({ children, className = '', header, subtitle, action }) {
  return (
    <section className={`section-shell ${className}`}>
      {(header || subtitle || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {header && <h2 className="text-base font-semibold text-slate-900">{header}</h2>}
            {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  )
}