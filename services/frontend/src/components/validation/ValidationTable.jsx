import StatusPill from '../ui/StatusPill'

export default function ValidationTable({ rows = [] }) {
  return (
    <div className="bg-white border border-slate-100 rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100">
          <thead className="bg-slate-50/50">
            <tr>
              {['Invoice ID', 'Error Type', 'Severity', 'Corrected', 'Status'].map((heading) => (
                <th
                  key={heading}
                  className="px-6 py-4 text-left text-[10px] font-black uppercase tracking-widest text-slate-400"
                >
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50/30 transition-colors group">
                <td className="px-6 py-4 text-[11px] font-bold text-slate-900">{row.invoice_id}</td>
                <td className="px-6 py-4 text-[11px] font-medium text-slate-500">{row.error_type}</td>
                <td className="px-6 py-4">
                   <StatusPill status={row.severity} />
                </td>
                <td className="px-6 py-4 text-[11px] font-bold text-slate-400 group-hover:text-slate-900 transition-colors">
                  {row.corrected_fields || 'None'}
                </td>
                <td className="px-6 py-4">
                   <StatusPill status={row.validation_status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}