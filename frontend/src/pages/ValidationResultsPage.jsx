import { useEffect, useState } from 'react'
import Card from '../components/ui/Card'
import ValidationTable from '../components/validation/ValidationTable'
import { validationApi } from '../services/api'
import { validationResults } from '../data/mockData'

export default function ValidationResultsPage() {
  const [rows, setRows] = useState(validationResults)

  useEffect(() => {
    let mounted = true

    validationApi.getResults().then((data) => {
      if (mounted) {
        setRows(data)
      }
    })

    return () => {
      mounted = false
    }
  }, [])

  return (
    <Card header="Validation results" subtitle="Invoice exceptions with corrections and final validation state.">
      <ValidationTable rows={rows} />
    </Card>
  )
}