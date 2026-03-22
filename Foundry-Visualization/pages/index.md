---
title: Support Analytics Dashboard
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #0ea5e9 100%); border-radius: 1.25rem; padding: 2.5rem 2.5rem 2rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; top: -40px; right: -40px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(14,165,233,0.35) 0%, transparent 70%); border-radius: 50%;"></div>
  <div style="position: absolute; bottom: -30px; left: 30%; width: 180px; height: 180px; background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%); border-radius: 50%;"></div>
  <div style="position: relative; z-index: 1;">
    <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.15em; color: #7dd3fc; margin-bottom: 0.5rem;">MetricForge Foundry</div>
    <h1 style="margin: 0 0 0.4rem; font-size: 2.4rem; font-weight: 800; line-height: 1.1;">Support Analytics</h1>
    <p style="margin: 0; font-size: 1.05rem; color: #cbd5e1; max-width: 600px;">Real-time insights into ticket lifecycle, agent efficiency, customer satisfaction, and operational health — powered by your Cube semantic layer.</p>
  </div>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     TOP-LINE KPIs  (from Cube.js pre-computed measures)
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM cube_kpis
```

<BigValue data={kpis} value='total_created'   title='Total Cases Created' fmt='#,##0' />
<BigValue data={kpis} value='total_solved'     title='Solved'              fmt='#,##0' comparison='total_created' comparisonTitle='of Total Created' comparisonFmt='#,##0' />
<BigValue data={kpis} value='avg_first_reply_min' title='Avg First Reply'  fmt='#,##0.0" min"' />
<BigValue data={kpis} value='satisfaction_score'   title='CSAT Score'      fmt='0.0%' />
<BigValue data={kpis} value='one_touch_pct'    title='One-Touch Resolution' fmt='0.0%' />
<BigValue data={kpis} value='reopened'         title='Reopened'            fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     VOLUME HEADLINES  (origin & incident mix)
     ═══════════════════════════════════════════════════════════════════ -->

## Ticket Origins & Incident Mix

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
  <BigValue data={kpis} value='end_user_created'  title='End-User Created' fmt='#,##0' />
  <BigValue data={kpis} value='agent_created'      title='Agent Created'    fmt='#,##0' />
  <BigValue data={kpis} value='incidents'          title='Incidents'        fmt='#,##0' />
  <BigValue data={kpis} value='problems'           title='Problems'         fmt='#,##0' />
  <BigValue data={kpis} value='reassigned'         title='Reassigned'       fmt='#,##0' />
  <BigValue data={kpis} value='total_replies'      title='Total Replies'    fmt='#,##0' />
</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     DAILY TREND — Created vs Solved sparkline
     ═══════════════════════════════════════════════════════════════════ -->

## Daily Case Flow

```sql daily
SELECT * FROM cube_daily_trend
```

<AreaChart
  data={daily}
  x='date'
  y={['created','solved']}
  title='Cases Created vs Solved Over Time'
  yAxisTitle='Cases'
  colorPalette={['#6366f1','#22c55e']}
  fillOpacity=0.15
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     FIRST REPLY TIME TREND
     ═══════════════════════════════════════════════════════════════════ -->

## First Reply Time Trend

<LineChart
  data={daily}
  x='date'
  y='avg_reply_min'
  title='Avg First Reply Time (Business Minutes)'
  yAxisTitle='Minutes'
  colorPalette={['#f59e0b']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     STATUS BREAKDOWN  (from Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Case Status Breakdown

```sql by_status
SELECT * FROM cube_by_status
```

<div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_status}
  x='status'
  y='total'
  title='Volume by Status'
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444','#64748b']}
/>

<DataTable
  data={by_status}
  rows=10
>
  <Column id='status' title='Status' />
  <Column id='total' title='Cases' fmt='#,##0' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='sat_score' title='CSAT' fmt='0.0%' />
  <Column id='reopened' title='Reopened' fmt='#,##0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     PRIORITY MIX  (from Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Priority Performance

```sql by_priority
SELECT * FROM cube_by_priority
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_priority}
  x='priority'
  y='total'
  title='Volume by Priority'
  swapXY={true}
  colorPalette={['#dc2626','#ea580c','#ca8a04','#65a30d','#64748b']}
/>

<BarChart
  data={by_priority}
  x='priority'
  y='avg_reply_min'
  title='Avg First Reply by Priority (min)'
  swapXY={true}
  colorPalette={['#0ea5e9','#38bdf8','#7dd3fc','#bae6fd','#e0f2fe']}
/>

</div>

<DataTable
  data={by_priority}
  rows=10
