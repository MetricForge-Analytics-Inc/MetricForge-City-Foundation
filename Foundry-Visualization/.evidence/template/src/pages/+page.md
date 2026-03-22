---
title: Support Analytics Dashboard
---

# 📊 Support Analytics Overview

Welcome to the MetricForge Support Analytics Dashboard. Get insights into your support operations, ticket trends, and team performance.

## Key Metrics

```sql kpis
SELECT 
  SUM(CASE WHEN case_current_status IS NOT NULL THEN 1 ELSE 0 END) as total_cases,
  SUM(CASE WHEN case_current_status = 'open' THEN 1 ELSE 0 END) as open_cases,
  SUM(CASE WHEN case_current_status = 'solved' THEN 1 ELSE 0 END) as solved_cases,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time_business_hrs,
  ROUND(AVG(case_on_hold_minutes_business), 2) as avg_hold_time_business_hrs
FROM memory.Foundry.cases_cube
```

<BigValue 
  data={kpis} 
  value='total_cases'
  title='Total Cases'
  fmt='#,##0'
/>

<BigValue 
  data={kpis} 
  value='open_cases'
  title='Open Cases'
  fmt='#,##0'
  comparison='solved_cases'
  comparisonTitle='vs Solved'
/>

<BigValue 
  data={kpis} 
  value='solved_cases'
  title='Solved Cases'
  fmt='#,##0'
/>

<BigValue 
  data={kpis} 
  value='avg_reply_time_business_hrs'
  title='Avg Reply Time'
  fmt='#,##0.0" min"'
/>

## Case Status Distribution

```sql status_breakdown
SELECT 
  case_current_status as status,
  COUNT(*) as case_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM memory.Foundry.cases_cube
WHERE case_current_status IS NOT NULL
GROUP BY case_current_status
ORDER BY case_count DESC
```

<BarChart 
  data={status_breakdown}
  x='status'
  y='case_count'
  title='Cases by Status'
  colorPalette={['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']}
/>

## Priority Distribution

```sql priority_breakdown
SELECT 
  COALESCE(case_priority, 'Not Set') as priority,
  COUNT(*) as case_count
FROM memory.Foundry.cases_cube
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

<DataTable 
  data={priority_breakdown}
  rows=10
/>

<BarChart 
  data={priority_breakdown}
  x='priority'
  y='case_count'
  title='Cases by Priority'
  swapXY=true
  colorPalette={['#dc2626', '#ea580c', '#ca8a04', '#65a30d', '#64748b']}
/>

## Channel Performance

```sql channel_stats
SELECT 
  COALESCE(channel, 'Unknown') as channel,
  COUNT(*) as total_cases,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time
FROM memory.Foundry.cases_cube
WHERE channel IS NOT NULL
GROUP BY channel
ORDER BY total_cases DESC
```

<BarChart 
  data={channel_stats}
  x='channel'
  y='total_cases'
  title='Cases by Channel'
/>

## Quick Links

- [📈 Trends & Time Series](/trends) - View case trends over time
- [⚡ Team Performance](/performance) - Analyze response times & SLAs  
- [⭐ Customer Satisfaction](/satisfaction) - Review ratings and feedback
- [🔍 Case Explorer](/cases) - Browse and search all cases