import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import JsonViewer from '../components/viewer/JsonViewer'
import { invoiceApi } from '../services/api'
import { transformedInvoice } from '../data/mockData'

export default function TransformedInvoiceViewerPage() {
  const [invoice, setInvoice] = useState(transformedInvoice)

  useEffect(() => {
    let mounted = true
    invoiceApi.getTransformedInvoice().then((data) => {
      if (mounted) setInvoice(data)
    })
    return () => { mounted = false }
  }, [])

  return (
    <div className="space-y-6">
      <Card header="Target Payload Preview" subtitle="Normalized JSON output after transformation and validation">
        <div className="bg-slate-900 rounded-xl p-6 overflow-hidden">
          <JsonViewer data={invoice} />
        </div>
      </Card>
    </div>
  )
}