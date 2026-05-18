import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import JsonViewer from '../components/viewer/JsonViewer'
import { invoiceApi } from '../services/api'

export default function TransformedInvoiceViewerPage() {
  const [invoice, setInvoice] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true
    invoiceApi.getTransformedInvoice()
      .then((data) => { if (mounted) setInvoice(data) })
      .catch((e) => { if (mounted) setError(e?.response?.data?.detail || e.message) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  return (
    <Card header="Transformed invoice viewer" subtitle="Syntax-highlighted JSON preview of the normalised target invoice payload.">
      {loading && <p className="py-8 text-center text-slate-400">Loading transformed invoice…</p>}
      {!loading && error && (
        <p className="py-8 text-center text-slate-400">{error} — upload an invoice first.</p>
      )}
      {!loading && invoice && <JsonViewer data={invoice} />}
    </Card>
  )
}