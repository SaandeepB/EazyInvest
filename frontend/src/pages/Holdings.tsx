import { useEffect, useMemo, useState } from 'react'
import { api } from '../services/api'
import type { Holding, HoldingCreate, LookupResult } from '../types'

const EMPTY_FORM: HoldingCreate = { symbol: '', quantity: 0, avg_cost: 0 }

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '—'
  }
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function formatSource(source: string): string {
  if (source === 'syndicated_csv') {
    return 'Syndicated CSV'
  }
  if (source === 'missing_from_syndicated_csv') {
    return 'Estimated from purchase price'
  }
  return source
}

export default function Holdings() {
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [suggestions, setSuggestions] = useState<LookupResult[]>([])
  const [form, setForm] = useState<HoldingCreate>(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [error, setError] = useState('')

  const normalizedSymbol = form.symbol.trim().toUpperCase()

  const selectedLookup = useMemo(
    () => suggestions.find(item => item.symbol === normalizedSymbol),
    [normalizedSymbol, suggestions],
  )

  const showUnknownPreview = normalizedSymbol.length > 0 && !selectedLookup

  const load = async () => {
    setLoading(true)
    try {
      const response = await api.getHoldings()
      setHoldings(response.holdings)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    const query = normalizedSymbol
    if (query.length < 1) {
      setSuggestions([])
      return
    }
    const timer = setTimeout(() => {
      api.lookupSymbols(query)
        .then(response => setSuggestions(response.results))
        .catch(() => setSuggestions([]))
    }, 180)
    return () => clearTimeout(timer)
  }, [normalizedSymbol])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      if (editingId !== null) {
        await api.updateHolding(editingId, {
          quantity: form.quantity,
          avg_cost: form.avg_cost,
        })
      } else {
        await api.addHolding({ ...form, symbol: normalizedSymbol })
      }
      setForm(EMPTY_FORM)
      setEditingId(null)
      setSuggestions([])
      await load()
    } catch (err: any) {
      setError(err.message || 'Could not save holding.')
    } finally {
      setSaving(false)
    }
  }

  const beginEdit = (holding: Holding) => {
    setEditingId(holding.id)
    setForm({ symbol: holding.symbol, quantity: holding.quantity, avg_cost: holding.avg_cost })
    setSuggestions([])
    setError('')
  }

  const removeHolding = async (id: number) => {
    await api.deleteHolding(id)
    await load()
  }

  return (
    <div className="page-grid">
      <section className="card stack-sm">
        <div className="eyebrow">My Holdings</div>
        <h1 className="page-title">Only user-added positions appear here</h1>
        <p className="muted">
          Symbol lookup and autocomplete come from the syndicated CSV dataset. Known symbols use the CSV market proxy
          price. Unknown symbols are still allowed, but they keep a null market proxy price and show estimated value
          from your purchase price instead.
        </p>
      </section>

      <section className="main-grid">
        <div className="card stack-sm">
          <div className="section-title">{editingId ? 'Edit holding' : 'Add a holding'}</div>
          <form className="stack-sm" onSubmit={handleSubmit}>
            <label className="field">
              <span>Symbol</span>
              <input
                value={form.symbol}
                onChange={e => setForm(current => ({ ...current, symbol: e.target.value.toUpperCase() }))}
                placeholder="AAPL"
                required
                disabled={editingId !== null}
              />
            </label>

            {editingId === null && suggestions.length > 0 && (
              <div className="suggestions">
                {suggestions.map(item => (
                  <button
                    type="button"
                    key={item.symbol}
                    className="suggestion-item"
                    onClick={() => setForm(current => ({ ...current, symbol: item.symbol }))}
                  >
                    <strong>{item.symbol}</strong>
                    <span>{item.name}</span>
                    <span>{formatCurrency(item.proxy_price)}</span>
                  </button>
                ))}
              </div>
            )}

            {selectedLookup && (
              <div className="info-box stack-sm">
                <strong>{selectedLookup.name}</strong>
                <span>{selectedLookup.asset_type} | {selectedLookup.sector_or_category}</span>
                <span>Proxy market price: {formatCurrency(selectedLookup.proxy_price)}</span>
              </div>
            )}

            {showUnknownPreview && (
              <div className="info-box stack-sm">
                <strong>{normalizedSymbol}</strong>
                <span>Unknown symbol</span>
                <span>Market proxy price unavailable. Estimated value will use your purchase price.</span>
              </div>
            )}

            <label className="field">
              <span>Quantity</span>
              <input
                type="number"
                min="0.0001"
                step="any"
                value={form.quantity || ''}
                onChange={e => setForm(current => ({ ...current, quantity: Number(e.target.value) }))}
                required
              />
            </label>
            <label className="field">
              <span>Purchase price</span>
              <input
                type="number"
                min="0.01"
                step="any"
                value={form.avg_cost || ''}
                onChange={e => setForm(current => ({ ...current, avg_cost: Number(e.target.value) }))}
                required
              />
            </label>
            {error && <div className="error-banner">{error}</div>}
            <div className="button-row">
              <button className="btn btn-primary" disabled={saving}>
                {saving ? 'Saving...' : editingId ? 'Save changes' : 'Add holding'}
              </button>
              {editingId !== null && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setEditingId(null)
                    setForm(EMPTY_FORM)
                    setSuggestions([])
                    setError('')
                  }}
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        <div className="card stack-sm">
          <div className="section-title">Current holdings</div>
          {loading ? (
            <div>Loading holdings...</div>
          ) : holdings.length === 0 ? (
            <div className="empty-panel">No holdings yet. Add your first symbol to start deterministic tracking.</div>
          ) : (
            <div className="holdings-table-wrap">
              <table className="holdings-table">
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Name</th>
                    <th>Asset Type</th>
                    <th>Sector / Category</th>
                    <th>Purchase Price</th>
                    <th>Market Proxy Price</th>
                    <th>Cost Basis</th>
                    <th>Market Value / Estimated Value</th>
                    <th>Source</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {holdings.map(holding => (
                    <tr key={holding.id}>
                      <td><strong>{holding.symbol}</strong></td>
                      <td>{holding.name}</td>
                      <td>{holding.asset_type}</td>
                      <td>{holding.sector_or_category}</td>
                      <td>{formatCurrency(holding.avg_cost)}</td>
                      <td>{formatCurrency(holding.current_price)}</td>
                      <td>{formatCurrency(holding.cost_basis)}</td>
                      <td>{formatCurrency(holding.current_value ?? holding.estimated_value)}</td>
                      <td>{formatSource(holding.price_source)}</td>
                      <td>
                        <div className="button-row">
                          <button className="btn btn-secondary" onClick={() => beginEdit(holding)}>Edit</button>
                          <button className="btn btn-danger" onClick={() => removeHolding(holding.id)}>Delete</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
