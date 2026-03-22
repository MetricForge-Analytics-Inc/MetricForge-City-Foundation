-- Daily volume & satisfaction trend from Cube.js
SELECT
  case_created_time                                 AS date,
  MEASURE(case_created_volume)                      AS created,
  MEASURE(total_solved_tickets)                     AS solved,
  MEASURE(case_reopened_volume)                     AS reopened,
  MEASURE(good_satisfaction_tickets)                AS good_sat,
  MEASURE(bad_satisfaction_tickets)                 AS bad_sat,
  MEASURE(avg_first_reply_time_business_minutes)    AS avg_reply_min,
  MEASURE(one_touch_tickets)                        AS one_touch,
  MEASURE(case_reassigned_volume)                   AS reassigned
FROM
  tickets_case_detail
GROUP BY 1
ORDER BY 1
