import { useEffect, useMemo, useState } from 'react'
import regionsData from '../../data/regions.json'
import useRegionInventory from '../useRegionInventory.js'
import { NON_GEOGRAPHIC_REGIONS } from './regionNameMap.js'
import KoreaMap from './KoreaMap.jsx'
import { buildSubMatcher, municipalitiesForRegion } from './nameMatcher.js'

const MUNICIPALITIES_URL = `${import.meta.env.BASE_URL}data/skorea-municipalities-topo.json`

/**
 * Map mode shell.
 *
 * Selection state lives in App.jsx (shared with InventoryView). When the
 * user clicks a province, a sub-region, or an "unzoned" chip, we call up
 * to App and the shared RegionDetailPanel renders on the right.
 *
 * Additionally, when a province is drilled in we compute the orgs that
 * don't match any polygon (city-wide orgs in metropolitan cities like
 * 부산시청, province-wide orgs in 도 like 경기도청) and render them as
 * a clickable chip bar above the map.
 */
export default function MapView({ selected, onPickRegion, onPickSub }) {
  const inv = useRegionInventory(30)

  // Region totals from the inventory roll-up.
  const countsByRegion = useMemo(() => {
    const m = {}
    for (const r of inv.byRegion) m[r.region] = r.total
    return m
  }, [inv.byRegion])

  // Per-region per-sub counts: { regionName: { subName: count } }.
  const countsBySub = useMemo(() => {
    const m = {}
    for (const r of inv.byRegion) {
      const inner = {}
      for (const e of r.byEntity) inner[e.name] = e.count
      m[r.region] = inner
    }
    return m
  }, [inv.byRegion])

  const unzonedRegions = useMemo(
    () => regionsData
      .filter(r => NON_GEOGRAPHIC_REGIONS.has(r.region))
      .map(r => ({ region: r.region, count: r.subEntities.length })),
    [],
  )

  // Lazy-load municipalities topojson the first time a province is selected.
  const [muniData, setMuniData] = useState(null)
  const [muniLoading, setMuniLoading] = useState(false)
  useEffect(() => {
    if (!selected?.region || muniData || muniLoading) return
    setMuniLoading(true)
    fetch(MUNICIPALITIES_URL)
      .then(r => r.json())
      .then(json => setMuniData(json))
      .catch(err => console.error('Failed to load municipalities:', err))
      .finally(() => setMuniLoading(false))
  }, [selected?.region, muniData, muniLoading])

  // Compute the orgs for the currently-selected region that DON'T match
  // any polygon — these are the chips rendered above the map. For example,
  // 부산광역시 → all 5 v2 orgs (all city-wide); 경기도 → 경기도청,
  // 경기도시공사 (city-level orgs match districts already).
  const unmatchedOrgs = useMemo(() => {
    if (!selected?.region || !muniData) return []
    const province = regionsData.find(r => r.region === selected.region)
    if (!province) return []
    const allSubs = province.subEntities.map(s => s.name)
    const matcher = buildSubMatcher(countsBySub[selected.region] || {})
    // Build set of subs that DO match some polygon in this province.
    const munis = municipalitiesForRegion(muniData, selected.region)
    const matchedSubs = new Set()
    for (const g of munis) {
      const m = matcher.match(g.properties.name)
      if (m) matchedSubs.add(m)
    }
    const subCounts = countsBySub[selected.region] || {}
    return allSubs
      .filter(s => !matchedSubs.has(s))
      .map(name => ({ name, count: subCounts[name] || 0 }))
  }, [selected?.region, muniData, countsBySub])

  return (
    <div
      style={{
        position: 'relative',
        flex: 1,
        minHeight: 0,
        margin: '20px auto',
        padding: '0 20px',
        width: '100%',
        maxWidth: 1440,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          justifyContent: 'space-between',
          gap: 12,
          flexWrap: 'wrap',
        }}
      >
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)' }}>
            대한민국 공공기관 지도
          </h1>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
            최근 30일 공지 수 기준 히트맵 ·
            {inv.status === 'loading' && ' 데이터 불러오는 중…'}
            {inv.status === 'ready' && ` 전체 ${inv.totalNotices.toLocaleString()}건`}
            {inv.status === 'error' && ' 데이터 연결 오류'}
          </div>
        </div>

        {/* Non-geographic regions surfaced as chips (no map polygon for them) */}
        {unzonedRegions.length > 0 && (
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)', alignSelf: 'center' }}>
              지역 미지정
            </span>
            {unzonedRegions.map(({ region, count }) => {
              const isActive = selected?.region === region
              return (
                <button
                  key={region}
                  onClick={() => onPickRegion?.(region)}
                  style={{
                    padding: '4px 10px',
                    fontSize: 12,
                    fontWeight: 500,
                    background: isActive ? 'var(--accent)' : 'var(--bg-card)',
                    color: isActive ? '#fff' : 'var(--text-secondary)',
                    border: '1px solid var(--border)',
                    borderRadius: 999,
                    cursor: 'pointer',
                  }}
                >
                  {region} <span style={{ opacity: 0.65 }}>· {count}</span>
                </button>
              )
            })}
          </div>
        )}
      </div>

      {/* Chip bar: orgs for the selected province that don't match any polygon */}
      {selected?.region && unmatchedOrgs.length > 0 && (
        <UnmatchedOrgsBar
          regionName={selected.region}
          orgs={unmatchedOrgs}
          selectedSub={selected.sub ?? null}
          onPickSub={onPickSub}
        />
      )}

      <div style={{ position: 'relative', flex: 1, minHeight: 480 }}>
        <KoreaMap
          countsByRegion={countsByRegion}
          countsBySub={countsBySub}
          selectedRegionName={selected?.region ?? null}
          selectedSubName={selected?.sub ?? null}
          muniData={muniData}
          muniLoading={muniLoading}
          onPickRegion={onPickRegion}
          onPickSub={onPickSub}
        />
      </div>
    </div>
  )
}

function UnmatchedOrgsBar({ regionName, orgs, selectedSub, onPickSub }) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '10px 14px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        boxShadow: 'var(--shadow-sm)',
        flexWrap: 'wrap',
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: 0.4,
          marginRight: 4,
          flexShrink: 0,
        }}
      >
        {regionName} 기관
      </div>
      {orgs.map(({ name, count }) => {
        const isActive = name === selectedSub
        return (
          <button
            key={name}
            onClick={() => onPickSub?.(regionName, name)}
            title={`${name} · ${count}건`}
            style={{
              padding: '5px 12px',
              fontSize: 12,
              fontWeight: 600,
              background: isActive ? '#F97316' : 'var(--bg-card)',
              color: isActive ? '#fff' : 'var(--text-primary)',
              border: '1px solid ' + (isActive ? '#C2410C' : 'var(--border)'),
              borderRadius: 999,
              cursor: 'pointer',
              transition: 'background 0.15s, color 0.15s',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => {
              if (!isActive) e.currentTarget.style.background = 'var(--bg-hover)'
            }}
            onMouseLeave={e => {
              if (!isActive) e.currentTarget.style.background = 'var(--bg-card)'
            }}
          >
            {name}
            <span style={{ opacity: isActive ? 0.85 : 0.55, marginLeft: 6, fontWeight: 500 }}>
              · {count}건
            </span>
          </button>
        )
      })}
    </div>
  )
}
