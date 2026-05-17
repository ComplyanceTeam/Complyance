export const formatNumber = (value) => new Intl.NumberFormat('en-US').format(value)

export const formatPercent = (value) => `${value.toFixed(1)}%`

export const formatCurrency = (value, currency = 'USD') =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value)

export const formatDuration = (seconds) => `${seconds.toFixed(1)}s`

export const formatDateTime = (value) => {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export const statusTone = (status) => {
  const normalized = String(status || '').toLowerCase()

  if (['completed', 'resolved', 'corrected', 'valid', 'passed'].includes(normalized)) {
    return 'success'
  }

  if (['active', 'in progress', 'processing'].includes(normalized)) {
    return 'info'
  }

  if (['queued', 'pending', 'warning', 'medium'].includes(normalized)) {
    return 'warning'
  }

  if (['failed', 'escalated', 'error', 'high'].includes(normalized)) {
    return 'danger'
  }

  return 'neutral'
}

export const prettyJson = (value) => JSON.stringify(value, null, 2)