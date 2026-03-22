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
<BigValue data={kpis} value='total_water_network_km'    title='Total Network (km)'   fmt='#,##0.0' />
<BigValue data={kpis} value='avg_pipe_age_years'        title='Avg Pipe Age (yrs)'   fmt='#,##0.0' />
<BigValue data={kpis} value='oldest_water_install_year' title='Oldest Pipe Year'     fmt='####' />

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

<!-- ═══════════════════════════════════════════════════════════════════
     AGE & CONDITION RISK
     ═══════════════════════════════════════════════════════════════════ -->

## Age & Capacity Risk by Ward

```sql by_ward
SELECT * FROM cube_by_ward
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_ward}
  x='ward_name'
  y='water_network_km'
  title='Water Network Length by Ward (km)'
  swapXY={true}
  colorPalette={['#0ea5e9']}
/>

<DataTable
  data={by_ward}
  rows=15
>
  <Column id='ward_name' title='Ward' />
  <Column id='water_mains' title='Mains' fmt='#,##0' />
  <Column id='water_network_km' title='Network (km)' fmt='#,##0.1' />
  <Column id='oldest_water_year' title='Oldest Pipe' />
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
  <Column id='ward' title='Ward' />
  <Column id='total_mains' title='Mains' fmt='#,##0' />
  <Column id='length_km' title='Length (km)' fmt='#,##0.1' />
  <Column id='avg_diameter_mm' title='Avg Diameter (mm)' fmt='#,##0.0' />
  <Column id='avg_age_years' title='Avg Age (yrs)' fmt='#,##0.0' />
  <Column id='oldest_year' title='Oldest' />
  <Column id='newest_year' title='Newest' />
</DataTable>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge City Foundation &middot; Water Systems &middot; Powered by Cube + Evidence
</div>
