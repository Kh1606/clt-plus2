/**
 * TopoJSON ↔ v2 sub_entity name matcher.
 *
 * The two name spaces use different conventions:
 *   topo: `청주시상당구`, `중구`, `김해시`
 *   v2:   `청주시-상당구`, `대구시청`, `김해시`
 *
 * We index every v2 sub name with a handful of normalized variants
 * (hyphen-stripped, suffix-stripped, parent-city) so direct lookup is O(1).
 */

export function subVariants(name) {
  const v = new Set()
  const norm = name.trim()
  v.add(norm)
  // Hyphen-stripped: 청주시-상당구 -> 청주시상당구
  v.add(norm.replace(/-/g, ''))
  // Strip city prefix: 청주시-상당구 -> 상당구
  const m = norm.match(/^([가-힣]+시)-?([가-힣]+(?:구|군))$/u)
  if (m) v.add(m[2])
  // Strip 시청/도청 suffix.
  v.add(norm.replace(/시청$/u, '시'))
  v.add(norm.replace(/도청$/u, '도'))
  return Array.from(v).filter(Boolean)
}

export function muniVariants(name) {
  const v = new Set()
  const norm = name.trim()
  v.add(norm)
  // For TopoJSON city-district names like 청주시상당구 / 용인시수지구 /
  // 수원시영통구 (no separator between city and district):
  const m = norm.match(/^([가-힣]+시)([가-힣]+(?:구|군))$/u)
  if (m) {
    v.add(`${m[1]}-${m[2]}`) // hyphenated form for v2 match
    v.add(m[2])              // bare district name
    v.add(m[1])              // PARENT CITY — so 용인시수지구 also matches 용인시청 (v2)
  }
  return Array.from(v).filter(Boolean)
}

/**
 * Build a matcher from a region's counts map.
 * Returns { counts, match(muniName) -> v2SubName | null }.
 */
export function buildSubMatcher(countsForRegion) {
  const counts = countsForRegion || {}
  const index = new Map() // normalizedKey -> v2SubName

  for (const subName of Object.keys(counts)) {
    for (const key of subVariants(subName)) {
      if (!index.has(key)) index.set(key, subName)
    }
  }

  return {
    counts,
    match(muniName) {
      if (!muniName) return null
      for (const key of muniVariants(muniName)) {
        if (index.has(key)) return index.get(key)
      }
      return null
    },
  }
}

/**
 * Map of v2 region name → 2-digit South Korea province code used in the
 * municipalities TopoJSON. Used for filtering topojson geometries by
 * province (g.properties.code.startsWith(provinceCode)).
 *
 * Codes confirmed by reading public/data/skorea-municipalities-topo.json:
 * 11=서울, 21=부산, 22=대구, 23=인천, 24=광주, 25=대전, 26=울산, 29=세종,
 * 31=경기, 32=강원, 33=충북, 34=충남, 35=전북, 36=전남, 37=경북, 38=경남,
 * 39=제주.
 *
 * v2's regions.json uses slightly different labels for sejong/jeju (no
 * 특별/자치 prefix), so we include both forms.
 */
export const REGION_CODE_BY_NAME = {
  '서울특별시': '11',
  '부산광역시': '21',
  '대구광역시': '22',
  '인천광역시': '23',
  '광주광역시': '24',
  '대전광역시': '25',
  '울산광역시': '26',
  '세종특별자치시': '29',
  '세종특별시': '29',
  '경기도': '31',
  '강원도': '32',
  '강원특별자치도': '32',
  '충청북도': '33',
  '충청남도': '34',
  '전라북도': '35',
  '전북특별자치도': '35',
  '전라남도': '36',
  '경상북도': '37',
  '경상남도': '38',
  '제주특별자치도': '39',
  '제주도': '39',
}

/**
 * Filter topojson municipality geometries to those belonging to a given
 * v2 region. Returns [] if region has no code mapping (e.g. '-', '기타',
 * '공사', '창원시' — non-geographic regions).
 */
export function municipalitiesForRegion(muniTopo, regionName) {
  const code = REGION_CODE_BY_NAME[regionName]
  if (!code || !muniTopo) return []
  const key = Object.keys(muniTopo.objects)[0]
  return muniTopo.objects[key].geometries.filter(
    g => String(g.properties.code).startsWith(code),
  )
}
