---
title: Team Performance & SLA Metrics
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #064e3b 0%, #059669 50%, #6ee7b7 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; bottom: -25px; right: 10%; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #a7f3d0; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">⚡ Team Performance & SLAs</h1>
  <p style="margin: 0; color: #d1fae5; font-size: 1rem;">Response times, hold times, resolution efficiency, and workload distribution. Understand how your team delivers.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     TOP-LINE KPIs (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM cube_kpis
```

<BigValue data={kpis} value='avg_first_reply_min'    title='Avg First Reply'         fmt='#,##0.0" min"' />
<BigValue data={kpis} value='avg_first_reply_cal_min' title='Avg First Reply (Cal)'   fmt='#,##0.0" min"' />
<BigValue data={kpis} value='total_replies'           title='Total Agent Replies'      fmt='#,##0' />
<BigValue data={kpis} value='one_touch_pct'           title='One-Touch %'             fmt='0.0%' />
<BigValue data={kpis} value='reassigned'              title='Reassigned'              fmt='#,##0' />
<BigValue data={kpis} value='reopened'                title='Reopened'                fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     RESPONSE TIME DISTRIBUTION
     ═══════════════════════════════════════════════════════════════════ -->

## Response Time Distribution

```sql reply_time_histogram
SELECT 
  CASE 
    WHEN case_reply_time_in_minutes_business < 15 THEN '0-15 min'
    WHEN case_reply_time_in_minutes_business < 30 THEN '15-30 min'
    WHEN case_reply_time_in_minutes_business < 60 THEN '30-60 min'
    WHEN case_reply_time_in_minutes_business < 120 THEN '1-2 hours'
    WHEN case_reply_time_in_minutes_business < 240 THEN '2-4 hours'
    WHEN case_reply_time_in_minutes_business < 480 THEN '4-8 hours'
    ELSE '8+ hours'
  END as time_bucket,
  COUNT(*) as case_count
FROM cases_cube
WHERE case_reply_time_in_minutes_business IS NOT NULL
GROUP BY 
  CASE 
    WHEN case_reply_time_in_minutes_business < 15 THEN '0-15 min'
    WHEN case_reply_time_in_minutes_business < 30 THEN '15-30 min'
    WHEN case_reply_time_in_minutes_business < 60 THEN '30-60 min'
    WHEN case_reply_time_in_minutes_business < 120 THEN '1-2 hours'
    WHEN case_reply_time_in_minutes_business < 240 THEN '2-4 hours'
    WHEN case_reply_time_in_minutes_business < 480 THEN '4-8 hours'
    ELSE '8+ hours'
  END
ORDER BY 
  CASE time_bucket
    WHEN '0-15 min' THEN 1
    WHEN '15-30 min' THEN 2
    WHEN '30-60 min' THEN 3
    WHEN '1-2 hours' THEN 4
    WHEN '2-4 hours' THEN 5
    WHEN '4-8 hours' THEN 6
    ELSE 7
  END
```

<BarChart 
  data={reply_time_histogram}
  x='time_bucket'
  y='case_count'
  title='First Reply Time — Distribution'
  colorPalette={['#10b981', '#34d399', '#84cc16', '#eab308', '#f97316', '#ef4444', '#991b1b']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     REPLY TIME TREND (daily)
     ═══════════════════════════════════════════════════════════════════ -->

## Reply Time Trend

```sql daily
SELECT * FROM cube_daily_trend
```

<LineChart
  data={daily}
  x='date'
  y='avg_reply_min'
  title='Avg First Reply Time Over Time (Business Min)'
  yAxisTitle='Minutes'
  colorPalette={['#059669']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     HOLD TIME vs REPLY TIME by PRIORITY
     ═══════════════════════════════════════════════════════════════════ -->

## Hold Time vs Reply Time by Priority

```sql hold_vs_reply
SELECT 
  COALESCE(case_priority, 'Not Set') as priority,
  COUNT(*) as total_cases,
  ROUND(AVG(case_on_hold_minutes_business), 2) as avg_hold_time,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time
FROM cases_cube
WHERE case_on_hold_minutes_business IS NOT NULL
GROUP BY case_priority
ORDER BY 
  CASE case_priority
    WHEN 'urgent' THEN 1
    WHEN 'high' THEN 2
    WHEN 'normal' THEN 3
    WHEN 'low' THEN 4
    ELSE 5
  END
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={hold_vs_reply}
  x='priority'
  y={['avg_hold_time', 'avg_reply_time']}
  title='Hold Time vs Reply Time (min)'
  type='grouped'
  swapXY={true}
  colorPalette={['#f59e0b','#059669']}
/>

<DataTable 
  data={hold_vs_reply}
  rows=10
>
  <Column id='priority' title='Priority' />
  <Column id='total_cases' title='Cases' fmt='#,##0' />
  <Column id='avg_hold_time' title='Avg Hold (min)' fmt='#,##0.0' />
  <Column id='avg_reply_time' title='Avg Reply (min)' fmt='#,##0.0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     RESOLUTION EFFICIENCY — TOUCH ANALYSIS (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Resolution Efficiency — Touch Analysis

```sql touch_data
SELECT 'One-Touch' AS resolution_type,  one_touch  AS tickets, one_touch_pct AS pct FROM cube_kpis
UNION ALL
SELECT 'Two-Touch',                     two_touch,              two_touch_pct       FROM cube_kpis
UNION ALL
SELECT 'Multi-Touch',                   multi_touch,            multi_touch_pct     FROM cube_kpis
```

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
  <BigValue data={kpis} value='one_touch_pct'   title='One-Touch %'     fmt='0.0%' />
  <BigValue data={kpis} value='two_touch_pct'   title='Two-Touch %'     fmt='0.0%' />
  <BigValue data={kpis} value='multi_touch_pct' title='Multi-Touch %'   fmt='0.0%' />
</div>

<BarChart
  data={touch_data}
  x='resolution_type'
  y='tickets'
  title='Solved Cases by Resolution Effort'
  colorPalette={['#22c55e','#f59e0b','#ef4444']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     REOPEN RATE
     ═══════════════════════════════════════════════════════════════════ -->

## Reopen Rate Analysis

```sql reopen_analysis
SELECT 
  CASE 
    WHEN case_number_of_reopens = 0 THEN '0 reopens'
    WHEN case_number_of_reopens = 1 THEN '1 reopen'
    WHEN case_number_of_reopens = 2 THEN '2 reopens'
    ELSE '3+ reopens'
  END as reopen_category,
  COUNT(*) as case_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM cases_cube
GROUP BY 
  CASE 
    WHEN case_number_of_reopens = 0 THEN '0 reopens'
    WHEN case_number_of_reopens = 1 THEN '1 reopen'
    WHEN case_number_of_reopens = 2 THEN '2 reopens'
    ELSE '3+ reopens'
  END
ORDER BY 
  CASE reopen_category
    WHEN '0 reopens' THEN 1
    WHEN '1 reopen' THEN 2
    WHEN '2 reopens' THEN 3
    ELSE 4
  END
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={reopen_analysis}
  x='reopen_category'
  y='case_count'
  title='Reopen Distribution'
  colorPalette={['#22c55e','#eab308','#f97316','#ef4444']}
/>

<DataTable 
  data={reopen_analysis}
  rows=10
>
  <Column id='reopen_category' title='Reopens' />
  <Column id='case_count' title='Cases' fmt='#,##0' />
  <Column id='percentage' title='%' fmt='0.0"%"' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     REOPENED & REASSIGNED TREND
     ═══════════════════════════════════════════════════════════════════ -->

## Operational Health Trend

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
     ASSIGNEE STATION DISTRIBUTION
     ═══════════════════════════════════════════════════════════════════ -->

## Workload — Assignee Stations

```sql assignee_dist
SELECT 
  case_assignee_stations as stations,
  COUNT(*) as cases_handled,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time,
  ROUND(AVG(case_number_of_reopens), 2) as avg_reopens
FROM cases_cube
WHERE case_assignee_stations IS NOT NULL
  AND case_assignee_stations > 0
GROUP BY case_assignee_stations
ORDER BY case_assignee_stations
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={assignee_dist}
  x='stations'
  y='cases_handled'
  title='Cases by # of Assignee Stations'
  colorPalette={['#6366f1']}
/>

<DataTable 
  data={assignee_dist}
  rows=15
>
  <Column id='stations' title='Stations' />
  <Column id='cases_handled' title='Cases' fmt='#,##0' />
  <Column id='avg_reply_time' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='avg_reopens' title='Avg Reopens' fmt='0.00' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     PERFORMANCE BY PRIORITY (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Performance by Priority

```sql by_priority
SELECT * FROM cube_by_priority
```

<DataTable 
  data={by_priority}
  rows=10
>
  <Column id='priority' title='Priority' />
  <Column id='total' title='Total' fmt='#,##0' />
  <Column id='solved' title='Solved' fmt='#,##0' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='sat_score' title='CSAT' fmt='0.0%' />
  <Column id='one_touch_pct' title='One-Touch %' fmt='0.0%' />
  <Column id='reopened' title='Reopened' fmt='#,##0' />
</DataTable>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge Foundry &middot; Team Performance &middot; Powered by Cube + Evidence
</div>