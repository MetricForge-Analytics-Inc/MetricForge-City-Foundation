-- Measures broken down by channel from Cube.js
SELECT
  channel,
  MEASURE(case_created_volume)                      AS total,
  MEASURE(total_solved_tickets)                     AS solved,
  MEASURE(avg_first_reply_time_business_minutes)    AS avg_reply_min,
  MEASURE(satisfaction_score)                       AS sat_score,
  MEASURE(one_touch_pct)                            AS one_touch_pct,
  MEASURE(case_reopened_volume)                     AS reopened
FROM
  tickets_case_detail
WHERE channel IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
