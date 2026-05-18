import axios from 'axios'
import {
  analyticsData,
  auditLogs,
  dashboardSummary,
  transformedInvoice,
  uploadFeedback,
  validationResults,
} from '../data/mockData'

const useMockApi = import.meta.env.VITE_USE_MOCK_API === 'true'

// Dynamic discovery of backend URL
const getBaseURL = () => {
    // If explicitly set in environment, use it
    if (import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL !== 'undefined') {
        return import.meta.env.VITE_API_BASE_URL
    }
    
    // Default to localhost if on localhost, otherwise use current hostname
    const { protocol, hostname } = window.location
    const port = 3001
    
    // Safety check for empty hostname (e.g. some webview environments)
    const activeHost = hostname || 'localhost'
    return `${protocol}//${activeHost}:${port}`
}

console.log('API Service initialized with BaseURL:', getBaseURL())

export const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
  }
})

const withDelay = (payload, delay = 250) =>
  new Promise((resolve) => {
    window.setTimeout(() => resolve(payload), delay)
  })

const requestData = async (loader, payload) => {
  if (useMockApi) {
    return withDelay(payload)
  }

  try {
    const response = await loader()
    return response?.data ?? response
  } catch (error) {
    console.warn('Backend reachability issue, using fallback data.', error.message)
    return withDelay(payload)
  }
}

export const dashboardApi = {
  getSummary: () => requestData(() => apiClient.get('/api/dashboard/stats'), dashboardSummary),
  
  getPipelineStages: () => requestData(() => withDelay(dashboardSummary.pipelineStages), dashboardSummary.pipelineStages),
  
  getRecentActivity: () => requestData(async () => {
    const res = await apiClient.get('/api/history?limit=10')
    const data = res.data
    if (!data || !Array.isArray(data) || data.length === 0) return dashboardSummary.recentActivity
    
    return data.map(r => ({
      id: r.invoice_id,
      status: r.is_mapping_valid ? 'validated' : 'corrected',
      country: (r.target_format || 'XX').split('_').pop().toUpperCase(),
      updatedAt: new Date(r.created_at).toLocaleTimeString(),
      owner: 'ML Supervisor'
    }))
  }, dashboardSummary.recentActivity),
}

export const validationApi = {
  getResults: () => requestData(async () => {
    const res = await apiClient.get('/api/history?limit=100')
    const data = res.data
    if (!data || !Array.isArray(data) || data.length === 0) return validationResults

    return data.map(r => ({
      invoice_id: r.invoice_id,
      error_type: r.mapping_errors || 'None',
      severity: r.is_mapping_valid ? 'Low' : 'High',
      corrected_fields: r.is_mapping_valid ? 'None' : 'Repaired',
      validation_status: r.is_mapping_valid ? 'Valid' : 'Invalid'
    }))
  }, validationResults),
}

export const auditApi = {
  getLogs: () => requestData(async () => {
    const res = await apiClient.get('/api/history?limit=100')
    const data = res.data
    if (!data || !Array.isArray(data) || data.length === 0) return auditLogs

    return data.map(r => ({
      id: r.id,
      timestamp: new Date(r.created_at).toLocaleString(),
      actor: 'ML Supervisor',
      event: 'Transcode Applied',
      target: r.invoice_id,
      details: `Target: ${r.target_format}. ${r.mapping_errors ? 'Errors fixed: ' + r.mapping_errors : 'Validation passed.'}`
    }))
  }, auditLogs),
}

export const invoiceApi = {
  getTransformedInvoice: () => requestData(async () => {
    const res = await apiClient.get('/api/history?limit=1')
    const data = res.data
    if (!data || !Array.isArray(data) || data.length === 0) return transformedInvoice
    return data[0]?.transcoded_payload || transformedInvoice
  }, transformedInvoice),
  
  uploadInvoice: async (invoiceData) => {
    console.log('POST -> /api/transcode', invoiceData.invoice_id)
    return apiClient.post('/api/transcode', invoiceData)
  },
}

export const analyticsApi = {
  getAnalytics: () => requestData(() => apiClient.get('/api/history?limit=50'), analyticsData),
}
