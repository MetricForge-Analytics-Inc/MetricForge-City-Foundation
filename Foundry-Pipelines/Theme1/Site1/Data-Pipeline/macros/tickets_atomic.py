from sqlmesh import macro

@macro()
def tickets_atomic_query(evaluator, table_type):

    query_suffix = """"""

    if table_type == "table":
        query_suffix = """
    where
        tickets.created_at between @start_date and @end_date
        """

    elif table_type == "view":
        query_suffix = """"""


    tickets_atomic_query = \
    f"""--sql
    select
        tickets.id as case_id,
        tickets.via__channel as channel,
        tickets.created_at as case_created_time,
        tickets.updated_at as case_last_updated_time,
        tickets.type as case_type,
        tickets.topic as case_topic,
        tickets.subject as case_subject,
        tickets.description as case_description,
        tickets.priority as case_priority,
        tickets.status as case_current_status,
        tickets.requester_id as case_requester_id,
        tickets.submitter_id as case_submitter_id,
        tickets.assignee_id as case_last_assignee_id,
        tickets.group_id as case_assigned_group_id,
        tickets.has_incidents as case_has_incidents,
        tickets.is_public as case_is_public,
        tickets.satisfaction_rating__score as case_satisfaction_rating,
        tickets.tags as case_tags,
        tickets.organization_id as case_organization_id,
        ticket_metrics.group_stations as case_assigned_group_stations,
        ticket_metrics.assignee_stations as case_assignee_stations,
        ticket_metrics.reopens as case_number_of_reopens,
        ticket_metrics.replies as case_number_of_replies,
        ticket_metrics.requester_updated_at as case_requester_last_updated_time,
        ticket_metrics.status_updated_at as case_status_last_updated_time,
        ticket_metrics.latest_comment_added_at as case_latest_comment_added_time,
        ticket_metrics.on_hold_time_in_minutes__calendar as case_on_hold_minutes_calendar,
        ticket_metrics.on_hold_time_in_minutes__business as case_on_hold_minutes_business,
        ticket_metrics.custom_status_updated_at as case_custom_status_updated_time,
        ticket_metrics.assignee_updated_at as case_assignee_last_updated_time,
        ticket_metrics.initially_assigned_at as case_initial_assignment_time,
        ticket_metrics.assigned_at as case_last_assignment_time,
        ticket_metrics.reply_time_in_minutes__calendar as case_reply_time_in_minutes_calendar,
        ticket_metrics.reply_time_in_minutes__business as case_reply_time_in_minutes_business
    from 
        Foundry.normalized_zendesk_extract.tickets as tickets
    left join
        Foundry.normalized_zendesk_extract.ticket_metrics as ticket_metrics
    on
        tickets.id = ticket_metrics.ticket_id
    {query_suffix}
    """

    return tickets_atomic_query

@macro()
def tickets_atomic_grain(evaluator):
    grain = "'grain (case_id, case_created_time)'"
    return grain


