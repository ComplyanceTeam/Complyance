import { Copy } from 'lucide-react'
import { prettyJson } from '../../utils/formatters'

const syntaxHighlight = (jsonText) => {
  const escaped = jsonText
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')

  return escaped.replace(
    /(&quot;.*?&quot;)(\s*:\s*)?(true|false|null|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|&quot;.*?&quot;)?/g,
    (match, key, separator = '', value = '') => {
      if (separator) {
        if (value === 'true' || value === 'false') {
          return `<span class="text-sky-600">${key}</span><span class="text-slate-400">${separator}</span><span class="text-emerald-600">${value}</span>`
        }

        if (value === 'null') {
          return `<span class="text-sky-600">${key}</span><span class="text-slate-400">${separator}</span><span class="text-rose-600">${value}</span>`
        }

        if (value && value.startsWith('&quot;')) {
          return `<span class="text-sky-600">${key}</span><span class="text-slate-400">${separator}</span><span class="text-amber-600">${value}</span>`
        }

        if (value) {
          return `<span class="text-sky-600">${key}</span><span class="text-slate-400">${separator}</span><span class="text-violet-600">${value}</span>`
        }
      }

      return `<span class="text-sky-600">${key}</span>`
    },
  )
}

export default function JsonViewer({ data }) {
  const jsonText = syntaxHighlight(prettyJson(data))

  const copyContent = async () => {
    await navigator.clipboard.writeText(prettyJson(data))
  }

  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-950 shadow-[0_24px_80px_rgba(15,23,42,0.24)]">
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4 text-sm text-slate-300">
        <span>Transformed invoice JSON preview</span>
        <button
          type="button"
          onClick={copyContent}
          className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-white/15"
        >
          <Copy className="h-3.5 w-3.5" />
          Copy JSON
        </button>
      </div>
      <pre className="overflow-x-auto p-5 text-sm leading-6 text-slate-200">
        <code dangerouslySetInnerHTML={{ __html: jsonText }} />
      </pre>
    </div>
  )
}