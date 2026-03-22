---
title: Customer Satisfaction Analysis
---

# ⭐ Customer Satisfaction Analysis

[← Back to Home](/)

## Overall Satisfaction

```sql satisfaction_overview
SELECT 
  SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END) as rated_cases,
  COUNT(*) as total_cases,
  ROUND(SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) as response_rate,
  SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) as satisfied,
  SUM(CASE WHEN case_satisfaction_rating = 'bad' THEN 1 ELSE 0 END) as dissatisfied
FROM memory.Foundry.cases_cube
```

<BigValue 
  data={satisfaction_overview} 
  value='response_rate'
  title='Survey Response Rate'
  fmt='#,##0.0"%"'
/>

```sql satisfaction_score
SELECT 
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END), 0), 2) as satisfaction_score
FROM memory.Foundry.cases_cube
```

<BigValue 
  data={satisfaction_score} 
  value='satisfaction_score'
  title='Satisfaction Score'
  fmt='#,##0.0"%"'
/>

## Satisfaction Distribution

```sql satisfaction_breakdown
SELECT 
  COALESCE(case_satisfaction_rating, 'Not Rated') as rating,
  COUNT(*) as case_count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM memory.Foundry.cases_cube
GROUP BY case_satisfaction_rating
ORDER BY 
  CASE case_satisfaction_rating
    WHEN 'good' THEN 1
    WHEN 'bad' THEN 2
    ELSE 3
  END
```

<BarChart 
  data={satisfaction_breakdown}
  x='rating'
  y='case_count'
  title='Satisfaction Ratings Distribution'
  colorPalette={['#10b981', '#ef4444', '#94a3b8']}
/>

## Satisfaction by Priority

```sql satisfaction_by_priority
SELECT 
  COALESCE(case_priority, 'Not Set') as priority,
  SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) as satisfied,
  SUM(CASE WHEN case_satisfaction_rating = 'bad' THEN 1 ELSE 0 END) as dissatisfied,
  SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END) as total_rated,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END), 0), 2) as satisfaction_pct
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
  data={satisfaction_by_priority}
  rows=10
/>

<BarChart 
  data={satisfaction_by_priority}
  x='priority'
  y='satisfaction_pct'
  title='Satisfaction % by Priority Level'
  swapXY=true
/>

## Satisfaction by Channel

```sql satisfaction_by_channel
SELECT 
  COALESCE(channel, 'Unknown') as channel,
  SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) as satisfied,
  SUM(CASE WHEN case_satisfaction_rating = 'bad' THEN 1 ELSE 0 END) as dissatisfied,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END), 0), 2) as satisfaction_pct
FROM memory.Foundry.cases_cube
WHERE channel IS NOT NULL
GROUP BY channel
ORDER BY satisfaction_pct DESC
```

<BarChart 
  data={satisfaction_by_channel}
  x='channel'
  y={['satisfied', 'dissatisfied']}
  title='Satisfaction by Channel'
  type='stacked'
/>

## Satisfaction Trend Over Time

```sql satisfaction_trend
SELECT 
  DATE_TRUNC('week', case_created_time) as week,
  SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) as satisfied,
  SUM(CASE WHEN case_satisfaction_rating = 'bad' THEN 1 ELSE 0 END) as dissatisfied,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END), 0), 2) as satisfaction_score
FROM memory.Foundry.cases_cube
WHERE case_created_time >= CURRENT_DATE - INTERVAL '12 weeks'
GROUP BY DATE_TRUNC('week', case_created_time)
ORDER BY week
```

<LineChart 
  data={satisfaction_trend}
  x='week'
  y='satisfaction_score'
  title='Weekly Satisfaction Score Trend'
  yAxisTitle='Satisfaction %'
/>

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
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END), 0), 2) as satisfaction_pct,
  SUM(CASE WHEN case_satisfaction_rating IS NOT NULL THEN 1 ELSE 0 END) as rated_cases
FROM memory.Foundry.cases_cube
WHERE case_reply_time_in_minutes_business IS NOT NULL
  AND case_satisfaction_rating IS NOT NULL
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

<BarChart 
  data={reply_satisfaction}
  x='reply_time_bucket'
  y='satisfaction_pct'
  title='Satisfaction % by Reply Time'
/>
