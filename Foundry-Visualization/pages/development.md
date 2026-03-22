---
title: Development & Housing
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 50%, #c4b5fd 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; bottom: -25px; right: 10%; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #ddd6fe; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">🏠 Development & Housing</h1>
  <p style="margin: 0; color: #ede9fe; font-size: 1rem;">Building permits, development intensity, and the critical link between housing growth and infrastructure capacity — the challenge that paused Kitchener's housing development.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     KPIs
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM city_kpis
```

<BigValue data={kpis} value='total_permits'          title='Total Permits'        fmt='#,##0' />
<BigValue data={kpis} value='total_permit_value'     title='Total Est. Value'     fmt='$#,##0' />
<BigValue data={kpis} value='avg_permit_value'        title='Avg Permit Value'    fmt='$#,##0' />
<BigValue data={kpis} value='residential_permits'    title='Residential'          fmt='#,##0' />
<BigValue data={kpis} value='commercial_permits'     title='Commercial'           fmt='#,##0' />
<BigValue data={kpis} value='completed_permits'      title='Completed'            fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     PERMITS BY TYPE & STATUS
     ═══════════════════════════════════════════════════════════════════ -->

## Permits by Type & Status

```sql permits_type
SELECT * FROM cube_permits_by_type
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={permits_type}
  x='permit_type'
  y='total'
  title='Permit Volume by Type'
  swapXY={true}
  colorPalette={['#7c3aed','#8b5cf6','#a78bfa','#c4b5fd','#ddd6fe','#64748b']}
/>

<DataTable
  data={permits_type}
  rows=15
>
  <Column id='permit_type' title='Type' />
  <Column id='permit_status' title='Status' />
  <Column id='total' title='Permits' fmt='#,##0' />
  <Column id='estimated_value' title='Est. Value' fmt='$#,##0' />
  <Column id='actual_value' title='Actual Value' fmt='$#,##0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     HOUSING vs INFRASTRUCTURE CAPACITY  (the key challenge metric)
     ═══════════════════════════════════════════════════════════════════ -->

## Housing vs Infrastructure Capacity

_This analysis addresses the problem statement directly: housing development was paused because the Region didn't account for infill growth — only subdivisions. 50% of 2024 residential permits were infill._

```sql permits_ward
SELECT * FROM cube_permits_by_ward
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={permits_ward}
  x='ward_name'
  y={['residential_permits', 'water_mains']}
  title='Residential Permits vs Water Mains per Ward'
  type='grouped'
  swapXY={true}
  colorPalette={['#7c3aed','#0ea5e9']}
/>

<BarChart
  data={permits_ward}
  x='ward_name'
  y='total_value'
  title='Total Development Value by Ward'
  swapXY={true}
  colorPalette={['#f59e0b']}
  fmt='$#,##0'
/>

</div>

<DataTable
  data={permits_ward}
  rows=15
  search=true
>
  <Column id='ward_name' title='Ward' />
  <Column id='total_permits' title='Permits' fmt='#,##0' />
  <Column id='residential_permits' title='Residential' fmt='#,##0' />
  <Column id='total_value' title='Total Value' fmt='$#,##0' />
  <Column id='water_mains' title='Water Mains' fmt='#,##0' />
  <Column id='population' title='Population' fmt='#,##0' />
  <Column id='development_intensity' title='Dev. Intensity ($)' fmt='$#,##0' />
</DataTable>

---

{#if permits_ward.length > 0}
<Alert status='info'>
  <b>Cross-Departmental Insight:</b> Wards with high residential permit activity but low water infrastructure counts may face capacity constraints. This is the type of analysis that was missing when housing was paused due to water capacity issues.
</Alert>
{/if}

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge City Foundation &middot; Development & Housing &middot; Powered by Cube + Evidence
</div>
