import { statusTone } from '../../utils/formatters'

const toneClasses = {
  success: 'bg-emerald-50 text-emerald-700',
  info: 'bg-blue-50 text-blue-700',
  warning: 'bg-amber-50 text-amber-700',
  danger: 'bg-rose-50 text-rose-700',
  neutral: 'bg-slate-50 text-slate-500',
}

export default function StatusPill({ status }) {
  const tone = statusTone(status)

  return (
    <span className={`inline-flex items-center rounded px-1.5 py-0.5 text-[9px] font-black uppercase tracking-widest ${toneClasses[tone]}`}>
      {status}
    </span>
  )
}