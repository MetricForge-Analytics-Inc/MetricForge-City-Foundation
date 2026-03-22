---
title: Case Trends & Time Series
---

# 📈 Case Trends & Time Series Analysis

[← Back to Home](/)

## Cases Created Over Time

```sql cases_by_date
SELECT 
  DATE_TRUNC('day', case_created_time) as date,
  COUNT(*) as new_cases,
  SUM(CASE WHEN case_priority = 'urgent' THEN 1 ELSE 0 END) as urgent_cases,
  SUM(CASE WHEN case_priority = 'high' THEN 1 ELSE 0 END) as high_cases
FROM memory.Foundry.cases_cube
WHERE case_created_time IS NOT NULL
GROUP BY DATE_TRUNC('day', case_created_time)
ORDER BY date DESC
LIMIT 90
```

<LineChart 
  data={cases_by_date}
  x='date'
  y='new_cases'
  title='Daily New Cases (Last 90 Days)'
  yAxisTitle='Number of Cases'
/>

## Priority Cases Trend

<LineChart 
  data={cases_by_date}
  x='date'
  y={['urgent_cases', 'high_cases']}
  title='Urgent & High Priority Cases Over Time'
  yAxisTitle='Number of Cases'
  colorPalette={['#dc2626', '#ea580c']}
/>

## Weekly Summary

```sql weekly_summary
SELECT 
  DATE_TRUNC('week', case_created_time) as week_start,
  COUNT(*) as total_cases,
  SUM(CASE WHEN case_current_status = 'solved' THEN 1 ELSE 0 END) as solved_cases,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time,
  SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) as satisfied_customers
FROM memory.Foundry.cases_cube
WHERE case_created_time >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', case_created_time)
ORDER BY week_start DESC
```

<DataTable 
  data={weekly_summary}
  rows=12
/>

<AreaChart 
  data={weekly_summary}
  x='week_start'
  y='total_cases'
  title='Weekly Case Volume'
  yAxisTitle='Cases'
/>

## Response Time Trend

```sql response_trend
SELECT 
  DATE_TRUNC('day', case_created_time) as date,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time_business,
  ROUND(AVG(case_reply_time_in_minutes_calendar), 2) as avg_reply_time_calendar,
  COUNT(*) as case_volume
FROM memory.Foundry.cases_cube
WHERE case_created_time >= CURRENT_DATE - INTERVAL '30 days'
  AND case_reply_time_in_minutes_business IS NOT NULL
GROUP BY DATE_TRUNC('day', case_created_time)
ORDER BY date
```

<LineChart 
  data={response_trend}
  x='date'
  y='avg_reply_time_business'
  title='Average Reply Time Trend (Business Hours)'
  yAxisTitle='Minutes'
/>

## Channel Trends

```sql channel_trends
SELECT 
  DATE_TRUNC('week', case_created_time) as week,
  channel,
  COUNT(*) as case_count
FROM memory.Foundry.cases_cube
WHERE case_created_time >= CURRENT_DATE - INTERVAL '12 weeks'
  AND channel IS NOT NULL
GROUP BY DATE_TRUNC('week', case_created_time), channel
ORDER BY week DESC, case_count DESC
```

<BarChart 
  data={channel_trends}
  x='week'
  y='case_count'
  series='channel'
  title='Case Volume by Channel (Weekly)'
  type='grouped'
/>
