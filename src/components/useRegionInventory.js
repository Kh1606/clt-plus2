import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase.js'

/**
 * Inventory roll-up.
 *
 * Returns { status, totalNotices, latestAt,
 *           byRegion: [{ region, total, byEntity: [{name, count}], latestAt }] }
 *
 * Fetches every notice in notices_v2 (no time filter) so per-org counts
 * match what NoticeList renders below.
 *
 * Supabase PostgREST defaults to a 1000-row server-side cap regardless
 * of client .limit(). We page through with .range() — same pattern as
 * scripts/prune_notices_v2.py.
 */
const PAGE_SIZE = 1000

async function fetchAllRows() {
  const all = []
  for (let start = 0; ; start += PAGE_SIZE) {
    const { data, error } = await supabase
      .from('notices_v2')
      .select('region,sub_entity,posted_at,scraped_at')
      .range(start, start + PAGE_SIZE - 1)
    if (error) throw error
    if (!data || data.length === 0) break
    all.push(...data)
    if (data.length < PAGE_SIZE) break
  }
  return all
}

export default function useRegionInventory() {
  const [state, setState] = useState({
    status: 'loading',
    totalNotices: 0,
    latestAt: null,
    byRegion: [],
  })

  useEffect(() => {
    let cancelled = false
    fetchAllRows()
      .then(rows => {
        if (cancelled) return
        // group by region
        const grouped = new Map()
        let latestAt = null
        for (const row of rows) {
          const region = row.region || '-'
          const sub = row.sub_entity || '-'
          const t = row.scraped_at ? Date.parse(row.scraped_at) : null
          if (t && (!latestAt || t > latestAt)) latestAt = t

          let g = grouped.get(region)
          if (!g) {
            g = { region, total: 0, byEntity: new Map(), latestAt: null }
            grouped.set(region, g)
          }
          g.total += 1
          g.byEntity.set(sub, (g.byEntity.get(sub) || 0) + 1)
          if (t && (!g.latestAt || t > g.latestAt)) g.latestAt = t
        }

        // shape + sort
        const byRegion = Array.from(grouped.values())
          .map(g => ({
            region: g.region,
            total: g.total,
            latestAt: g.latestAt,
            byEntity: Array.from(g.byEntity.entries())
              .map(([name, count]) => ({ name, count }))
              .sort((a, b) => b.count - a.count),
          }))
          .sort((a, b) => b.total - a.total)

        setState({
          status: 'ready',
          totalNotices: rows.length,
          latestAt,
          byRegion,
        })
      })
      .catch(err => {
        if (cancelled) return
        setState({
          status: 'error',
          totalNotices: 0,
          latestAt: null,
          byRegion: [],
          error: err?.message || String(err),
        })
      })
    return () => { cancelled = true }
  }, [])

  return state
}
