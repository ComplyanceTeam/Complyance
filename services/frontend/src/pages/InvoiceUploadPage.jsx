import { useState } from 'react'
import { FileWarning, UploadCloud, RefreshCw } from 'lucide-react'
import Card from '../components/ui/Card'
import UploadDropzone from '../components/upload/UploadDropzone'
import { invoiceApi } from '../services/api'
import { uploadFeedback } from '../data/mockData'

export default function InvoiceUploadPage() {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [feedback, setFeedback] = useState(uploadFeedback)

  const handleFileSelect = (nextFile) => {
    setFile(nextFile)
    setProgress(12)
    setFeedback(['Payload detected', 'Schema mapped', 'Ingestion ready'])
  }

  const startUpload = async () => {
    if (!file || isUploading) return
    setIsUploading(true)
    setProgress(18)
    const intervalId = window.setInterval(() => {
      setProgress((current) => Math.min(current + 16, 94))
    }, 240)
    try {
      const response = await invoiceApi.uploadInvoice(file)
      window.clearInterval(intervalId)
      setProgress(100)
      setFeedback(response.warnings)
    } finally {
      window.clearInterval(intervalId)
      setIsUploading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-10">
      <div className="text-center">
        <h1 className="text-3xl font-black text-slate-900 tracking-tighter uppercase">Batch Ingestion Terminal</h1>
        <p className="mt-2 text-xs font-bold text-slate-400 uppercase tracking-[0.3em]">Initialize automated transformation sequence</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card 
            header="Source Ingestion" 
            subtitle="Upload datasets for ML-driven validation"
            action={
              <button 
                onClick={() => { setFile(null); setProgress(0); setFeedback(uploadFeedback); }}
                className="p-2 rounded-lg bg-slate-50 text-slate-400 hover:text-slate-900 transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            }
          >
            <UploadDropzone file={file} onFileSelect={handleFileSelect} progress={progress} feedback={feedback} isUploading={isUploading} />

            <div className="mt-10 flex items-center justify-center">
              <button
                type="button"
                onClick={startUpload}
                className="btn-primary px-12 py-4 text-xs tracking-[0.2em] shadow-2xl shadow-slate-900/20"
                disabled={!file || isUploading}
              >
                <UploadCloud className="h-5 w-5" />
                {isUploading ? 'INGESTING...' : 'INITIALIZE PIPELINE'}
              </button>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card header="Compliance Core" subtitle="Active validation rules">
            <div className="space-y-6">
              {[
                { label: 'Syntax Integrity', desc: 'Validates UBL/CII structural requirements.' },
                { label: 'Tax Geometry', desc: 'Recalculates VAT totals with 0.01 tolerance.' },
                { label: 'Cross-Border', desc: 'Resolves country-specific format mandates.' },
              ].map((item, idx) => (
                <div key={item.label} className="group">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-[10px] font-black text-slate-300">0{idx + 1}</span>
                    <p className="text-[11px] font-black text-slate-900 uppercase tracking-widest">{item.label}</p>
                  </div>
                  <p className="text-[10px] font-bold text-slate-400 leading-relaxed pl-7">{item.desc}</p>
                </div>
              ))}
            </div>
          </Card>
          
          <div className="p-6 rounded-2xl bg-slate-900 text-white shadow-xl shadow-slate-900/10">
             <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                <span className="text-[10px] font-black uppercase tracking-widest">Engine Active</span>
             </div>
             <p className="text-[11px] font-bold text-white/50 leading-relaxed">
               Securely processing invoices using deterministic rulesets and XGBoost supervisors.
             </p>
          </div>
        </div>
      </div>
    </div>
  )
}
