import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from '../layouts/AppLayout'
import DashboardPage from '../pages/DashboardPage'
//import AnalyticsDashboardPage from '../pages/AnalyticsDashboardPage'
import InvoiceUploadPage from '../pages/InvoiceUploadPage'
//import LogsAuditViewerPage from '../pages/LogsAuditViewerPage'
import PipelineMonitoringPage from '../pages/PipelineMonitoringPage'
import TransformedInvoiceViewerPage from '../pages/TransformedInvoiceViewerPage'
import ValidationResultsPage from '../pages/ValidationResultsPage'

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="upload" element={<InvoiceUploadPage />} />
          <Route path="pipeline" element={<PipelineMonitoringPage />} />
          <Route path="validation" element={<ValidationResultsPage />} />
          <Route path="viewer" element={<TransformedInvoiceViewerPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}