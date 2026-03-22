from sqlmesh import macro

@macro()
def tickets_details_query(evaluator, table_type):

    query_suffix = """"""

    if table_type == "table":
        query_suffix = """
    where
        tickets.case_created_time between @start_date and @end_date
        """

    elif table_type == "view":
        query_suffix = """"""




    tickets_details_query = \
    f"""--sql
    select
        tickets.case_id,
        tickets.channel,
        tickets.case_created_time,
        tickets.case_last_updated_time,
        tickets.case_type,
        tickets.case_topic,
        tickets.case_subject,
        tickets.case_description,
        tickets.case_priority,
        tickets.case_current_status,
        tickets.case_has_incidents,
        tickets.case_is_public,
        tickets.case_satisfaction_rating,
        tickets.case_tags,
        tickets.case_organization_id,
        tickets.case_assigned_group_stations,
        tickets.case_assignee_stations,
        tickets.case_number_of_reopens,
        tickets.case_number_of_replies,
        tickets.case_requester_last_updated_time,
        tickets.case_status_last_updated_time,
        tickets.case_latest_comment_added_time,
        tickets.case_on_hold_minutes_calendar,
        tickets.case_on_hold_minutes_business,
        tickets.case_custom_status_updated_time,
        tickets.case_assignee_last_updated_time,
        tickets.case_initial_assignment_time,
        tickets.case_last_assignment_time,
        tickets.case_reply_time_in_minutes_calendar,
        tickets.case_reply_time_in_minutes_business,
        tickets.requester,
        tickets.submitter,
        tickets.assignee
    from
        Foundry.support.tickets_integration_{table_type} as tickets
    {query_suffix}
    """

    return tickets_details_query

@macro()
def tickets_details_grain(evaluator):
    grain = "'grain (case_id, case_created_time)'"
    return grain

