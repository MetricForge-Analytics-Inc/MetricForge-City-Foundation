---
title: Infrastructure Assets
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #064e3b 0%, #059669 50%, #6ee7b7 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; bottom: -25px; right: 10%; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #a7f3d0; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">🏗️ Infrastructure Assets</h1>
  <p style="margin: 0; color: #d1fae5; font-size: 1rem;">Roads, water mains, and cross-departmental infrastructure analysis by ward. Coordinated planning requires integrated data.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     KPIs
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM city_kpis
```

<BigValue data={kpis} value='total_road_segments'        title='Road Segments'        fmt='#,##0' />
<BigValue data={kpis} value='total_water_mains'           title='Water Mains'          fmt='#,##0' />
<BigValue data={kpis} value='avg_pipe_age_years'          title='Avg Pipe Age (yrs)'   fmt='#,##0.0' />
<BigValue data={kpis} value='avg_condition_score'         title='Avg Pipe Condition'   fmt='#,##0.1' />
<BigValue data={kpis} value='total_population'            title='Population'           fmt='#,##0' />
<BigValue data={kpis} value='total_residential_households' title='Households'           fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     ROAD CONDITION
     ═══════════════════════════════════════════════════════════════════ -->

## Road Network — Condition Analysis

```sql road_condition
SELECT * FROM cube_road_condition
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={road_condition}
  x='surface_type'
  y='segments'
  title='Segments by Surface Type'
  colorPalette={['#22c55e','#84cc16','#eab308','#f97316','#ef4444','#64748b']}
/>

<BarChart
  data={road_condition}
  x='classification'
  y='segments'
  title='Segments by Road Classification'
  swapXY={true}
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444']}
/>

</div>

<DataTable
  data={road_condition}
  rows=20
>
  <Column id='surface_type' title='Surface Type' />
  <Column id='classification' title='Classification' />
  <Column id='segments' title='Segments' fmt='#,##0' />
</DataTable>

---

<!-- ═══════════════════════════════════════════════════════════════════
     WARD INFRASTRUCTURE MAP
     ═══════════════════════════════════════════════════════════════════ -->

## Infrastructure by Ward

```sql by_ward
SELECT * FROM cube_by_ward
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_ward}
  x='ward_name'
  y={['road_segments', 'water_mains']}
  title='Road Segments & Water Mains per Ward'
  type='grouped'
  swapXY={true}
  colorPalette={['#6366f1','#0ea5e9']}
/>

<DataTable
  data={by_ward}
  rows=15
>
  <Column id='ward_name' title='Ward' />
  <Column id='road_segments' title='Roads' fmt='#,##0' />
  <Column id='water_mains' title='Water Mains' fmt='#,##0' />
  <Column id='population' title='Population' fmt='#,##0' />
  <Column id='households' title='Households' fmt='#,##0' />
  <Column id='distinct_materials' title='Pipe Materials' fmt='#,##0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     WATER PIPE MATERIAL ANALYSIS
     ═══════════════════════════════════════════════════════════════════ -->

## Water Main Materials & Age

```sql water_material
SELECT * FROM cube_water_by_material
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={water_material}
  x='material'
  y='total_mains'
  title='Water Mains by Pipe Material'
  colorPalette={['#0ea5e9','#38bdf8','#7dd3fc','#bae6fd','#e0f2fe','#64748b']}
/>

<BarChart
  data={water_material}
  x='material'
  y='avg_age_years'
  title='Average Pipe Age by Material (years)'
  colorPalette={['#ef4444','#f97316','#eab308','#84cc16','#22c55e','#64748b']}
/>

</div>

<DataTable
  data={water_material}
  rows=20
>
  <Column id='material' title='Material' />
  <Column id='ward' title='Ward' />
  <Column id='total_mains' title='Mains' fmt='#,##0' />
  <Column id='length_km' title='Length (km)' fmt='#,##0.1' />
  <Column id='avg_diameter_mm' title='Avg Diameter (mm)' fmt='#,##0.0' />
  <Column id='avg_age_years' title='Avg Age (yrs)' fmt='#,##0.0' />
  <Column id='oldest_year' title='Oldest' />
  <Column id='newest_year' title='Newest' />
</DataTable>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge City Foundation &middot; Infrastructure Assets &middot; Powered by Cube + Evidence
</div>
