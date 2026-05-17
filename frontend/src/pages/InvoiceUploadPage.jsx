import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Card from '../components/ui/Card'
import UploadDropzone from '../components/upload/UploadDropzone'
import { invoiceApi } from '../services/api'
import { CheckCircle2, UploadCloud, RotateCcw } from 'lucide-react'

export default function InvoiceUploadPage() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFileSelect = (nextFile) => {
    setFile(nextFile)
    setProgress(5)
    setResult(null)
    setError(null)
  }

  const startUpload = async () => {
    if (!file || isUploading) return
    setIsUploading(true)
    setError(null)
    setProgress(10)

    const ticker = window.setInterval(() => {
      setProgress((p) => Math.min(p + 8, 85))
    }, 400)

    try {
      const response = await invoiceApi.uploadInvoice(file)
      window.clearInterval(ticker)
      setProgress(100)
      setResult(response)
      // Redirect to dashboard after 2 seconds to show results
      setTimeout(() => navigate('/'), 2000)
    } catch (e) {
      window.clearInterval(ticker)
      setError(e?.response?.data?.detail || e.message || 'Pipeline error')
      setProgress(0)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card header="Invoice upload" subtitle="Drag and drop a CSV, XML, or JSON invoice file. The pipeline will run automatically.">
          <UploadDropzone file={file} onFileSelect={handleFileSelect} progress={progress} isUploading={isUploading} />

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={startUpload}
              disabled={!file || isUploading}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              <UploadCloud className="h-4 w-4" />
              {isUploading ? 'Running pipeline…' : 'Start validation run'}
            </button>
            <button
              type="button"
              onClick={() => { setFile(null); setProgress(0); setResult(null); setError(null) }}
              className="inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 ring-1 ring-slate-200 transition hover:bg-slate-50"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
          </div>
        </Card>

        <Card header="Pipeline result" subtitle="Output from the ML prediction and correction engine.">
          {!result && !error && (
            <p className="py-8 text-center text-slate-400 text-sm">Upload an invoice to see results here.</p>
          )}

          {error && (
            <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-700">
              <strong>Error:</strong> {error}
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 rounded-2xl bg-emerald-50 px-4 py-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                <span className="font-semibold text-emerald-700">{result.status}</span>
              </div>

              <dl className="grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl bg-slate-50 p-3">
                  <dt className="text-slate-500">Total invoices</dt>
                  <dd className="text-xl font-bold text-slate-900">{result.summary?.totalInvoices ?? '—'}</dd>
                </div>
                <div className="rounded-xl bg-slate-50 p-3">
                  <dt className="text-slate-500">Success rate</dt>
                  <dd className="text-xl font-bold text-emerald-600">{result.summary?.successRate ?? '—'}%</dd>
                </div>
                <div className="rounded-xl bg-slate-50 p-3">
                  <dt className="text-slate-500">Valid mappings</dt>
                  <dd className="text-xl font-bold text-slate-900">{result.summary?.validMappings ?? '—'}</dd>
                </div>
                <div className="rounded-xl bg-amber-50 p-3">
                  <dt className="text-amber-600">Errors corrected</dt>
                  <dd className="text-xl font-bold text-amber-700">{result.summary?.invalidMappings ?? '—'}</dd>
                </div>
              </dl>

              <div className="space-y-1 text-xs text-slate-400">
                <p className="font-semibold text-slate-500 uppercase tracking-wide">Outputs generated</p>
                {(result.outputs || []).map((o) => (
                  <p key={o} className="font-mono">{o}</p>
                ))}
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}