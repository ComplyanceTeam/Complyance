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
    if (droppedFile) onFileSelect(droppedFile)
  }

  return (
    <div className="space-y-8">
      <div
        className="group relative rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50/50 p-12 text-center transition-all hover:border-slate-400 hover:bg-white"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
      >
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-2xl shadow-slate-900/20 group-hover:scale-105 transition-transform duration-300">
          <CloudUpload className="h-8 w-8" />
        </div>

        <h3 className="mt-8 text-lg font-black tracking-tight text-slate-900">Ingest Data Batch</h3>
        <p className="mt-2 text-sm font-bold text-slate-400 uppercase tracking-widest">CSV • JSON • XML</p>

        <label className="mt-8 inline-flex cursor-pointer items-center gap-2 rounded-xl bg-slate-900 px-6 py-3 text-xs font-black text-white shadow-xl shadow-slate-900/10 hover:bg-slate-800 transition-all active:scale-95 uppercase tracking-widest">
          <FileText className="h-4 w-4" />
          Select Source
          <input
            type="file"
            accept=".csv,.json,.xml"
            className="hidden"
            onChange={(event) => onFileSelect(event.target.files?.[0])}
          />
        </label>

        {file && (
          <div className="mt-8 flex items-center justify-center">
            <div className="inline-flex items-center gap-2 rounded-lg bg-emerald-50 px-4 py-2 text-[10px] font-black text-emerald-600 border border-emerald-100 uppercase tracking-widest">
              <FileCheck2 className="h-4 w-4" />
              {file.name}
            </div>
          </div>
        )}
      </div>

      <div className="space-y-4 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
        <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">
          <span>Upload Sequence</span>
          <span className="text-slate-900">{progress}%</span>
        </div>

        <div className="h-1.5 w-full rounded-full bg-slate-100 overflow-hidden">
          <div 
            className="h-full bg-slate-900 transition-all duration-500 ease-out" 
            style={{ width: `${progress}%` }} 
          />
        </div>

        <div className="flex items-center gap-3 pt-2">
          {isUploading ? (
            <LoaderCircle className="h-5 w-5 animate-spin text-slate-900" />
          ) : (
            <div className="h-5 w-5 items-center justify-center flex rounded-full bg-emerald-500 text-white">
               <FileCheck2 className="h-3 w-3" />
            </div>
          )}
          <span className="text-xs font-bold text-slate-900">
            {isUploading ? 'Validating schema payloads...' : 'Batch verification successful.'}
          </span>
        </div>

        {!!feedback.length && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6">
            {feedback.map((item) => (
              <div key={item} className="p-3 rounded-xl border border-slate-50 bg-slate-50/50 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">
                {item}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
