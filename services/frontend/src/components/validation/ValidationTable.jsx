import StatusPill from '../ui/StatusPill'

export default function ValidationTable({ rows = [] }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100">
          <thead>
            <tr className="bg-slate-50/80">
              {['Invoice ID', 'Exception Type', 'Severity', 'Corrections', 'Flow Status'].map((heading) => (
                <th
                  key={heading}
                  className="px-8 py-5 text-left text-[11px] font-black uppercase tracking-[0.15em] text-slate-400"
                >
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50/50 transition-colors group">
                <td className="px-8 py-5 text-[13px] font-black text-slate-900">{row.invoice_id}</td>
                <td className="px-8 py-5 text-[12px] font-bold text-slate-500 uppercase tracking-wide">{row.error_type}</td>
                <td className="px-8 py-5">
                   <StatusPill status={row.severity} />
                </td>
                <td className="px-8 py-5 text-[12px] font-black text-slate-400 group-hover:text-slate-900 transition-colors">
                  {row.corrected_fields || 'NONE'}
                </td>
                <td className="px-8 py-5">
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
