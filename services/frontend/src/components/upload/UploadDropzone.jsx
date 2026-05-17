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
    <div className="space-y-6">
      <div
        className="group relative rounded-[2.5rem] border-2 border-dashed border-slate-200 bg-white/60 p-12 text-center transition-all hover:border-blue-400 hover:bg-blue-50/30"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-[2rem] bg-slate-900 text-white shadow-2xl shadow-slate-900/20 transition-transform group-hover:scale-110">
          <CloudUpload className="h-8 w-8" />
        </div>

        <h3 className="mt-8 text-xl font-black tracking-tight text-slate-900">Import invoice dataset</h3>
        <p className="mx-auto mt-2 max-w-xs text-sm font-medium leading-relaxed text-slate-400">
          Drop your batch file here (.csv, .json, .xml) or use the manual selector below.
        </p>

        <label className="mt-8 inline-flex cursor-pointer items-center gap-2 rounded-2xl bg-slate-900 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-slate-900/10 transition hover:bg-slate-800 active:scale-95">
          <FileText className="h-4 w-4" />
          Choose Source File
          <input
            type="file"
            accept=".csv,.json,.xml"
            className="hidden"
            onChange={(event) => onFileSelect(event.target.files?.[0])}
          />
        </label>

        {file && (
          <div className="mt-8 flex items-center justify-center gap-2">
            <div className="inline-flex items-center gap-2 rounded-2xl bg-emerald-50 px-4 py-2 text-xs font-bold text-emerald-700 ring-1 ring-emerald-200">
              <FileCheck2 className="h-4 w-4" />
              {file.name}
            </div>
          </div>
        )}
      </div>

      <div className="rounded-[2rem] border border-slate-200/60 bg-white/80 p-6 shadow-sm">
        <div className="flex items-center justify-between text-[11px] font-black uppercase tracking-widest text-slate-400">
          <span>Processing Ingestion</span>
          <span className="text-slate-900">{progress}%</span>
        </div>

        <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
          <div 
            className="h-full rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-500" 
            style={{ width: `${progress}%` }} 
          />
        </div>

        <div className="mt-6 flex items-center gap-3">
          <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${isUploading ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}`}>
            {isUploading ? <LoaderCircle className="h-5 w-5 animate-spin" /> : <FileCheck2 className="h-5 w-5" />}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-bold text-slate-900">{isUploading ? 'Validating schema...' : 'Ingestion complete'}</p>
            <p className="text-xs font-medium text-slate-400">{isUploading ? 'Checking batch consistency' : 'Ready for transformation'}</p>
          </div>
        </div>

        {!!feedback.length && (
          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
            {feedback.map((item) => (
              <div key={item} className="flex items-center gap-2 rounded-2xl border border-slate-100 bg-slate-50/50 px-4 py-3 text-xs font-bold text-slate-600">
                <div className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                {item}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}