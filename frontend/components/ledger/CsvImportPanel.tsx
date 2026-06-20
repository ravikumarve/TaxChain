'use client'

import { useState, useRef } from 'react'
import { transactionsApi } from '@/lib/api'
import { Card } from '@/components/ui/Card'

interface CsvRow {
  row: number
  data: Record<string, string>
  warnings: string[]
  errors: string[]
}

interface CsvPreview {
  columns: string[]
  rows: CsvRow[]
  total_rows: number
  valid_rows: number
  error_rows: number
}

export default function CsvImportPanel() {
  const [preview, setPreview] = useState<CsvPreview | null>(null)
  const [loading, setLoading] = useState(false)
  const [committing, setCommitting] = useState(false)
  const [result, setResult] = useState<{ saved: number; total: number; errors: any[] } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setError('Only CSV files are supported')
      return
    }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await transactionsApi.csvPreview(file)
      setPreview(response.data)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to parse CSV')
    } finally {
      setLoading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const handleCommit = async () => {
    if (!fileInputRef.current?.files?.[0]) return
    setCommitting(true)
    setError(null)
    try {
      const response = await transactionsApi.csvCommit(fileInputRef.current.files[0])
      setResult(response.data)
      setPreview(null)
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to import CSV')
    } finally {
      setCommitting(false)
    }
  }

  const renderCell = (value: string | undefined) => {
    if (!value) return <span className="text-faint">—</span>
    return <span className="text-main">{value}</span>
  }

  return (
    <Card className="p-6">
      <h3 className="text-md font-semibold text-main mb-4">CSV Import</h3>

      {/* Drop zone */}
      {!preview && !result && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
            dragOver
              ? 'border-indigo-500/60 bg-indigo-500/5'
              : 'border-border-dim hover:border-indigo-500/30 hover:bg-surface'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileSelect}
          />
          <svg className="mx-auto h-10 w-10 text-muted mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p className="text-sm text-muted mb-1">
            <span className="text-indigo-400 font-medium">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-faint">CSV files only (date, type, token, quantity, price, fee, chain)</p>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-400" />
          <span className="ml-3 text-sm text-muted">Parsing CSV...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-3 bg-loss/10 border border-loss/20 rounded-lg text-loss text-sm">
          {error}
        </div>
      )}

      {/* Preview table */}
      {preview && !loading && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex gap-4 text-sm">
              <span className="text-muted">
                Total: <span className="text-main font-medium">{preview.total_rows}</span>
              </span>
              <span className="text-emerald-400">
                Valid: <span className="font-medium">{preview.valid_rows}</span>
              </span>
              {preview.error_rows > 0 && (
                <span className="text-loss">
                  Errors: <span className="font-medium">{preview.error_rows}</span>
                </span>
              )}
            </div>
          </div>

          {preview.rows.length > 0 && (
            <div className="overflow-x-auto max-h-80 overflow-y-auto border border-border-dim rounded-lg">
              <table className="w-full text-xs">
                <thead className="bg-surface sticky top-0">
                  <tr>
                    <th className="px-3 py-2 text-left text-faint uppercase tracking-wider font-mono w-12">#</th>
                    {preview.columns.map((col) => (
                      <th key={col} className="px-3 py-2 text-left text-faint uppercase tracking-wider font-mono whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                    <th className="px-3 py-2 text-left text-faint uppercase tracking-wider font-mono">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-dim">
                  {preview.rows.slice(0, 100).map((row) => (
                    <tr
                      key={row.row}
                      className={`${
                        row.errors.length > 0
                          ? 'bg-loss/5'
                          : row.warnings.length > 0
                          ? 'bg-yellow-500/5'
                          : 'bg-emerald-500/5'
                      }`}
                    >
                      <td className="px-3 py-2 text-faint font-mono">{row.row}</td>
                      {preview.columns.map((col) => (
                        <td key={col} className="px-3 py-2 whitespace-nowrap font-mono">
                          {renderCell(row.data[col])}
                        </td>
                      ))}
                      <td className="px-3 py-2">
                        {row.errors.length > 0 && (
                          <span className="text-loss text-xs" title={row.errors.join(', ')}>
                            Error
                          </span>
                        )}
                        {row.errors.length === 0 && row.warnings.length > 0 && (
                          <span className="text-yellow-400 text-xs" title={row.warnings.join(', ')}>
                            Warning
                          </span>
                        )}
                        {row.errors.length === 0 && row.warnings.length === 0 && (
                          <span className="text-emerald-400 text-xs">Valid</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {preview.total_rows > 100 && (
            <p className="text-xs text-faint mt-2">
              Showing first 100 of {preview.total_rows} rows
            </p>
          )}

          <div className="flex gap-3 mt-4">
            <button
              onClick={() => { setPreview(null); setError(null) }}
              className="btn btn-outline text-sm"
            >
              Cancel
            </button>
            {preview.valid_rows > 0 && (
              <button
                onClick={handleCommit}
                disabled={committing}
                className="btn btn-primary text-sm"
              >
                {committing
                  ? 'Importing...'
                  : `Import ${preview.valid_rows} Valid Row${preview.valid_rows !== 1 ? 's' : ''}`}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="text-center py-6 space-y-3">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-500/20">
            <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-main font-medium">
            Successfully imported {result.saved} of {result.total} transactions
          </p>
          {result.errors.length > 0 && (
            <div className="text-xs text-loss mt-2">
              {result.errors.length} row(s) had errors and were skipped
            </div>
          )}
          <button
            onClick={() => { setResult(null); setPreview(null); setError(null) }}
            className="btn btn-outline text-sm mt-2"
          >
            Import Another File
          </button>
        </div>
      )}
    </Card>
  )
}
