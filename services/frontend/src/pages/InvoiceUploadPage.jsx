import { useState } from 'react'
import { FileWarning, UploadCloud, RefreshCw } from 'lucide-react'
import Card from '../components/ui/Card'
import UploadDropzone from '../components/upload/UploadDropzone'
import { invoiceApi } from '../services/api'
import { uploadFeedback } from '../data/mockData'
import JsonViewer from '../components/viewer/JsonViewer'
import Modal from '../components/ui/Modal'

export default function InvoiceUploadPage() {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [feedback, setFeedback] = useState(uploadFeedback)
  const [resultPayload, setResultPayload] = useState(null)
  const [isResultModalOpen, setIsResultModalOpen] = useState(false)

  const handleFileSelect = (nextFile) => {
    setFile(nextFile)
    setProgress(12)
    setFeedback(['Payload detected', 'Schema mapped', 'Ingestion ready'])
    setResultPayload(null)
    setIsResultModalOpen(false)
  }

  const startUpload = async () => {
    if (!file || isUploading) return
    setIsUploading(true)
    setProgress(18)
    
    const intervalId = window.setInterval(() => {
      setProgress((current) => Math.min(current + 5, 94))
    }, 1000)

    try {
      const fileName = file.name.toLowerCase()
      const fileExt = fileName.split('.').pop()
      const isJson = fileExt === 'json'
      const isCsv = fileExt === 'csv'
      const isXml = fileExt === 'xml'

      if (!isJson && !isCsv && !isXml) {
        throw new Error('Unsupported file type. Please upload a CSV, JSON, or XML invoice file.')
      }

      let response

      if (isJson) {
        const text = await file.text()
        if (!text.trim()) {
          throw new Error('Selected file is empty.')
        }

        let invoiceData
        try {
          const sanitizedText = text.replace(/:\s*NaN/g, ': null')
          invoiceData = JSON.parse(sanitizedText)

          if (Array.isArray(invoiceData)) {
            if (invoiceData.length === 0) throw new Error('JSON array is empty.')
            invoiceData = invoiceData[0]
          }

          if (!invoiceData || typeof invoiceData !== 'object') {
            throw new Error('Parsed data is not a valid invoice object.')
          }

          // Sanitize types for backend strict validation
          const stringFields = ['invoice_id', 'source_format', 'target_country', 'seller_id', 'buyer_id', 'issue_date', 'currency']
          stringFields.forEach(field => {
            if (invoiceData[field] !== undefined && invoiceData[field] !== null) {
              invoiceData[field] = String(invoiceData[field])
            }
          })

          if (invoiceData.line_items_json && typeof invoiceData.line_items_json !== 'string') {
            invoiceData.line_items_json = JSON.stringify(invoiceData.line_items_json)
          }
        } catch (err) {
          console.error('Parsing error:', err)
          throw new Error('Invalid JSON format. Please upload a valid invoice object (malformed syntax or unsupported values).')
        }

        console.log('Initiating pipeline for:', invoiceData.invoice_id)
        response = await invoiceApi.uploadInvoice(invoiceData)
      } else {
        console.log('Initiating pipeline file upload for:', file.name)
        response = await invoiceApi.uploadInvoiceFile(file)
      }
      
      if (!response || !response.data) {
          throw new Error('Backend returned an empty response.')
      }

      window.clearInterval(intervalId)
      setProgress(100)
      
      const result = response.data
      setFeedback([
          `Status: Processed`,
          `Target: ${result.target_format || 'Auto'}`,
          `Integrity: ${result.is_mapping_valid ? 'Verified' : 'Flagged'}`,
          `Findings: ${result.mapping_errors || 'None'}`
      ])
      
      if (result.transcoded_payload) {
          setResultPayload(result.transcoded_payload)
      } else if (result.original_payload) {
          setResultPayload(result.original_payload)
      } else {
          setResultPayload(result)
      }
      setIsResultModalOpen(true)
      
    } catch (err) {
      console.error('Upload Error:', err)
      let errorMsg = err.message || 'Unknown network error'
      
      // Handle FastAPI 422 Validation Errors (which are objects/arrays)
      if (err.response?.status === 422) {
          const details = err.response?.data?.detail
          if (Array.isArray(details)) {
              errorMsg = `Validation Error: ${details.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', ')}`
          } else if (typeof details === 'object') {
              errorMsg = `Validation Error: ${JSON.stringify(details)}`
          } else {
              errorMsg = details || errorMsg
          }
      } else {
          errorMsg = err.response?.data?.detail || errorMsg
      }

      setFeedback([`Execution Failed: ${errorMsg}`])
      window.clearInterval(intervalId)
      setProgress(0)
      setResultPayload(null)
      setIsResultModalOpen(false)
    } finally {
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
                onClick={() => { setFile(null); setProgress(0); setFeedback(uploadFeedback); setResultPayload(null); setIsResultModalOpen(false); }}
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

          <Modal 
            isOpen={isResultModalOpen} 
            onClose={() => setIsResultModalOpen(false)}
            title="Transformed Payload Result"
          >
            {resultPayload && (
              <div className="bg-slate-900 rounded-xl p-6 overflow-x-auto">
                <JsonViewer data={resultPayload} />
              </div>
            )}
          </Modal>
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
