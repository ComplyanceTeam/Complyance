import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import AuditLogTable from '../components/logs/AuditLogTable'
import { auditApi } from '../services/api'

export default function LogsAuditViewerPage() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    auditApi.getLogs()
      .then((data) => { if (mounted) setRows(Array.isArray(data) ? data : []) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [])

  return (
    <Card header="Logs and audit viewer" subtitle="Operational history of validation, correction, and pipeline events.">
      {loading ? (
        <p className="py-8 text-center text-slate-400">Loading audit logs…</p>
      ) : rows.length === 0 ? (
        <p className="py-8 text-center text-slate-400">No logs available. Upload an invoice to run the pipeline.</p>
      ) : (
        <AuditLogTable rows={rows} />
      )}
    </Card>
  )
}