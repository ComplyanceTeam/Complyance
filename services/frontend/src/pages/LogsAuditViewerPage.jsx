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
      if (mounted) setRows(data)
    })
    return () => { mounted = false }
  }, [])

  return (
    <div className="space-y-6">
      <Card header="Operational Audit Log" subtitle="History of pipeline execution and system events">
        <AuditLogTable rows={rows} />
      </Card>
    </div>
  )
}