import { CloudUpload, FileCheck2, FileText, LoaderCircle } from 'lucide-react'

export default function UploadDropzone({
  file,
  onFileSelect,
  progress,
  feedback = [],
  isUploading,
}) {
  const handleDrop = (event) => {
    event.preventDefault()

    const droppedFile = event.dataTransfer.files?.[0]
    if (droppedFile) {
      onFileSelect(droppedFile)
    }
  }

  return (
    <div className="space-y-4">
      <div
        className="group rounded-3xl border-2 border-dashed border-slate-200 bg-white/90 p-8 text-center shadow-sm transition hover:border-blue-300 hover:bg-blue-50/40"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-lg shadow-slate-200">
          <CloudUpload className="h-7 w-7" />
        </div>

        <h3 className="mt-5 text-lg font-semibold text-slate-900">Upload invoice dataset</h3>
        <p className="mt-2 text-sm text-slate-500">Drag and drop a CSV file or select one from your computer.</p>

        <label className="mt-6 inline-flex cursor-pointer items-center gap-2 rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800">
          <FileText className="h-4 w-4" />
          Choose CSV file
          <input
            type="file"
            accept=".csv,.json,.xml"
            className="hidden"
            onChange={(event) => onFileSelect(event.target.files?.[0])}
          />
        </label>

        {file && (
          <div className="mt-6 inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm text-slate-700">
            <FileCheck2 className="h-4 w-4 text-emerald-600" />
            {file.name}
          </div>
        )}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>Upload progress</span>
          <span>{progress}%</span>
        </div>

        <div className="mt-3 h-2 rounded-full bg-slate-100">
          <div className="h-2 rounded-full bg-gradient-to-r from-blue-600 to-cyan-500 transition-all" style={{ width: `${progress}%` }} />
        </div>

        <div className="mt-4 flex items-center gap-2 text-sm text-slate-600">
          {isUploading ? <LoaderCircle className="h-4 w-4 animate-spin text-blue-600" /> : <FileCheck2 className="h-4 w-4 text-emerald-600" />}
          <span>{isUploading ? 'Validating upload payload and headers...' : 'Upload validation ready.'}</span>
        </div>

        {!!feedback.length && (
          <div className="mt-4 grid gap-2 sm:grid-cols-3">
            {feedback.map((item) => (
              <div key={item} className="rounded-2xl bg-slate-50 px-3 py-2 text-xs font-medium text-slate-600">
                {item}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}