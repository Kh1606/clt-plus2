import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase.js'

function isoNDaysAgo(n) {
  const d = new Date()
  d.setUTCDate(d.getUTCDate() - n)
  return d.toISOString()
}

/**
 * Inventory roll-up for the dashboard.
 * Fetches the last `lookbackDays` of notices_v2, groups by (region, sub_entity),
 * and returns:
 *   { status, totalNotices, latestAt,
 *     byRegion: [{ region, total, byEntity: [{name, count}], latestAt }] }
 *
 * One Supabase query — client-side aggregation is fine at this scale.
 */
export default function useRegionInventory(lookbackDays = 30) {
  const [state, setState] = useState({
    status: 'loading',
    totalNotices: 0,
    latestAt: null,
    byRegion: [],
  })

  useEffect(() => {
    let cancelled = false
    supabase
      .from('notices_v2')
      .select('region,sub_entity,posted_at,scraped_at')
      .gte('scraped_at', isoNDaysAgo(lookbackDays))
      .limit(10000)
      .then(({ data, error }) => {
        if (cancelled) return
        if (error) {
          setState({ status: 'error', totalNotices: 0, latestAt: null, byRegion: [], error: error.message })
          return
        }
        const rows = data || []
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
    return () => { cancelled = true }
  }, [lookbackDays])

  return state
}
