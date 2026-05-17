import StatusPill from '../ui/StatusPill'

export default function ValidationTable({ rows = [] }) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50/90">
            <tr>
              {['invoice_id', 'error_type', 'severity', 'corrected_fields', 'validation_status'].map((heading) => (
                <th
                  key={heading}
                  className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-slate-500"
                >
                  {heading.replaceAll('_', ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {rows.map((row) => (
              <tr key={`${row.invoice_id}-${row.error_type}`} className="hover:bg-slate-50/70">
                <td className="px-4 py-4 text-sm font-medium text-slate-900">{row.invoice_id}</td>
                <td className="px-4 py-4 text-sm text-slate-600">{row.error_type}</td>
                <td className="px-4 py-4 text-sm"><StatusPill status={row.severity} /></td>
                <td className="px-4 py-4 text-sm text-slate-600">{row.corrected_fields}</td>
                <td className="px-4 py-4 text-sm"><StatusPill status={row.validation_status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}