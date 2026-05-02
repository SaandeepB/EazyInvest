import { Search, Sparkles, WalletCards } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import HoldingPreviewCard from '../components/holdings/HoldingPreviewCard'
import PageShell from '../components/layout/PageShell'
import EmptyState from '../components/ui/EmptyState'
import InputCard from '../components/ui/InputCard'
import MetricCard from '../components/ui/MetricCard'
import StatusPill from '../components/ui/StatusPill'
import TableCard from '../components/ui/TableCard'
import { api } from '../services/api'
import type { Holding, HoldingCreate, LookupResult } from '../types'

const EMPTY_FORM: HoldingCreate = { symbol: '', quantity: 0, avg_cost: 0 }

function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '--'
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

  const totals = useMemo(() => {
    const costBasis = holdings.reduce((sum, holding) => sum + holding.cost_basis, 0)
    const marketValue = holdings.reduce((sum, holding) => sum + (holding.current_value ?? holding.estimated_value ?? 0), 0)
    return {
      count: holdings.length,
      costBasis,
      marketValue,
    }
  }, [holdings])

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
    <PageShell
      eyebrow="My Holdings"
      title="Manage only the positions you have actually added."
      description="Lookup is powered by the syndicated CSV dataset. Known symbols receive proxy pricing; unknown symbols stay supported with estimated values based on your purchase price."
      aside={<StatusPill label={`${totals.count} holdings`} tone="navy" />}
    >
      <section className="metric-grid">
        <MetricCard label="User-added holdings" value={String(totals.count)} detail="Only your positions appear here" tone="navy" icon={WalletCards} />
        <MetricCard label="Total cost basis" value={formatCurrency(totals.costBasis)} detail="Quantity multiplied by purchase price" tone="blue" icon={Sparkles} />
        <MetricCard label="Value tracked" value={formatCurrency(totals.marketValue)} detail="Market or estimated value from valuation service" tone="teal" icon={Search} />
      </section>

      <section className="holdings-layout">
        <div className="stack-lg">
          <InputCard
            title={editingId ? 'Edit holding' : 'Add a holding'}
            description="Enter a symbol, quantity, and purchase price. Symbol lookup is optional, but it helps prefill the proxy market context."
          >
            <form className="stack-md" onSubmit={handleSubmit}>
              <div className="form-grid">
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
                  <span>Purchase Price</span>
                  <input
                    type="number"
                    min="0.01"
                    step="any"
                    value={form.avg_cost || ''}
                    onChange={e => setForm(current => ({ ...current, avg_cost: Number(e.target.value) }))}
                    required
                  />
                </label>
              </div>

              {editingId === null && suggestions.length > 0 && (
                <div className="suggestions">
                  {suggestions.slice(0, 6).map(item => (
                    <button
                      type="button"
                      key={item.symbol}
                      className="suggestion-item"
                      onClick={() => setForm(current => ({ ...current, symbol: item.symbol }))}
                    >
                      <div>
                        <strong>{item.symbol}</strong>
                        <div className="muted">{item.name}</div>
                      </div>
                      <StatusPill label={item.asset_type} tone="blue" />
                      <span className="suggestion-price">{formatCurrency(item.proxy_price)}</span>
                    </button>
                  ))}
                </div>
              )}

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
          </InputCard>

          <TableCard
            title="Current holdings"
            description="This table shows only the positions you added, never the full market proxy CSV universe."
          >
            {loading ? (
              <div>Loading holdings...</div>
            ) : holdings.length === 0 ? (
              <EmptyState title="No holdings yet" description="Add your first position to start tracking cost basis, market proxy value, and estimated value." />
            ) : (
              <div className="table-wrap">
                <table className="holdings-table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Type</th>
                      <th>Quantity</th>
                      <th>Purchase Price</th>
                      <th>Market Proxy Price</th>
                      <th>Cost Basis</th>
                      <th>Market Value / Estimated Value</th>
                      <th>Source</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {holdings.map(holding => (
                      <tr key={holding.id}>
                        <td>
                          <div className="table-symbol">
                            <strong>{holding.symbol}</strong>
                            <span className="muted">{holding.name}</span>
                          </div>
                        </td>
                        <td>
                          <div className="table-symbol">
                            <span>{holding.asset_type}</span>
                            <span className="muted">{holding.sector_or_category}</span>
                          </div>
                        </td>
                        <td>{holding.quantity.toLocaleString()}</td>
                        <td>{formatCurrency(holding.avg_cost)}</td>
                        <td>{formatCurrency(holding.current_price)}</td>
                        <td>{formatCurrency(holding.cost_basis)}</td>
                        <td>{formatCurrency(holding.current_value ?? holding.estimated_value)}</td>
                        <td><StatusPill label={formatSource(holding.price_source)} tone={holding.current_price === null ? 'warning' : 'success'} /></td>
                        <td>
                          <div className="table-actions">
                            <button className="btn btn-secondary btn-compact" onClick={() => beginEdit(holding)}>Edit</button>
                            <button className="btn btn-danger btn-compact" onClick={() => removeHolding(holding.id)}>Delete</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TableCard>
        </div>

        <div className="stack-lg">
          <HoldingPreviewCard symbol={normalizedSymbol} selectedLookup={selectedLookup} showUnknownPreview={showUnknownPreview} />
          <div className="card stack-sm">
            <div className="section-title">What gets filled in automatically</div>
            <div className="list-panel">
              <div className="list-row">
                <span>Name and asset type</span>
                <span className="list-value">From CSV lookup</span>
              </div>
              <div className="list-row">
                <span>Sector or category</span>
                <span className="list-value">From CSV lookup</span>
              </div>
              <div className="list-row">
                <span>Proxy market price</span>
                <span className="list-value">Valuation service</span>
              </div>
              <div className="list-row">
                <span>Unknown symbol handling</span>
                <span className="list-value">Estimated value only</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </PageShell>
  )
}
