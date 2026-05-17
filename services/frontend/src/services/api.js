import axios from 'axios'
import {
  analyticsData,
  auditLogs,
  dashboardSummary,
  transformedInvoice,
  uploadFeedback,
  validationResults,
} from '../data/mockData'

const useMockApi = import.meta.env.VITE_USE_MOCK_API !== 'false'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api',
  timeout: 15000,
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
  } catch {
    return withDelay(payload)
  }
}

export const dashboardApi = {
  getSummary: () => requestData(() => apiClient.get('/dashboard/summary'), dashboardSummary),
  getPipelineStages: () => requestData(() => apiClient.get('/dashboard/pipeline-stages'), dashboardSummary.pipelineStages),
  getRecentActivity: () => requestData(() => apiClient.get('/dashboard/activity'), dashboardSummary.recentActivity),
}

export const validationApi = {
  getResults: () => requestData(() => apiClient.get('/validation/results'), validationResults),
}

export const invoiceApi = {
  getTransformedInvoice: () => requestData(() => apiClient.get('/invoice/transformed'), transformedInvoice),
  uploadInvoice: async (file) => {
    const mockResponse = {
      fileName: file?.name || 'invoice.csv',
      status: 'Uploaded',
      accepted: true,
      warnings: uploadFeedback,
    }

    return requestData(() => apiClient.post('/invoice/upload', file), mockResponse)
  },
}

export const analyticsApi = {
  getAnalytics: () => requestData(() => apiClient.get('/analytics/summary'), analyticsData),
}

export const auditApi = {
  getLogs: () => requestData(() => apiClient.get('/audit/logs'), auditLogs),
}