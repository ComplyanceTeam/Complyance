export default function AuditLogTable({ rows }) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100">
          <thead>
            <tr className="bg-slate-50/80">
              {['Timestamp', 'Actor', 'Event', 'Target', 'Details'].map((h) => (
                <th key={h} className="px-8 py-5 text-left text-[11px] font-black uppercase tracking-[0.15em] text-slate-400">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {rows.map((row) => (
              <tr key={row.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-8 py-5 text-[12px] font-bold text-slate-400 whitespace-nowrap uppercase">{row.timestamp}</td>
                <td className="px-8 py-5 text-[12px] font-black text-slate-900 uppercase tracking-tight">{row.actor}</td>
                <td className="px-8 py-5 text-[12px] font-black text-slate-700 uppercase tracking-widest">{row.event}</td>
                <td className="px-8 py-5 text-[12px] font-bold text-slate-400 italic">{row.target}</td>
                <td className="px-8 py-5 text-[12px] font-bold text-slate-500 max-w-sm truncate leading-relaxed">{row.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
