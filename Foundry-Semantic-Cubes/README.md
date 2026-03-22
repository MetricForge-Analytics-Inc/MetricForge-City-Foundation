# Foundry Semantic Cubes

## Overview

Semantic cubes define the **measures** (metrics) and **dimensions** (attributes) that sit between raw data and the visualization layer. Each cube YAML file in `Support/` maps to a Cube.js cube definition that queries the `support.tickets_integration_view`.

The central design principle is **time attribution**: every measure is placed in a cube whose primary datetime dimension represents _when_ that measure's event occurred. This determines how date filters behave in the BI layer.

---

## Why Time Attribution Matters in Cube.js

In Cube.js, when a user applies a date filter (e.g. "last 30 days"), that filter is applied to the cube's **time dimension**. If a measure lives in a cube whose time dimension is `case_created_time`, then filtering by "last 30 days" returns tickets _created_ in the last 30 days. If that same measure lived in a cube whose time dimension is `case_closed_time`, the filter would return tickets _closed_ in the last 30 days instead.

This has real analytical consequences:

| Question | Correct cube | Why |
|---|---|---|
| "How many tickets were created last week?" | `case_created_time` | You want tickets whose **creation** falls in the range |
| "How many tickets were solved last month?" | `case_closed_time` | You want tickets whose **resolution** falls in the range |
| "How many tickets were reopened this quarter?" | `case_reopened_time` | You want tickets whose **reopen event** falls in the range |
| "What was the average first reply time last week?" | `case_response_date` | You want tickets whose **first agent response** falls in the range |

Placing a measure in the wrong cube means date filters silently return wrong results — the numbers look plausible but answer a different question.

### How `extends` Affects Filtering

Each child cube inherits all dimensions and measures from its parent. The cube you choose to query determines which time dimension is the _default_ for date filters.

Each child cube inherits all dimensions and measures from its parent. When you query `tickets_case_closed_time`, you get all measures from every cube in the chain — created volume, reply times, reassignment, incidents, reopens, AND solved/touch metrics — plus the ability to filter by any time dimension in the chain.

### Pre-aggregations

When defining pre-aggregations for performance, the time dimension used in the pre-aggregation must match the cube's primary time attribution. A pre-aggregation on `tickets_case_closed_time` should partition by `case_closed_time`, not `case_created_time`, or cache hits will not align with query patterns.

### Cumulative (Snapshot) Measures vs. Event Measures

Some measures are **event metrics** — they count something that happened on a specific date. "Tickets created on March 15" is an event: the ticket was born that day. A plain `count` or `sum` with a date filter works correctly.

Other measures are **cumulative / snapshot metrics** — they describe the current state of the world as of a point in time. "Unsolved tickets on March 15" means all tickets created **on or before** March 15 that are _still_ unsolved. If you use a plain `sum` with a date filter, you only get tickets created _on_ March 15 that are unsolved — missing every older ticket.

**Solution: `rolling_window` with `trailing: unbounded`**

