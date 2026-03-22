from sqlmesh import macro

@macro()
def tickets_integration_query(evaluator, table_type):

    query_suffix = """"""

    if table_type == "table":
        query_suffix = """
    where
        tickets.case_created_time between @start_date and @end_date
        """

    elif table_type == "view":
        query_suffix = """"""




    tickets_integration_query = \
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
    -- Related Requester User Information: 
    struct(
        requesting_users.user_id as requester_id,
        requesting_users.user_full_name as requester_full_name,
        requesting_users.user_email as requester_email,
        requesting_users.user_time_zone as requester_time_zone,
        requesting_users.user_locale as requester_locale,
        requesting_users.user_organization_id as requester_organization_id,
        requesting_users.user_role as requester_role,
        requesting_users.user_is_verified as requester_is_verified,
        requesting_users.user_is_active as requester_is_active,
        requesting_users.user_last_login_time as requester_last_login_time
    ) as requester,
    -- Related Submitter User Information
    struct(
        submitting_users.user_id as submitter_user_id,
        submitting_users.user_full_name as submitter_full_name,
        submitting_users.user_email as submitter_email,
        submitting_users.user_time_zone as submitter_time_zone,
        submitting_users.user_locale as submitter_locale,
        submitting_users.user_organization_id as submitter_organization_id,
        submitting_users.user_role as submitter_role,
        submitting_users.user_is_verified as submitter_is_verified,
        submitting_users.user_is_active as submitter_is_active,
        submitting_users.user_last_login_time as submitter_last_login_time
    ) as submitter,
    -- Related Assignee User Information
    struct(
        assigned_users.user_id as assignee_id,
        assigned_users.user_full_name as assignee_full_name,
        assigned_users.user_email as assignee_email,
        assigned_users.user_time_zone as assignee_time_zone,
        assigned_users.user_locale as assignee_locale,
        assigned_users.user_organization_id as assignee_organization_id,
        assigned_users.user_role as assignee_role,
        assigned_users.user_is_verified as assignee_is_verified,
        assigned_users.user_is_active as assignee_is_active,
        assigned_users.user_last_login_time as assignee_last_login_time
    ) as assignee
    from
        Foundry.support.tickets_atomic_{table_type} as tickets
    left join
        Foundry.support.users_atomic_{table_type} as requesting_users
    on
        tickets.case_requester_id = requesting_users.user_id
    left join
        Foundry.support.users_atomic_{table_type} as submitting_users
    on
        tickets.case_submitter_id = submitting_users.user_id
    left join
        Foundry.support.users_atomic_{table_type} as assigned_users
    on
        tickets.case_last_assignee_id = assigned_users.user_id
    {query_suffix}
    """

    return tickets_integration_query

@macro()
def tickets_integration_grain(evaluator):
    grain = "'grain (case_id, case_created_time)'"
    return grain

