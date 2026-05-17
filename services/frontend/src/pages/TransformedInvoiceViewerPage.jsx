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
      if (mounted) {
        setInvoice(data)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <Card header="Transformed invoice viewer" subtitle="Syntax-highlighted JSON preview of the normalized target invoice payload.">
      <JsonViewer data={invoice} />
    </Card>
  )
}