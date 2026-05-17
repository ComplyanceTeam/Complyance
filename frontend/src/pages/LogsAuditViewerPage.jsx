import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import AuditLogTable from '../components/logs/AuditLogTable'
import { auditApi } from '../services/api'
import { auditLogs } from '../data/mockData'

export default function LogsAuditViewerPage() {
  const [rows, setRows] = useState(auditLogs)

  useEffect(() => {
    let mounted = true

    auditApi.getLogs().then((data) => {
      if (mounted) {
        setRows(data)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <Card header="Logs and audit viewer" subtitle="Operational history of validation, correction, and pipeline progression events.">
      <AuditLogTable rows={rows} />
    </Card>
  )
}