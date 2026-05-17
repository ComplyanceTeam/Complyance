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
    if (!file || isUploading) {
      return
    }

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
      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <Card header="Invoice upload" subtitle="Drag and drop a CSV, XML, or JSON invoice dataset for pipeline ingestion.">
          <UploadDropzone file={file} onFileSelect={handleFileSelect} progress={progress} feedback={feedback} isUploading={isUploading} />

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={startUpload}
              className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={!file || isUploading}
            >
              <UploadCloud className="h-4 w-4" />
              {isUploading ? 'Uploading...' : 'Start validation run'}
            </button>
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-2xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 ring-1 ring-slate-200 transition hover:bg-slate-50"
              onClick={() => {
                setFile(null)
                setProgress(0)
                setFeedback(uploadFeedback)
              }}
            >
              Reset
            </button>
          </div>
        </Card>

        <Card header="Upload validation feedback" subtitle="Pre-ingestion checks applied to the file before pipeline execution.">
          <div className="space-y-4 text-sm text-slate-600">
            {[
              'Column headers match the canonical invoice schema.',
              'Date and currency fields were normalized successfully.',
              'No structural violations were detected in the sample window.',
            ].map((item) => (
              <div key={item} className="flex items-start gap-3 rounded-2xl bg-slate-50 px-4 py-3">
                <FileWarning className="mt-0.5 h-4 w-4 text-amber-500" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}