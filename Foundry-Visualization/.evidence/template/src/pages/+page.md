---
title: City Data OS — Overview
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #0ea5e9 100%); border-radius: 1.25rem; padding: 2.5rem 2.5rem 2rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; top: -40px; right: -40px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(14,165,233,0.35) 0%, transparent 70%); border-radius: 50%;"></div>
  <div style="position: absolute; bottom: -30px; left: 30%; width: 180px; height: 180px; background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%); border-radius: 50%;"></div>
  <div style="position: relative; z-index: 1;">
    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.15em; color: #7dd3fc; margin-bottom: 0.5rem;">MetricForge City Foundation</div>
    <h1 style="margin: 0 0 0.4rem; font-size: 2.4rem; font-weight: 800; line-height: 1.1;">City Data OS</h1>
    <p style="margin: 0; font-size: 1.05rem; color: #cbd5e1; max-width: 600px;">Municipal data infrastructure — cross-departmental insights into roads, water systems, building permits, and ward demographics. Powered by the Cube semantic layer.</p>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     TOP-LINE KPIs
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM city_kpis
```

<BigValue data={kpis} value='total_road_segments'  title='Road Segments'       fmt='#,##0' />
<BigValue data={kpis} value='total_road_length_km'  title='Road Network (km)'  fmt='#,##0.0' />
<BigValue data={kpis} value='total_water_mains'     title='Water Mains'        fmt='#,##0' />
<BigValue data={kpis} value='total_water_network_km' title='Water Network (km)' fmt='#,##0.0' />
<BigValue data={kpis} value='total_permits'          title='Building Permits'   fmt='#,##0' />
<BigValue data={kpis} value='total_population'       title='Population'         fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     INFRASTRUCTURE HEALTH SNAPSHOT
     ═══════════════════════════════════════════════════════════════════ -->

## Infrastructure Health

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
  <BigValue data={kpis} value='avg_pipe_age_years'          title='Avg Water Pipe Age'      fmt='#,##0.0" yrs"' />
  <BigValue data={kpis} value='oldest_water_install_year'   title='Oldest Pipe Installed'    fmt='####' />
  <BigValue data={kpis} value='total_wards'                 title='Wards'                   fmt='#,##0' />
  <BigValue data={kpis} value='total_area_sq_km'            title='Total Area (km²)'        fmt='#,##0.0' />
  <BigValue data={kpis} value='residential_permits'         title='Residential Permits'     fmt='#,##0' />
  <BigValue data={kpis} value='commercial_permits'          title='Commercial Permits'      fmt='#,##0' />
</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     WARD-LEVEL OVERVIEW
     ═══════════════════════════════════════════════════════════════════ -->

## Ward-Level Infrastructure

```sql by_ward
SELECT * FROM cube_by_ward
```

<div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_ward}
  x='ward_name'
  y='road_segments'
  title='Road Segments by Ward'
  swapXY={true}
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444','#a855f7']}
/>

<DataTable
  data={by_ward}
  rows=15
>
  <Column id='ward_name' title='Ward' />
  <Column id='road_segments' title='Roads' fmt='#,##0' />
  <Column id='road_length_km' title='Road km' fmt='#,##0.0' />
  <Column id='water_mains' title='Water Mains' fmt='#,##0' />
  <Column id='population' title='Population' fmt='#,##0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     ROAD CONDITION
     ═══════════════════════════════════════════════════════════════════ -->

## Road Condition Breakdown

```sql road_condition
SELECT * FROM cube_road_condition
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={road_condition}
  x='condition'
  y='segments'
  title='Segments by Condition'
  colorPalette={['#22c55e','#84cc16','#eab308','#f97316','#ef4444','#64748b']}
/>

<BarChart
  data={road_condition}
  x='classification'
  y='length_km'
  title='Road Length by Classification (km)'
  swapXY={true}
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444']}
/>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     PERMITS OVERVIEW
     ═══════════════════════════════════════════════════════════════════ -->

## Development Permits

```sql permits_type
SELECT * FROM cube_permits_by_type
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={permits_type}
  x='permit_type'
  y='total'
  title='Permits by Type'
  swapXY={true}
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444','#a855f7']}
/>

<DataTable
  data={permits_type}
  rows=15
>
  <Column id='permit_type' title='Type' />
  <Column id='permit_status' title='Status' />
  <Column id='total' title='Permits' fmt='#,##0' />
  <Column id='estimated_value' title='Est. Value' fmt='$#,##0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     NAVIGATION CARDS
     ═══════════════════════════════════════════════════════════════════ -->

## Explore More

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; margin-top: 0.5rem;">

  <a href="/infrastructure" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #ecfdf5 0%, #6ee7b7 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">🏗️</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #064e3b;">Infrastructure Assets</div>
      <div style="font-size: 0.9rem; color: #047857; margin-top: 0.25rem;">Roads, bridges, water & sewer networks</div>
    </div>
  </a>

  <a href="/development" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #ede9fe 0%, #c4b5fd 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">🏠</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #4c1d95;">Development & Housing</div>
      <div style="font-size: 0.9rem; color: #6d28d9; margin-top: 0.25rem;">Permits, zoning, capacity analysis</div>
    </div>
  </a>

  <a href="/water" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #93c5fd 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">💧</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #1e3a8a;">Water Systems</div>
      <div style="font-size: 0.9rem; color: #1d4ed8; margin-top: 0.25rem;">Pipe age, material, capacity by ward</div>
    </div>
  </a>

  <a href="/governance" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #fefce8 0%, #fde047 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">📊</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #713f12;">Data Governance</div>
      <div style="font-size: 0.9rem; color: #a16207; margin-top: 0.25rem;">Quality, catalog, access & lineage</div>
    </div>
  </a>

</div>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem; padding-bottom: 1rem;">
  MetricForge City Foundation &middot; City Data OS &middot; Powered by Cube + Evidence
</div>
