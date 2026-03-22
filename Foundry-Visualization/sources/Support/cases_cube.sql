-- Evidence source query — pulls all dimensions from the
-- tickets_case_detail Cube.js presentation cube.
-- Cube.js exposes this via its Postgres-compatible SQL API.

SELECT
  -- identifiers
  case_id,
  case_organization_id,

  -- numeric dimensions
  case_assigned_group_stations,
  case_assignee_stations,
  case_number_of_reopens,
  case_number_of_replies,
  case_on_hold_minutes_business,
  case_on_hold_minutes_calendar,
  case_reply_time_in_minutes_business,
  case_reply_time_in_minutes_calendar,

  -- categorical dimensions
  case_current_status,
  case_priority,
  case_satisfaction_rating,
  case_type,
  case_topic,
  channel,

  -- text dimensions
  case_subject,
  case_description,
  case_tags,

  -- boolean dimensions
  case_has_incidents,
  case_is_public,

  -- struct / nested dimensions (from joined user tables)
  assignee,
  requester,
  submitter,

  -- lifecycle timestamps (from the full inheritance chain)
  case_created_time,
  case_last_updated_time,
  case_status_last_updated_time,
  case_assignee_last_updated_time,
  case_custom_status_updated_time,
  case_initial_assignment_time,
  case_last_assignment_time,
  case_latest_comment_added_time,
  case_requester_last_updated_time

FROM
  tickets_case_detail