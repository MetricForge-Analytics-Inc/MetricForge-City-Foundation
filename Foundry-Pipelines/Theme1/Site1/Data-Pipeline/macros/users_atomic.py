from sqlmesh import macro

@macro()
def users_atomic_query(evaluator, table_type):

    query_suffix = """"""

    if table_type == "table":
        query_suffix = """
    where
        users.created_at between @start_date and @end_date
        """

    elif table_type == "view":
        query_suffix = """"""


    users_atomic_query = \
    f"""--sql
    select
        users.id as user_id,
        users.url,
        users.name as user_full_name,
        users.email as user_email,
        users.created_at as user_created_time,
        users.updated_at as user_last_updated_time,
        users.time_zone as user_time_zone,
        users.locale as user_locale,
        users.organization_id as user_organization_id,
        users.role as user_role,
        users.verified as user_is_verified,
        users.active as user_is_active,
        users.notes as user_notes,
        users.alias as user_alias,
        users.shared,
        users.shared_agent,
        users.last_login_at as user_last_login_time,
        users.role_type as user_role_type,
        users.moderator as user_moderator,
        users.only_private_comments,
        users.restricted_agent as user_restricted_agent,
        users.suspended as user_is_suspended,
        users.default_group_id as user_default_group_id,
        users.report_csv,
        users._dlt_load_id,
        users._dlt_id,
        users.photo__content_url,
        users.photo__content_type,
        users.photo__deleted,
        users.ticket_restriction
    from Foundry.normalized_zendesk_extract.users as users
    {query_suffix}
    """

    return users_atomic_query

@macro()
def users_atomic_grain(evaluator):
    grain = "'grain (user_id, user_created_time)'"
    return grain

