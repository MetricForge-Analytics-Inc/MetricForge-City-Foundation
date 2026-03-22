---
title: Case Explorer
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #93c5fd 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; top: -30px; right: -30px; width: 180px; height: 180px; background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #bfdbfe; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">🔍 Case Explorer</h1>
  <p style="margin: 0; color: #dbeafe; font-size: 1rem;">Browse, search, and drill into individual support cases. Identify cases that need attention and understand patterns across types and topics.</p>
</div>

<!-- ═══════════════════════════════════════════════════════════════════
     SNAPSHOT KPIs
     ═══════════════════════════════════════════════════════════════════ -->

```sql kpis
SELECT * FROM cube_kpis
```

<BigValue data={kpis} value='total_created'        title='Total Cases'         fmt='#,##0' />
<BigValue data={kpis} value='incidents'             title='Incidents'           fmt='#,##0' />
<BigValue data={kpis} value='problems'              title='Problems'            fmt='#,##0' />
<BigValue data={kpis} value='reopened'              title='Reopened'            fmt='#,##0' />
<BigValue data={kpis} value='avg_first_reply_min'   title='Avg First Reply'    fmt='#,##0.0" min"' />

---

<!-- ═══════════════════════════════════════════════════════════════════
     RECENT CASES
     ═══════════════════════════════════════════════════════════════════ -->

## Recent Cases

```sql recent_cases
SELECT 
  case_id,
  case_subject,
  case_priority,
  case_current_status,
  case_type,
  channel,
  case_created_time,
  case_reply_time_in_minutes_business,
  case_satisfaction_rating,
  case_number_of_reopens,
  case_number_of_replies
FROM cases_cube
ORDER BY case_created_time DESC
LIMIT 100
```

<DataTable 
  data={recent_cases}
  rows=20
  search=true
>
  <Column id='case_id' title='ID' />
  <Column id='case_subject' title='Subject' />
  <Column id='case_priority' title='Priority' />
  <Column id='case_current_status' title='Status' />
  <Column id='case_type' title='Type' />
  <Column id='channel' title='Channel' />
  <Column id='case_created_time' title='Created' />
  <Column id='case_reply_time_in_minutes_business' title='Reply (min)' fmt='#,##0.0' />
  <Column id='case_satisfaction_rating' title='CSAT' />
  <Column id='case_number_of_reopens' title='Reopens' />
  <Column id='case_number_of_replies' title='Replies' />
</DataTable>

---

<!-- ═══════════════════════════════════════════════════════════════════
     HIGH PRIORITY CASES
     ═══════════════════════════════════════════════════════════════════ -->

## 🔴 High Priority Cases

```sql high_priority
SELECT 
  case_id,
  case_subject,
  case_priority,
  case_current_status,
  channel,
  case_created_time,
  case_reply_time_in_minutes_business,
  case_number_of_reopens,
  case_number_of_replies
FROM cases_cube
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
>
  <Column id='case_id' title='ID' />
  <Column id='case_subject' title='Subject' />
  <Column id='case_priority' title='Priority' />
  <Column id='case_current_status' title='Status' />
  <Column id='channel' title='Channel' />
  <Column id='case_created_time' title='Created' />
  <Column id='case_reply_time_in_minutes_business' title='Reply (min)' fmt='#,##0.0' />
  <Column id='case_number_of_reopens' title='Reopens' />
  <Column id='case_number_of_replies' title='Replies' />
</DataTable>

---

<!-- ═══════════════════════════════════════════════════════════════════
     CASES REQUIRING ATTENTION
     ═══════════════════════════════════════════════════════════════════ -->

## ⚠️ Cases Requiring Attention

```sql attention_needed
SELECT 
  case_id,
  case_subject,
  case_priority,
  case_current_status,
  channel,
  case_created_time,
  case_number_of_reopens,
  case_satisfaction_rating,
  CASE 
    WHEN case_current_status = 'open' AND case_priority = 'urgent' THEN '🔴 Urgent & Open'
    WHEN case_number_of_reopens > 2 THEN '🔄 Multiple Reopens'
    WHEN case_satisfaction_rating = 'bad' THEN '👎 Poor Satisfaction'
    ELSE 'Other'
  END as attention_reason
FROM cases_cube
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
  <b>{attention_needed.length} cases</b> need your attention — urgent open tickets, repeated reopens, or poor satisfaction.
</Alert>
{/if}

<DataTable 
  data={attention_needed}
  rows=15
  search=true
>
  <Column id='attention_reason' title='Reason' />
  <Column id='case_id' title='ID' />
  <Column id='case_subject' title='Subject' />
  <Column id='case_priority' title='Priority' />
  <Column id='case_current_status' title='Status' />
  <Column id='channel' title='Channel' />
  <Column id='case_created_time' title='Created' />
  <Column id='case_number_of_reopens' title='Reopens' />
</DataTable>

---

<!-- ═══════════════════════════════════════════════════════════════════
     CASE TYPE ANALYSIS
     ═══════════════════════════════════════════════════════════════════ -->

## 📂 Case Type Analysis

```sql case_types
SELECT 
  COALESCE(case_type, 'Not Specified') as case_type,
  COUNT(*) as total_cases,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time,
  SUM(CASE WHEN case_current_status IN ('solved','closed') THEN 1 ELSE 0 END) as solved,
  ROUND(SUM(CASE WHEN case_current_status IN ('solved','closed') THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as solve_rate_pct
FROM cases_cube
GROUP BY case_type
ORDER BY total_cases DESC
```

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: start;">

<BarChart 
  data={case_types}
  x='case_type'
  y='total_cases'
  title='Volume by Type'
  swapXY={true}
  colorPalette={['#6366f1','#0ea5e9','#22c55e','#f59e0b','#64748b']}
/>

<DataTable 
  data={case_types}
  rows=10
>
  <Column id='case_type' title='Type' />
  <Column id='total_cases' title='Total' fmt='#,##0' />
  <Column id='solved' title='Solved' fmt='#,##0' />
  <Column id='solve_rate_pct' title='Solve Rate' fmt='0.0"%"' />
  <Column id='avg_reply_time' title='Avg Reply (min)' fmt='#,##0.0' />
</DataTable>

</div>

---

<!-- ═══════════════════════════════════════════════════════════════════
     TOPIC DISTRIBUTION
     ═══════════════════════════════════════════════════════════════════ -->

## 💬 Topic Distribution

```sql topics
SELECT 
  COALESCE(case_topic, 'No Topic') as topic,
  COUNT(*) as case_count,
  ROUND(AVG(case_reply_time_in_minutes_business), 2) as avg_reply_time,
  ROUND(SUM(CASE WHEN case_satisfaction_rating = 'good' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(SUM(CASE WHEN case_satisfaction_rating IN ('good','bad') THEN 1 ELSE 0 END), 0), 1) as sat_pct
FROM cases_cube
GROUP BY case_topic
ORDER BY case_count DESC
LIMIT 15
```

<BarChart 
  data={topics}
  x='topic'
  y='case_count'
  title='Top 15 Topics by Volume'
  swapXY={true}
  colorPalette={['#a855f7','#8b5cf6','#7c3aed','#6d28d9','#5b21b6']}
/>

<DataTable 
  data={topics}
  rows=15
>
  <Column id='topic' title='Topic' />
  <Column id='case_count' title='Cases' fmt='#,##0' />
  <Column id='avg_reply_time' title='Avg Reply (min)' fmt='#,##0.0' />
  <Column id='sat_pct' title='CSAT %' fmt='0.0"%"' />
</DataTable>

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge Foundry &middot; Case Explorer &middot; Powered by Cube + Evidence
</div>