Cube.js supports [`rolling_window`](https://cube.dev/docs/reference/data-model/measures#rolling_window) on measures. Setting `trailing: unbounded` tells Cube.js to aggregate all rows from the beginning of time up through the selected date:

```yaml
- name: case_unsolved_volume
  sql: is_unsolved
  type: sum
  rolling_window:
    trailing: unbounded
```

With this configuration:
- **"Unsolved volume on March 15"** → `SUM(is_unsolved)` for all tickets where `case_created_time <= March 15`
- **"Unsolved volume this week"** → `SUM(is_unsolved)` accumulated through each day of the week

Measures that use this pattern:
- `case_unsolved_volume` — running total of tickets still unsolved
- `total_unreplied_tickets` — running total of tickets with no agent reply
- `new_tickets` — running total of tickets in New status
- `open_tickets` — running total of tickets in Open status
- `pending_tickets` — running total of tickets in Pending status
- `on_hold_tickets` — running total of tickets in On-hold status
- `unassigned_unsolved_tickets` — running total of unassigned open tickets
- `assigned_unsolved_tickets` — running total of assigned open tickets
- `unreplied_unsolved_tickets` — running total of open tickets without a reply

> **Important caveat:** These measures reflect the ticket's _current_ state, not its historical state. `is_unsolved = 1` means the ticket is unsolved _right now_, not that it was unsolved on the filtered date. For true point-in-time historical snapshots, you would need daily snapshot tables. The rolling window gives the correct _filter semantics_ (include all tickets up to the date) while the flag reflects current reality.

---

## Cube Inheritance Structure

The cubes use `extends` to form a sequential inheritance chain. Each child inherits all dimensions and measures from its parent, then adds its own time-attributed datetime dimension and measures.

```
1_tickets_case_created_time           (base — all shared dimensions, creation + backlog + satisfaction measures)
└── 2_tickets_case_response_time      (extends 1 — reply/response measures)
    └── 3_tickets_case_reassigned_time    (extends 2 — reassignment measures)
        └── 4_tickets_case_incident_time      (extends 3 — incident/problem measures)
            └── 5_tickets_case_reopened_time  (extends 4 — reopen measures)
                └── 6_tickets_case_closed_time (extends 5 — solved/touch measures)
```

The numbering prefix (`1_`–`6_`) indicates the position in the chain. The most derived cube (`tickets_case_closed_time`) has access to every measure defined across the entire lifecycle.

---

## Cube Definitions

### 1. `tickets_case_created_time` — Base Cube

**DATETIME:** `case_created_time` (ticket creation timestamp)

**Why these measures belong here:** Measures in this cube either answer a question about the moment a ticket was born (event metrics) or describe the cumulative backlog as of a creation date (snapshot metrics with `rolling_window`).

#### Event measures

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `case_created_volume` | count | Total ticket count | A ticket is created once — count it when it's created |
| `case_end_user_created_volume` | sum | Tickets submitted by end-users | The submission event happens at creation time |
| `case_agent_created_volume` | sum | Tickets submitted by agents | Same — agent-created tickets are counted at creation |
| `good_satisfaction_tickets` | sum | Tickets rated "good" | Satisfaction is a property of the ticket, attributed to when it entered the system |
| `bad_satisfaction_tickets` | sum | Tickets rated "bad" | Same as above |
| `rated_satisfaction_tickets` | sum | Tickets with any rating | Same as above |
| `surveyed_satisfaction_tickets` | sum | Tickets that received a survey | Same as above |
| `unsurveyed_satisfaction_tickets` | sum | Tickets not surveyed | Same as above |
| `total_on_hold_time_calendar_minutes` | sum | Total on-hold time (calendar) | Cumulative metric on the ticket, attributed to creation |
| `total_on_hold_time_business_minutes` | sum | Total on-hold time (business hours) | Same as above |

#### Cumulative backlog measures (`rolling_window: trailing: unbounded`)

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `case_unsolved_volume` | sum | Running total of unsolved tickets | "Unsolved on Date X" = all tickets created up to X still unsolved |
| `total_unreplied_tickets` | sum | Running total of unreplied tickets | "Unreplied on Date X" = all tickets created up to X with no reply |
| `new_tickets` | sum | Running total of tickets in New status | Backlog measure — status breakdown up to the filtered date |
| `open_tickets` | sum | Running total of tickets in Open status | Same |
| `pending_tickets` | sum | Running total of tickets in Pending status | Same |
| `on_hold_tickets` | sum | Running total of tickets in On-hold status | Same |
| `unassigned_unsolved_tickets` | sum | Running total of unassigned open tickets | Backlog composition — unassigned work up to the filtered date |
| `assigned_unsolved_tickets` | sum | Running total of assigned open tickets | Same — assigned but not yet resolved |
| `unreplied_unsolved_tickets` | sum | Running total of open tickets without a first reply | Same — untouched work in the backlog |

#### Computed ratio measures

| Measure | Type | Formula | Description |
|---|---|---|---|
| `satisfaction_score` | number | `good / rated` | Percentage of rated tickets that were rated good |
| `satisfaction_rated_pct` | number | `rated / surveyed` | Percentage of surveyed tickets that were actually rated |
| `satisfaction_surveyed_pct` | number | `surveyed / created` | Percentage of all tickets that received a survey |

#### Shared dimensions defined here (inherited by all child cubes)

- **Ticket attributes:** `case_id`, `case_current_status`, `case_priority`, `case_type`, `case_topic`, `case_subject`, `case_description`, `case_tags`, `channel`, `case_has_incidents`, `case_is_public`, `case_satisfaction_rating`, `case_organization_id`
- **Numeric metrics:** `case_assigned_group_stations`, `case_assignee_stations`, `case_number_of_reopens`, `case_number_of_replies`, `case_on_hold_minutes_business`, `case_on_hold_minutes_calendar`, `case_reply_time_in_minutes_business`, `case_reply_time_in_minutes_calendar`
- **Struct dimensions:** `assignee`, `requester`, `submitter` (nested user objects from joined tables)
- **All time dimensions:** `case_created_time`, `case_last_updated_time`, `case_status_last_updated_time`, `case_assignee_last_updated_time`, `case_custom_status_updated_time`, `case_requester_last_updated_time`, `case_initial_assignment_time`, `case_last_assignment_time`, `case_latest_comment_added_time`

---

### 2. `tickets_case_response_time`

**Extends:** `tickets_case_created_time`
**DATETIME:** `case_response_date` → mapped to `case_latest_comment_added_time`

**Why these measures belong here:** These measures quantify agent responsiveness. Filtering by date returns tickets whose _agent response_ falls in the selected range.

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `total_agent_replies` | sum | Sum of reply counts | Replies happen at response time, not creation time |
| `avg_first_reply_time_calendar_minutes` | avg | Average first reply time (calendar) | The reply event is what this measures — attribute to when it happened |
| `avg_first_reply_time_business_minutes` | avg | Average first reply time (business hours) | Same — measures response speed at the time of response |

---

### 3. `tickets_case_reassigned_time`

**Extends:** `tickets_case_response_time`
**DATETIME:** `case_reassigned_time` → mapped to `case_last_assignment_time`

**Why these measures belong here:** Reassignment is an event that happens during a ticket's lifecycle, potentially long after creation. Filtering by date returns tickets whose _reassignment_ falls in the selected range.

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `case_reassigned_volume` | sum | Number of reassigned tickets | The reassignment event has its own timestamp — that's when it matters |

---

### 4. `tickets_case_incident_time`

**Extends:** `tickets_case_reassigned_time`
**DATETIME:** `case_incident_time` → mapped to `case_created_time`

**Why these measures belong here:** Incident and problem classification is determined at ticket creation. Filtering by date returns tickets whose _incident classification_ falls in the selected range.

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `total_incidents` | sum | Tickets classified as incidents | The incident type is set when the ticket is created/classified |
| `total_problems` | sum | Tickets classified as problems | Same — problem type is determined at creation |

> **Note:** `case_incident_time` maps to the same underlying column (`case_created_time`) as the base cube's datetime. This is intentional — it provides a semantically distinct cube for incident-specific queries while sharing the same physical timestamp.

---

### 5. `tickets_case_reopened_time`

**Extends:** `tickets_case_incident_time`
**DATETIME:** `case_reopened_time` → mapped to `case_last_updated_time`

**Why these measures belong here:** Reopening is an event that happens after initial resolution. Filtering by date returns tickets whose _reopen event_ falls in the selected range.

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `case_reopened_volume` | sum | Number of reopened tickets | The reopen event has its own timestamp — "how many tickets were reopened this week?" requires this attribution |

---

### 6. `tickets_case_closed_time`

**Extends:** `tickets_case_reopened_time`
**DATETIME:** `case_closed_time` → mapped to `case_status_last_updated_time`

**Why these measures belong here:** Resolution/closure metrics need to be filtered by _when the ticket was solved_, not when it was created. A ticket created in January but solved in March should appear in March's solved count.

#### Event measures

| Measure | Type | Description | Why this time attribution |
|---|---|---|---|
| `total_solved_tickets` | sum | Tickets that have been solved | "How many tickets were solved last month?" filters by close time |
| `one_touch_tickets` | sum | Solved after 1 agent reply | Touch metrics only apply to solved tickets — attribute to when they were solved |
| `two_touch_tickets` | sum | Solved after 2 agent replies | Same |
| `multi_touch_tickets` | sum | Solved after 2+ agent replies | Same |

#### Computed ratio measures

| Measure | Type | Formula | Description |
|---|---|---|---|
| `one_touch_pct` | number | `one_touch / solved` | Percentage of solved tickets resolved in one reply |
| `two_touch_pct` | number | `two_touch / solved` | Percentage of solved tickets resolved in two replies |
| `multi_touch_pct` | number | `multi_touch / solved` | Percentage of solved tickets resolved in more than two replies |

---

## Not Yet Implemented

The following measures require additional data sources or pipeline changes before they can be added.

### Needs: Ticket Events / Updates Data Source

These measures require per-event granularity from the `ticket_events` table and would get a new cube with an **event timestamp** as the datetime dimension:

- **Update/Comment counts:** Updates, Agent updates, End-user updates, Comments, Public/Internal comments, Agent/End-user comments
- **Event-based lifecycle:** Tickets created/solved/assigned/reopened (from status change events), Assignee/Group reassignments, Resolutions, Reopens, Deletions, Recoveries
- **Satisfaction change events:** Satisfaction updates, Good/Bad initial ratings, Rating changes (bad→good, good→bad)
- **Status time tracking:** Field changes time, New/Open/Pending/On-hold status time, Unassigned time, Previously assigned time

### Needs: Resolution Time Columns

Would go in `tickets_case_closed_time` once the pipeline exposes `first_resolution_time` and `full_resolution_time`:

- First/Full resolution time (min, hrs, days — calendar and business hours)
- First/Last assignment to resolution time

### Needs: Wait Time Columns

Would go in `tickets_case_created_time` once `requester_wait_time` and `agent_wait_time` are added from `ticket_metrics`:

- Requester wait time (min, hrs, days — calendar and business hours)
- Agent wait time (min, hrs, days — calendar and business hours)

### Needs: SLA Policy Data Source

Would require a new `tickets_sla_time` cube:

- SLA tickets, Achieved/Breached/Active SLA tickets and percentages
- SLA policies, Achieved/Breached/Active SLA policies
- SLA targets, metric breach/target/completion times

### Needs: Users Data Source

Would require a separate users cube (not ticket-based):

- User/Agent/End-user/Suspended/Deleted user counts
- Assignee, Requester, Organization counts
- Time since user/assignee login

### Needs: Skills Data Source

Would go in `tickets_case_created_time` once skills columns exist:

- Tickets w/skills, Tickets w/o skills
- Ticket skill fulfillment rate, usage rate

### Undefined

- `inbound_shared_tickets` — needs definition and data source
- `outbound_shared_tickets` — needs definition and data source

---

## A Note on "Tickets Created - Last 7 Days" Style Measures

The Zendesk Explore reference lists measures like "Tickets created - Last 7 days", "Tickets solved - This month", etc. These are **not separate measures**. They are time-range filters applied to existing measures:

- "Tickets created - Last 7 days" = `case_created_volume` with a date filter of last 7 days on `case_created_time`
- "Tickets solved - Last month" = `total_solved_tickets` with a date filter of last month on `case_closed_time`

This is handled at the BI/query layer, not in the cube definitions.
