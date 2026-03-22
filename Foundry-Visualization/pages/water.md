---
title: Water Systems
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #93c5fd 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; top: -30px; right: -30px; width: 180px; height: 180px; background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #bfdbfe; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">💧 Water Systems</h1>
  <p style="margin: 0; color: #dbeafe; font-size: 1rem;">Water distribution main analysis — pipe age, material breakdown, capacity indicators. Critical infrastructure that directly impacts housing development decisions.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     KPIs
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM city_kpis
```

<BigValue data={kpis} value='total_water_mains'        title='Total Water Mains'    fmt='#,##0' />
<BigValue data={kpis} value='avg_pipe_age_years'        title='Avg Pipe Age (yrs)'   fmt='#,##0.0' />
<BigValue data={kpis} value='avg_condition_score'       title='Avg Condition Score'  fmt='#,##0.1' />
<BigValue data={kpis} value='total_population'          title='Population Served'    fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     MATERIAL BREAKDOWN
     ═══════════════════════════════════════════════════════════════════ -->

## Pipe Material Analysis

```sql water_material
SELECT * FROM cube_water_by_material
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={water_material}
  x='material'
  y='total_mains'
  title='Water Mains by Material'
  colorPalette={['#3b82f6','#60a5fa','#93c5fd','#bfdbfe','#dbeafe','#64748b']}
/>

<BarChart
  data={water_material}
  x='material'
  y='avg_age_years'
  title='Average Age by Material (years)'
  colorPalette={['#ef4444','#f97316','#eab308','#84cc16','#22c55e','#64748b']}
/>

</div>

---

## Condition & Criticality by Material

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={water_material}
  x='material'
  y='avg_condition_score'
  title='Avg Condition Score by Material'
  colorPalette={['#22c55e','#84cc16','#eab308','#f97316','#ef4444','#64748b']}
/>

<BarChart
  data={water_material}
  x='material'
  y='avg_criticality'
  title='Avg Criticality by Material'
  colorPalette={['#3b82f6','#60a5fa','#93c5fd','#bfdbfe','#dbeafe','#64748b']}
/>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     AGE & CONDITION RISK
     ═══════════════════════════════════════════════════════════════════ -->

## Water Infrastructure by Ward

```sql by_ward
SELECT * FROM cube_by_ward
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_ward}
  x='ward_name'
  y='water_mains'
  title='Water Mains by Ward'
  swapXY={true}
  colorPalette={['#0ea5e9']}
/>

<DataTable
  data={by_ward}
  rows=15
>
  <Column id='ward_name' title='Ward' />
  <Column id='water_mains' title='Mains' fmt='#,##0' />
  <Column id='distinct_materials' title='Materials' fmt='#,##0' />
  <Column id='population' title='Population' fmt='#,##0' />
</DataTable>

</div>

---

## Detailed Material Inventory

<DataTable
  data={water_material}
  rows=25
  search=true
>
  <Column id='material' title='Material' />
  <Column id='pipe_status' title='Status' />
  <Column id='total_mains' title='Mains' fmt='#,##0' />
  <Column id='avg_pipe_size' title='Avg Pipe Size' fmt='#,##0.0' />
  <Column id='avg_condition_score' title='Condition' fmt='#,##0.1' />
  <Column id='avg_criticality' title='Criticality' fmt='#,##0.1' />
  <Column id='avg_age_years' title='Avg Age (yrs)' fmt='#,##0.0' />
</DataTable>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge City Foundation &middot; Water Systems &middot; Powered by Cube + Evidence
</div>
