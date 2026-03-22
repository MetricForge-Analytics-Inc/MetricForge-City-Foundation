---
title: Team Performance & SLA Metrics
---

# ⚡ Team Performance & SLA Metrics

[← Back to Home](/)

## Response Time Performance

```sql response_metrics
SELECT 
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time_business,
  ROUND(MIN(case_reply_time_in_minutes_business), 2) as min_reply_time,
  ROUND(MAX(case_reply_time_in_minutes_business), 2) as max_reply_time,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY case_reply_time_in_minutes_business), 2) as median_reply_time,
  ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY case_reply_time_in_minutes_business), 2) as p95_reply_time
FROM memory.Foundry.cases_cube
WHERE case_reply_time_in_minutes_business IS NOT NULL
```

<BigValue 
  data={response_metrics} 
  value='avg_reply_time_business'
  title='Avg Reply Time'
  fmt='#,##0.0" min"'
/>

<BigValue 
  data={response_metrics} 
  value='median_reply_time'
  title='Median Reply Time'
  fmt='#,##0.0" min"'
/>

<BigValue 
  data={response_metrics} 
  value='p95_reply_time'
  title='95th Percentile'
  fmt='#,##0.0" min"'
/>

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
FROM memory.Foundry.cases_cube
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
  title='Reply Time Distribution'
  colorPalette={['#10b981', '#84cc16', '#eab308', '#f97316', '#ef4444', '#dc2626', '#991b1b']}
/>

## Hold Time Analysis

```sql hold_time_stats
SELECT 
  COALESCE(case_priority, 'Not Set') as priority,
  COUNT(*) as total_cases,
  ROUND(AVG(case_on_hold_minutes_business), 2) as avg_hold_time,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time
FROM memory.Foundry.cases_cube
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

<DataTable 
  data={hold_time_stats}
  rows=10
/>

<BarChart 
  data={hold_time_stats}
  x='priority'
  y={['avg_hold_time', 'avg_reply_time']}
  title='Hold Time vs Reply Time by Priority'
  type='grouped'
  swapXY=true
/>

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
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM memory.Foundry.cases_cube
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

<BigValue 
  data={reopen_analysis}
  value='percentage'
  where="reopen_category = '0 reopens'"
  title='First Contact Resolution'
  fmt='#,##0.0"%"'
/>

<BarChart 
  data={reopen_analysis}
  x='reopen_category'
  y='case_count'
  title='Case Reopen Distribution'
/>

## Assignee Activity

```sql assignee_stats
SELECT 
  case_assignee_stations,
  COUNT(*) as cases_handled,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time
FROM memory.Foundry.cases_cube
WHERE case_assignee_stations IS NOT NULL
  AND case_assignee_stations > 0
GROUP BY case_assignee_stations
ORDER BY cases_handled DESC
LIMIT 20
```

<DataTable 
  data={assignee_stats}
  rows=15
/>
