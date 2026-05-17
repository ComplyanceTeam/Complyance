import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import ValidationTable from '../components/validation/ValidationTable'
import { validationApi } from '../services/api'

export default function ValidationResultsPage() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    validationApi.getResults()
      .then((data) => { if (mounted) setRows(Array.isArray(data) ? data : []) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  return (
    <Card header="Validation results" subtitle="Invoice exceptions detected by the ML engine with corrections applied.">
      {loading ? (
        <p className="py-8 text-center text-slate-400">Loading validation results…</p>
      ) : rows.length === 0 ? (
        <p className="py-8 text-center text-slate-400">No validation results found. Upload an invoice to run the pipeline.</p>
      ) : (
        <ValidationTable rows={rows} />
      )}
    </Card>
  )
}