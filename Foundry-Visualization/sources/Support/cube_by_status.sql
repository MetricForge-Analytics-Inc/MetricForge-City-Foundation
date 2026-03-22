-- Measures broken down by current status from Cube.js
SELECT
  case_current_status                               AS status,
  MEASURE(case_created_volume)                      AS total,
  MEASURE(avg_first_reply_time_business_minutes)    AS avg_reply_min,
  MEASURE(total_agent_replies)                      AS total_replies,
  MEASURE(satisfaction_score)                       AS sat_score,
  MEASURE(case_reopened_volume)                     AS reopened
FROM
  tickets_case_detail
WHERE case_current_status IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
