---
title: Customer Satisfaction Analysis
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #713f12 0%, #ca8a04 45%, #fde047 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; top: -20px; left: 60%; width: 160px; height: 160px; background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #fef9c3; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">⭐ Customer Satisfaction</h1>
  <p style="margin: 0; color: #fef3c7; font-size: 1rem;">CSAT scores, survey response rates, and the levers that drive customer happiness — reply speed, channel, and priority.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     TOP-LINE KPIs (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM cube_kpis
```

<BigValue data={kpis} value='satisfaction_score'  title='CSAT Score'            fmt='0.0%' />
<BigValue data={kpis} value='good_sat'            title='Good Ratings'          fmt='#,##0' />
<BigValue data={kpis} value='bad_sat'             title='Bad Ratings'           fmt='#,##0' />
<BigValue data={kpis} value='rated_sat'           title='Rated Tickets'         fmt='#,##0' />
<BigValue data={kpis} value='surveyed_sat'        title='Surveyed Tickets'      fmt='#,##0' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION FUNNEL
     ═══════════════════════════════════════════════════════════════════ -->

## Satisfaction Funnel

```sql sat_funnel
SELECT 'Total Created'   AS stage, total_created AS tickets, 1 AS sort FROM cube_kpis
UNION ALL
SELECT 'Surveyed',                  surveyed_sat,             2        FROM cube_kpis
UNION ALL
SELECT 'Rated (Good+Bad)',          rated_sat,                3        FROM cube_kpis
UNION ALL
SELECT 'Good',                      good_sat,                 4        FROM cube_kpis
```

<BarChart
  data={sat_funnel}
  x='stage'
  y='tickets'
  title='From Created to Satisfied — The Funnel'
  colorPalette={['#6366f1','#0ea5e9','#f59e0b','#22c55e']}
  sort={false}
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION DISTRIBUTION
     ═══════════════════════════════════════════════════════════════════ -->

## Rating Distribution

```sql satisfaction_breakdown
SELECT 
  COALESCE(case_satisfaction_rating, 'Not Rated') as rating,
  COUNT(*) as case_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM cases_cube
GROUP BY case_satisfaction_rating
ORDER BY 
  CASE case_satisfaction_rating
    WHEN 'good' THEN 1
    WHEN 'bad' THEN 2
    WHEN 'offered' THEN 3
    WHEN 'unoffered' THEN 4
    ELSE 5
  END
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={satisfaction_breakdown}
  x='rating'
  y='case_count'
  title='Satisfaction Ratings'
  colorPalette={['#22c55e', '#ef4444', '#0ea5e9', '#94a3b8', '#64748b']}
/>

<DataTable 
  data={satisfaction_breakdown}
  rows=10
>
  <Column id='rating' title='Rating' />
  <Column id='case_count' title='Cases' fmt='#,##0' />
  <Column id='percentage' title='%' fmt='0.0"%"' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION BY PRIORITY (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Satisfaction by Priority

```sql by_priority
SELECT * FROM cube_by_priority
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={by_priority}
  x='priority'
  y='sat_score'
  title='CSAT Score by Priority'
  swapXY={true}
  colorPalette={['#22c55e','#84cc16','#eab308','#f97316','#64748b']}
  fmt='0.0%'
/>

<DataTable 
  data={by_priority}
  rows=10
>
  <Column id='priority' title='Priority' />
  <Column id='total' title='Cases' fmt='#,##0' />
  <Column id='sat_score' title='CSAT' fmt='0.0%' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='one_touch_pct' title='One-Touch %' fmt='0.0%' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION BY CHANNEL (Cube measures)
     ═══════════════════════════════════════════════════════════════════ -->

## Satisfaction by Channel

```sql by_channel
SELECT * FROM cube_by_channel
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={by_channel}
  x='channel'
  y='sat_score'
  title='CSAT Score by Channel'
  colorPalette={['#22c55e','#84cc16','#eab308','#f97316','#ef4444','#64748b']}
  fmt='0.0%'
/>

<DataTable 
  data={by_channel}
  rows=10
>
  <Column id='channel' title='Channel' />
  <Column id='total' title='Cases' fmt='#,##0' />
  <Column id='sat_score' title='CSAT' fmt='0.0%' />
  <Column id='avg_reply_min' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='one_touch_pct' title='One-Touch %' fmt='0.0%' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     SATISFACTION TREND OVER TIME
     ═══════════════════════════════════════════════════════════════════ -->

## CSAT Trend Over Time

```sql daily
SELECT * FROM cube_daily_trend
```

<AreaChart
  data={daily}
  x='date'
  y={['good_sat','bad_sat']}
  title='Good vs Bad Satisfaction Ratings Over Time'
  yAxisTitle='Tickets'
  colorPalette={['#22c55e','#ef4444']}
  fillOpacity=0.2
/>

---

<!-- ═══════════════════════════════════════════════════════════════════
     REPLY TIME vs SATISFACTION
     ═══════════════════════════════════════════════════════════════════ -->

## Correlation: Reply Time vs Satisfaction

```sql reply_satisfaction
SELECT 
  CASE 
    WHEN case_reply_time_in_minutes_business < 30 THEN '< 30 min'
    WHEN case_reply_time_in_minutes_business < 60 THEN '30-60 min'
    WHEN case_reply_time_in_minutes_business < 120 THEN '1-2 hours'
    WHEN case_reply_time_in_minutes_business < 240 THEN '2-4 hours'
    ELSE '4+ hours'
  END as reply_time_bucket,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IN ('good','bad') THEN 1 ELSE 0 END), 0), 1) as satisfaction_pct,
  SUM(CASE WHEN case_satisfaction_rating IN ('good','bad') THEN 1 ELSE 0 END) as rated_cases
FROM cases_cube
WHERE case_reply_time_in_minutes_business IS NOT NULL
  AND case_satisfaction_rating IN ('good','bad')
GROUP BY 
  CASE 
    WHEN case_reply_time_in_minutes_business < 30 THEN '< 30 min'
    WHEN case_reply_time_in_minutes_business < 60 THEN '30-60 min'
    WHEN case_reply_time_in_minutes_business < 120 THEN '1-2 hours'
    WHEN case_reply_time_in_minutes_business < 240 THEN '2-4 hours'
    ELSE '4+ hours'
  END
ORDER BY 
  CASE reply_time_bucket
    WHEN '< 30 min' THEN 1
    WHEN '30-60 min' THEN 2
    WHEN '1-2 hours' THEN 3
    WHEN '2-4 hours' THEN 4
    ELSE 5
  END
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={reply_satisfaction}
  x='reply_time_bucket'
  y='satisfaction_pct'
  title='CSAT % by Reply Time Bucket'
  colorPalette={['#22c55e','#84cc16','#eab308','#f97316','#ef4444']}
/>

<DataTable 
  data={reply_satisfaction}
  rows=10
>
  <Column id='reply_time_bucket' title='Reply Time' />
  <Column id='satisfaction_pct' title='CSAT %' fmt='0.0"%"' />
  <Column id='rated_cases' title='Rated Cases' fmt='#,##0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     RESOLUTION EFFORT vs SATISFACTION
     ═══════════════════════════════════════════════════════════════════ -->

## Resolution Effort vs Satisfaction

```sql touch_sat
SELECT 
  CASE 
    WHEN case_number_of_replies < 2 THEN 'One-Touch'
    WHEN case_number_of_replies = 2 THEN 'Two-Touch'
    ELSE 'Multi-Touch'
  END as resolution_type,
  COUNT(*) as total_cases,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IN ('good','bad') THEN 1 ELSE 0 END), 0), 1) as sat_pct
FROM cases_cube
WHERE case_current_status IN ('solved','closed')
GROUP BY 
  CASE 
    WHEN case_number_of_replies < 2 THEN 'One-Touch'
    WHEN case_number_of_replies = 2 THEN 'Two-Touch'
    ELSE 'Multi-Touch'
  END
ORDER BY 
  CASE resolution_type
    WHEN 'One-Touch' THEN 1
    WHEN 'Two-Touch' THEN 2
    ELSE 3
  END
```

<BarChart
  data={touch_sat}
  x='resolution_type'
  y='sat_pct'
  title='CSAT % by Resolution Effort'
  colorPalette={['#22c55e','#f59e0b','#ef4444']}
/>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge Foundry &middot; Customer Satisfaction &middot; Powered by Cube + Evidence
</div>