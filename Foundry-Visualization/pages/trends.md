---
title: Case Trends & Time Series
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #4c1d95 0%, #7c3aed 45%, #c4b5fd 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; bottom: -30px; right: 5%; width: 200px; height: 200px; background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #ddd6fe; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">📈 Trends & Time Series</h1>
  <p style="margin: 0; color: #ede9fe; font-size: 1rem;">Spot patterns in case volume, response times, channel mix, and operational health across daily, weekly, and monthly windows.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     DAILY CASE FLOW  (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Daily Case Flow — Created vs Solved

```sql daily
SELECT * FROM cube_daily_trend
```

<AreaChart
  data={daily}
  x='date'
  y={['created','solved']}
  title='Daily Created vs Solved'
  yAxisTitle='Cases'
  colorPalette={['#7c3aed','#22c55e']}
  fillOpacity=0.15
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     PRIORITY CASE TREND
     ═══════════════════════════════════════════════════════════════════ -->

## Priority Cases Over Time

```sql priority_trend
SELECT 
  DATE_TRUNC('day', case_created_time) as date,
  SUM(CASE WHEN case_priority = 'urgent' THEN 1 ELSE 0 END) as urgent,
  SUM(CASE WHEN case_priority = 'high' THEN 1 ELSE 0 END) as high,
  SUM(CASE WHEN case_priority = 'normal' THEN 1 ELSE 0 END) as normal,
  SUM(CASE WHEN case_priority = 'low' THEN 1 ELSE 0 END) as low
FROM cases_cube
WHERE case_created_time IS NOT NULL
GROUP BY DATE_TRUNC('day', case_created_time)
ORDER BY date
```

<AreaChart 
  data={priority_trend}
  x='date'
  y={['urgent', 'high', 'normal', 'low']}
  title='Daily Volume by Priority'
  yAxisTitle='Cases'
  colorPalette={['#dc2626', '#ea580c', '#ca8a04', '#65a30d']}
  fillOpacity=0.12
  type='stacked'
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
  title='Avg First Reply Time (Business Min) Over Time'
  yAxisTitle='Minutes'
  colorPalette={['#f59e0b']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     WEEKLY SUMMARY TABLE
     ═══════════════════════════════════════════════════════════════════ -->

## Weekly Summary

```sql weekly_summary
SELECT 
  DATE_TRUNC('week', case_created_time) as week,
  COUNT(*) as total_cases,
  SUM(CASE WHEN case_current_status IN ('solved','closed') THEN 1 ELSE 0 END) as solved,
  SUM(CASE WHEN case_number_of_reopens > 0 THEN 1 ELSE 0 END) as reopened,
  ROUND(AVG(case_reply_time_in_minutes_business), 1) as avg_reply_min,
  SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) as good_sat,
  SUM(CASE WHEN case_satisfaction_rating = 'bad' THEN 1 ELSE 0 END) as bad_sat
FROM cases_cube
WHERE case_created_time IS NOT NULL
GROUP BY DATE_TRUNC('week', case_created_time)
ORDER BY week DESC
```

<DataTable 
  data={weekly_summary}
  rows=12
>
  <Column id='week' title='Week' />
  <Column id='total_cases' title='Created' fmt='#,##0' />
  <Column id='solved' title='Solved' fmt='#,##0' />
  <Column id='reopened' title='Reopened' fmt='#,##0' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='good_sat' title='Good CSAT' fmt='#,##0' />
  <Column id='bad_sat' title='Bad CSAT' fmt='#,##0' />
</DataTable>

<AreaChart 
  data={weekly_summary}
  x='week'
  y='total_cases'
  title='Weekly Case Volume'
  yAxisTitle='Cases'
  colorPalette={['#7c3aed']}
  fillOpacity=0.2
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     CHANNEL TRENDS
     ═══════════════════════════════════════════════════════════════════ -->

## Channel Volume Trends

```sql channel_weekly
SELECT 
  DATE_TRUNC('week', case_created_time) as week,
  channel,
  COUNT(*) as case_count
FROM cases_cube
WHERE case_created_time IS NOT NULL
  AND channel IS NOT NULL
GROUP BY DATE_TRUNC('week', case_created_time), channel
ORDER BY week, case_count DESC
```

<BarChart 
  data={channel_weekly}
  x='week'
  y='case_count'
  series='channel'
  title='Weekly Case Volume by Channel'
  type='stacked'
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#ef4444','#a855f7']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     ONE-TOUCH TREND
     ═══════════════════════════════════════════════════════════════════ -->

## One-Touch Resolution Trend

<AreaChart
  data={daily}
  x='date'
  y='one_touch'
  title='Daily One-Touch Resolutions'
  yAxisTitle='Cases'
  colorPalette={['#22c55e']}
  fillOpacity=0.2
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
  title='Reopened & Reassigned Over Time'
  yAxisTitle='Cases'
  colorPalette={['#ef4444','#a855f7']}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION TREND
     ═══════════════════════════════════════════════════════════════════ -->

## Satisfaction Trend

<AreaChart
  data={daily}
  x='date'
  y={['good_sat','bad_sat']}
  title='Good vs Bad Satisfaction Over Time'
  yAxisTitle='Tickets'
  colorPalette={['#22c55e','#ef4444']}
  fillOpacity=0.2
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     MONTHLY SUMMARY
     ═══════════════════════════════════════════════════════════════════ -->

## Monthly Summary

```sql monthly
SELECT 
  DATE_TRUNC('month', case_created_time) as month,
  COUNT(*) as created,
  SUM(CASE WHEN case_current_status IN ('solved','closed') THEN 1 ELSE 0 END) as solved,
  SUM(CASE WHEN case_number_of_reopens > 0 THEN 1 ELSE 0 END) as reopened,
  ROUND(AVG(case_reply_time_in_minutes_business), 1) as avg_reply_min,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IN ('good','bad') THEN 1 ELSE 0 END), 0), 1) as sat_pct
FROM cases_cube
WHERE case_created_time IS NOT NULL
GROUP BY DATE_TRUNC('month', case_created_time)
ORDER BY month DESC
```

<DataTable 
  data={monthly}
  rows=12
>
  <Column id='month' title='Month' />
  <Column id='created' title='Created' fmt='#,##0' />
  <Column id='solved' title='Solved' fmt='#,##0' />
  <Column id='reopened' title='Reopened' fmt='#,##0' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='sat_pct' title='CSAT %' fmt='0.0"%"' />
</DataTable>

<BarChart
  data={monthly}
  x='month'
  y={['created','solved']}
  title='Monthly Created vs Solved'
  type='grouped'
  colorPalette={['#7c3aed','#22c55e']}
/>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge Foundry &middot; Trends &middot; Powered by Cube + Evidence
</div>