export const dashboardSummary = {
  totals: {
    invoicesReceived: 1842,
    invoicesValidated: 1728,
    invoicesTransformed: 1659,
    successRate: 96.2,
    exceptionRate: 3.8,
    averageProcessingTime: '1.8s',
  },
  pipelineStages: [
    { name: 'Ingestion', status: 'completed', throughput: 98, latency: '0.4s' },
    { name: 'Pre-validation', status: 'completed', throughput: 97, latency: '0.3s' },
    { name: 'Format determination', status: 'active', throughput: 93, latency: '0.4s' },
    { name: 'Transformation', status: 'active', throughput: 95, latency: '0.5s' },
    { name: 'Post-validation', status: 'active', throughput: 92, latency: '0.2s' },
    { name: 'Error correction', status: 'queued', throughput: 84, latency: '0.0s' },
    { name: 'Output generation', status: 'queued', throughput: 99, latency: '0.0s' },
  ],
  recentActivity: [
    { id: 'INV-1042', status: 'validated', country: 'DE', updatedAt: '2 min ago', owner: 'Processing Bot' },
    { id: 'INV-1043', status: 'corrected', country: 'FR', updatedAt: '5 min ago', owner: 'Validation Service' },
    { id: 'INV-1044', status: 'transformed', country: 'US', updatedAt: '8 min ago', owner: 'Format Resolver' },
    { id: 'INV-1045', status: 'flagged', country: 'IN', updatedAt: '11 min ago', owner: 'Audit Engine' },
  ],
  validationSummary: [
    { label: 'Structure checks', value: 99.1 },
    { label: 'Mapping accuracy', value: 97.6 },
    { label: 'Field completeness', value: 96.8 },
    { label: 'Tax compliance', value: 94.7 },
  ],
  trendData: [
    { name: 'Mon', processed: 142, valid: 134, invalid: 8 },
    { name: 'Tue', processed: 168, valid: 160, invalid: 8 },
    { name: 'Wed', processed: 181, valid: 172, invalid: 9 },
    { name: 'Thu', processed: 156, valid: 149, invalid: 7 },
    { name: 'Fri', processed: 194, valid: 185, invalid: 9 },
    { name: 'Sat', processed: 112, valid: 108, invalid: 4 },
    { name: 'Sun', processed: 98, valid: 95, invalid: 3 },
  ],
  pipelineSplit: [
    { name: 'Completed', value: 78 },
    { name: 'In progress', value: 16 },
    { name: 'Queued', value: 6 },
  ],
}

export const validationResults = [
  {
    invoice_id: 'INV-1042',
    error_type: 'Missing seller VAT',
    severity: 'High',
    corrected_fields: 'seller_vat',
    validation_status: 'Corrected',
  },
  {
    invoice_id: 'INV-1043',
    error_type: 'Country format mismatch',
    severity: 'Medium',
    corrected_fields: 'invoice_date, tax_code',
    validation_status: 'Corrected',
  },
  {
    invoice_id: 'INV-1044',
    error_type: 'Line item total drift',
    severity: 'High',
    corrected_fields: 'line_items.total_amount',
    validation_status: 'Escalated',
  },
  {
    invoice_id: 'INV-1045',
    error_type: 'Unsupported currency code',
    severity: 'Low',
    corrected_fields: 'currency',
    validation_status: 'Resolved',
  },
  {
    invoice_id: 'INV-1046',
    error_type: 'Date parsing warning',
    severity: 'Low',
    corrected_fields: 'issue_date',
    validation_status: 'Resolved',
  },
]

export const transformedInvoice = {
  invoice_id: 'INV-1042',
  country: 'DE',
  target_format: 'XRechnung',
  transformation_status: 'Completed',
  totals: {
    subtotal: 12500,
    tax: 2250,
    grand_total: 14750,
  },
  parties: {
    seller: {
      name: 'Northwind Trading GmbH',
      vat: 'DE123456789',
      address: 'Alexanderplatz 1, Berlin',
    },
    buyer: {
      name: 'Apex Procurement AG',
      vat: 'DE987654321',
      address: 'Industriestrasse 12, Munich',
    },
  },
  line_items: [
    { sku: 'CONS-001', description: 'Compliance consulting', quantity: 10, unit_price: 800 },
    { sku: 'SUP-002', description: 'Invoice validation license', quantity: 5, unit_price: 450 },
  ],
  metadata: {
    corrected_fields: ['seller_vat', 'invoice_date', 'currency'],
    validation_passed: true,
    output_file: 'final_mapped_invoice.xml',
  },
}

export const analyticsData = {
  throughput: [
    { name: 'Week 1', invoices: 380, errors: 15 },
    { name: 'Week 2', invoices: 424, errors: 12 },
    { name: 'Week 3', invoices: 452, errors: 10 },
    { name: 'Week 4', invoices: 498, errors: 9 },
  ],
  severityBreakdown: [
    { name: 'High', value: 24 },
    { name: 'Medium', value: 38 },
    { name: 'Low', value: 58 },
  ],
  countryMix: [
    { name: 'DE', value: 34 },
    { name: 'FR', value: 23 },
    { name: 'US', value: 19 },
    { name: 'IN', value: 17 },
    { name: 'SG', value: 7 },
  ],
  sla: [
    { name: '< 1s', value: 41 },
    { name: '1-3s', value: 47 },
    { name: '> 3s', value: 12 },
  ],
}

export const auditLogs = [
  {
    id: 1,
    timestamp: '2026-05-17 09:42:11',
    actor: 'Validation Service',
    event: 'Validation completed',
    target: 'INV-1042',
    details: 'Passed 48 structural checks with 2 auto-corrections.',
  },
  {
    id: 2,
    timestamp: '2026-05-17 09:41:34',
    actor: 'Correction Engine',
    event: 'Field mapping applied',
    target: 'INV-1043',
    details: 'Mapped deprecated tax code to target-compliant value.',
  },
  {
    id: 3,
    timestamp: '2026-05-17 09:40:58',
    actor: 'Pipeline Orchestrator',
    event: 'Stage advanced',
    target: 'Batch #42',
    details: 'Moved from post-validation to error correction.',
  },
  {
    id: 4,
    timestamp: '2026-05-17 09:39:22',
    actor: 'Audit Engine',
    event: 'Exception created',
    target: 'INV-1045',
    details: 'Currency code flagged for manual review.',
  },
]

export const uploadFeedback = [
  'File type accepted',
  'Column headers validated',
  'Mapping preview ready',
]