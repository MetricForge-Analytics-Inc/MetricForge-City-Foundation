-- Cube.js pre-computed KPI measures from the tickets_case_detail presentation cube
SELECT
  MEASURE(case_created_volume)                      AS total_created,
  MEASURE(case_end_user_created_volume)             AS end_user_created,
  MEASURE(case_agent_created_volume)                AS agent_created,
  MEASURE(total_solved_tickets)                     AS total_solved,
  MEASURE(total_agent_replies)                      AS total_replies,
  MEASURE(avg_first_reply_time_business_minutes)    AS avg_first_reply_min,
  MEASURE(avg_first_reply_time_calendar_minutes)    AS avg_first_reply_cal_min,
  MEASURE(case_reassigned_volume)                   AS reassigned,
  MEASURE(case_reopened_volume)                     AS reopened,
  MEASURE(total_incidents)                          AS incidents,
  MEASURE(total_problems)                           AS problems,
  MEASURE(one_touch_tickets)                        AS one_touch,
  MEASURE(two_touch_tickets)                        AS two_touch,
  MEASURE(multi_touch_tickets)                      AS multi_touch,
  MEASURE(good_satisfaction_tickets)                AS good_sat,
  MEASURE(bad_satisfaction_tickets)                 AS bad_sat,
  MEASURE(rated_satisfaction_tickets)               AS rated_sat,
  MEASURE(surveyed_satisfaction_tickets)            AS surveyed_sat,
  MEASURE(total_on_hold_time_business_minutes)      AS total_hold_biz_min,
  MEASURE(satisfaction_score)                       AS satisfaction_score,
  MEASURE(one_touch_pct)                            AS one_touch_pct,
  MEASURE(two_touch_pct)                            AS two_touch_pct,
  MEASURE(multi_touch_pct)                          AS multi_touch_pct
FROM
  tickets_case_detail
