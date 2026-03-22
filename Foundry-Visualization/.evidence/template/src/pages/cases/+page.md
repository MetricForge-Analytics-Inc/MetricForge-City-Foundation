---
title: Case Details & Explorer
---

# 🔍 Case Details & Explorer

[← Back to Home](/)

## Recent Cases

```sql recent_cases
SELECT 
  case_subject,
  case_priority,
  case_current_status,
  channel,
  case_created_time,
  case_reply_time_in_minutes_business,
  case_satisfaction_rating,
  case_number_of_reopens
FROM memory.Foundry.cases_cube
ORDER BY case_created_time DESC
LIMIT 100
```

<DataTable 
  data={recent_cases}
  rows=20
  search=true
/>

## High Priority Cases

```sql high_priority
SELECT 
  case_subject,
  case_priority,
  case_current_status,
  channel,
  case_created_time,
  ROUND(case_reply_time_in_minutes_business / 60.0, 2) as reply_hours,
  case_number_of_reopens
FROM memory.Foundry.cases_cube
WHERE case_priority IN ('urgent', 'high')
ORDER BY 
  CASE case_priority
    WHEN 'urgent' THEN 1
    WHEN 'high' THEN 2
    ELSE 3
  END,
  case_created_time DESC
LIMIT 50
```

<DataTable 
  data={high_priority}
  rows=15
  search=true
/>

## Cases Requiring Attention

```sql attention_needed
SELECT 
  case_subject,
  case_priority,
  case_current_status,
  channel,
  case_created_time,
  case_number_of_reopens,
  CASE 
    WHEN case_current_status = 'open' AND case_priority = 'urgent' THEN 'Urgent & Open'
    WHEN case_number_of_reopens > 2 THEN 'Multiple Reopens'
    WHEN case_satisfaction_rating = 'bad' THEN 'Poor Satisfaction'
    ELSE 'Other'
  END as attention_reason
FROM memory.Foundry.cases_cube
WHERE 
  (case_current_status = 'open' AND case_priority = 'urgent')
  OR case_number_of_reopens > 2
  OR case_satisfaction_rating = 'bad'
ORDER BY 
  CASE 
    WHEN case_current_status = 'open' AND case_priority = 'urgent' THEN 1
    WHEN case_number_of_reopens > 2 THEN 2
    WHEN case_satisfaction_rating = 'bad' THEN 3
    ELSE 4
  END,
  case_created_time DESC
LIMIT 50
```

{#if attention_needed.length > 0}
<Alert status='warning'>
  There are {attention_needed.length} cases requiring attention
</Alert>
{/if}

<DataTable 
  data={attention_needed}
  rows=15
  search=true
/>

## Case Type Analysis

```sql case_types
SELECT 
  COALESCE(case_type, 'Not Specified') as case_type,
  COUNT(*) as total_cases,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time,
  SUM(CASE WHEN case_current_status = 'solved' THEN 1 ELSE 0 END) as solved,
  ROUND(SUM(CASE WHEN case_current_status = 'solved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as solve_rate
FROM memory.Foundry.cases_cube
GROUP BY case_type
ORDER BY total_cases DESC
```

<DataTable 
  data={case_types}
  rows=10
/>

<BarChart 
  data={case_types}
  x='case_type'
  y='total_cases'
  title='Cases by Type'
  swapXY=true
/>

## Topic Distribution

```sql topics
SELECT 
  COALESCE(case_topic, 'No Topic') as topic,
  COUNT(*) as case_count,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time
FROM memory.Foundry.cases_cube
GROUP BY case_topic
ORDER BY case_count DESC
LIMIT 15
```

<BarChart 
  data={topics}
  x='topic'
  y='case_count'
  title='Top Topics'
  swapXY=true
/>
