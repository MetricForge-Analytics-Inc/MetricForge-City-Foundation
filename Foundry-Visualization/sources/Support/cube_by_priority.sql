-- Measures broken down by priority from Cube.js
SELECT
  case_priority                                     AS priority,
  MEASURE(case_created_volume)                      AS total,
  MEASURE(total_solved_tickets)                     AS solved,
  MEASURE(case_reopened_volume)                     AS reopened,
  MEASURE(avg_first_reply_time_business_minutes)    AS avg_reply_min,
  MEASURE(satisfaction_score)                       AS sat_score,
  MEASURE(one_touch_pct)                            AS one_touch_pct
FROM
  tickets_case_detail
GROUP BY 1
ORDER BY
  CASE case_priority
    WHEN 'urgent' THEN 1
    WHEN 'high'   THEN 2
    WHEN 'normal' THEN 3
    WHEN 'low'    THEN 4
    ELSE 5
  END
