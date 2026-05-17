import axios from 'axios'

const envUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const API_BASE = envUrl.endsWith('/api') ? envUrl : `${envUrl}/api`

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 300000,  // 5 min — pipeline processes can take time on large files
})

// ── Generic request helper ──────────────────────────────
const get = (path) => apiClient.get(path).then((r) => r.data)
const post = (path, data, config) => apiClient.post(path, data, config).then((r) => r.data)

// ── Dashboard ───────────────────────────────────────────
export const dashboardApi = {
  getSummary: () => get('/dashboard/summary'),
  getPipelineStages: () => get('/dashboard/pipeline-stages'),
  getRecentActivity: () => get('/dashboard/activity'),
}

// ── Validation ──────────────────────────────────────────
export const validationApi = {
  getResults: () => get('/validation/results'),
}

// ── Invoice ─────────────────────────────────────────────
export const invoiceApi = {
  getTransformedInvoice: () => get('/invoice/transformed'),
  uploadInvoice: async (file) => {
    const form = new FormData()
    form.append('file', file)
    return post('/invoice/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ── Analytics ───────────────────────────────────────────
export const analyticsApi = {
  getAnalytics: () => get('/analytics/summary'),
}

// ── Audit ───────────────────────────────────────────────
export const auditApi = {
  getLogs: () => get('/audit/logs'),
}