>
  <Column id='priority' title='Priority' />
  <Column id='total' title='Cases' fmt='#,##0' />
  <Column id='solved' title='Solved' fmt='#,##0' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='sat_score' title='CSAT' fmt='0.0%' />
  <Column id='one_touch_pct' title='One-Touch %' fmt='0.0%' />
  <Column id='reopened' title='Reopened' fmt='#,##0' />
</DataTable>

---

<!-- ═══════════════════════════════════════════════════════════════════
     CHANNEL ANALYSIS  (from Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Channel Analysis

```sql by_channel
SELECT * FROM cube_by_channel
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart
  data={by_channel}
  x='channel'
  y='total'
  title='Volume by Channel'
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444','#a855f7']}
/>

<BarChart
  data={by_channel}
  x='channel'
  y='avg_reply_min'
  title='Avg First Reply by Channel (min)'
  colorPalette={['#f59e0b','#fbbf24','#fcd34d','#fde68a','#fef3c7','#fffbeb']}
/>

</div>

<DataTable
  data={by_channel}
  rows=10
>
  <Column id='channel' title='Channel' />
  <Column id='total' title='Cases' fmt='#,##0' />
  <Column id='solved' title='Solved' fmt='#,##0' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='sat_score' title='CSAT' fmt='0.0%' />
  <Column id='one_touch_pct' title='One-Touch %' fmt='0.0%' />
</DataTable>

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION & RESOLUTION QUALITY
     ═══════════════════════════════════════════════════════════════════ -->

## Satisfaction & Resolution Quality

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
  <BigValue data={kpis} value='good_sat'       title='Good Ratings'      fmt='#,##0' />
  <BigValue data={kpis} value='bad_sat'        title='Bad Ratings'       fmt='#,##0' />
  <BigValue data={kpis} value='rated_sat'      title='Rated Tickets'     fmt='#,##0' />
  <BigValue data={kpis} value='surveyed_sat'   title='Surveyed Tickets'  fmt='#,##0' />
  <BigValue data={kpis} value='one_touch_pct'  title='One-Touch %'       fmt='0.0%' />
  <BigValue data={kpis} value='multi_touch_pct' title='Multi-Touch %'    fmt='0.0%' />
</div>

```sql touch_data
SELECT 'One-Touch' AS resolution_type,  one_touch  AS tickets FROM cube_kpis
UNION ALL
SELECT 'Two-Touch',                     two_touch           FROM cube_kpis
UNION ALL
SELECT 'Multi-Touch',                   multi_touch         FROM cube_kpis
```

<BarChart
  data={touch_data}
  x='resolution_type'
  y='tickets'
  title='Resolution Effort Distribution'
  colorPalette={['#22c55e','#f59e0b','#ef4444']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     REOPENED & REASSIGNED TREND
     ═══════════════════════════════════════════════════════════════════ -->

## Operational Health — Reopens & Reassignments

<LineChart
  data={daily}
  x='date'
  y={['reopened','reassigned']}
  title='Reopened & Reassigned Cases Over Time'
  yAxisTitle='Cases'
  colorPalette={['#ef4444','#a855f7']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     NAVIGATION CARDS
     ═══════════════════════════════════════════════════════════════════ -->

## Explore More

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; margin-top: 0.5rem;">

  <a href="/trends" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #ede9fe 0%, #c4b5fd 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">📈</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #4c1d95;">Trends & Time Series</div>
      <div style="font-size: 0.9rem; color: #6d28d9; margin-top: 0.25rem;">Daily, weekly & monthly patterns</div>
    </div>
  </a>

  <a href="/performance" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #ecfdf5 0%, #6ee7b7 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">⚡</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #064e3b;">Team Performance</div>
      <div style="font-size: 0.9rem; color: #047857; margin-top: 0.25rem;">SLAs, response times & workload</div>
    </div>
  </a>

  <a href="/satisfaction" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #fefce8 0%, #fde047 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">⭐</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #713f12;">Customer Satisfaction</div>
      <div style="font-size: 0.9rem; color: #a16207; margin-top: 0.25rem;">CSAT, surveys & sentiment</div>
    </div>
  </a>

  <a href="/cases" style="text-decoration: none; color: inherit;">
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #93c5fd 100%); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.15s;">
      <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">🔍</div>
      <div style="font-weight: 700; font-size: 1.1rem; color: #1e3a8a;">Case Explorer</div>
      <div style="font-size: 0.9rem; color: #1d4ed8; margin-top: 0.25rem;">Search, filter & drill into details</div>
    </div>
  </a>

</div>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem; padding-bottom: 1rem;">
  MetricForge Foundry &middot; Support Analytics &middot; Powered by Cube + Evidence
</div>