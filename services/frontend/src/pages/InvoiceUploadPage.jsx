import { useState } from 'react'
import { FileWarning, UploadCloud } from 'lucide-react'
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
    setFeedback(['File type accepted', 'Column headers validated', 'Mapping preview ready'])
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
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card header="Batch Ingestion" subtitle="Upload invoice datasets for processing">
            <UploadDropzone file={file} onFileSelect={handleFileSelect} progress={progress} feedback={feedback} isUploading={isUploading} />

            <div className="mt-8 flex items-center gap-3">
              <button
                type="button"
                onClick={startUpload}
                className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-5 py-2.5 text-xs font-bold text-white transition hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm active:scale-95"
                disabled={!file || isUploading}
              >
                <UploadCloud className="h-4 w-4" />
                {isUploading ? 'PROCESSING...' : 'START VALIDATION'}
              </button>
              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-lg bg-white px-5 py-2.5 text-xs font-bold text-slate-500 border border-slate-200 transition hover:bg-slate-50 active:scale-95"
                onClick={() => {
                  setFile(null)
                  setProgress(0)
                  setFeedback(uploadFeedback)
                }}
              >
                RESET
              </button>
            </div>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card header="Validation Rules" subtitle="Pre-ingestion compliance checks">
            <div className="space-y-4">
              {[
                'Schema Consistency',
                'Data Normalization',
                'Structural Integrity',
              ].map((item, idx) => (
                <div key={item} className="flex items-start gap-3 p-4 rounded-xl border border-slate-50 bg-slate-50/30">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-white border border-slate-100 text-[10px] font-black text-slate-400">
                    0{idx + 1}
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-900">{item}</p>
                    <p className="text-[10px] text-slate-400 font-medium leading-relaxed mt-0.5">Applied to all batch records before pipeline entry.</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}