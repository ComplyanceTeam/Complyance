import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import ValidationTable from '../components/validation/ValidationTable'
import { validationApi } from '../services/api'
import { validationResults } from '../data/mockData'
import Modal from '../components/ui/Modal'
import JsonViewer from '../components/viewer/JsonViewer'

export default function ValidationResultsPage() {
  const [rows, setRows] = useState(validationResults)
  const [selectedRow, setSelectedRow] = useState(null)
  const [viewMode, setViewMode] = useState('validation') // 'validation' or 'target'

  useEffect(() => {
    let mounted = true

    validationApi.getResults().then((data) => {
      if (mounted) {
        setRows(data)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <>
      <Card header="Validation results" subtitle="Invoice exceptions with corrections and final validation state.">
        <ValidationTable rows={rows} onRowClick={setSelectedRow} />
      </Card>
      
      <Modal 
        isOpen={!!selectedRow} 
        onClose={() => setSelectedRow(null)}
        title={`Result: ${selectedRow?.invoice_id || ''}`}
      >
        {selectedRow && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4 bg-slate-50 p-1 rounded-lg w-max">
              <button
                onClick={() => setViewMode('validation')}
                className={`px-4 py-2 text-xs font-black uppercase tracking-widest rounded-md transition-colors ${
                  viewMode === 'validation' 
                    ? 'bg-slate-900 text-white shadow-md' 
                    : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                Validation Details
              </button>
              <button
                onClick={() => setViewMode('target')}
                className={`px-4 py-2 text-xs font-black uppercase tracking-widest rounded-md transition-colors ${
                  viewMode === 'target' 
                    ? 'bg-slate-900 text-white shadow-md' 
                    : 'text-slate-500 hover:text-slate-900'
                }`}
              >
                Target Output
              </button>
            </div>
            
            <div className="bg-slate-900 rounded-xl p-6 overflow-x-auto">
              {viewMode === 'validation' ? (
                <JsonViewer data={{
                  invoice_id: selectedRow.invoice_id,
                  error_type: selectedRow.error_type,
                  severity: selectedRow.severity,
                  corrected_fields: selectedRow.corrected_fields,
                  validation_status: selectedRow.validation_status
                }} />
              ) : (
                <JsonViewer data={selectedRow.transcoded_payload || { message: "No target output available" }} />
              )}
            </div>
          </div>
        )}
      </Modal>
    </>
  )
}