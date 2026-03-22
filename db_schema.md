# Municipal Data Infrastructure — Core Schema

## Overview

Three universal tables underpin the entire federated data model. Every department maps their existing data onto these abstractions — no system replacement required.

---

## 1. `assets`
**Purpose:** One row per physical or logical asset in the municipality. This is the single source of truth for *what exists*.

| Column | Type | Description |
|---|---|---|
| `asset_id` | `UUID` | Globally unique identifier (primary key) |
| `asset_type` | `VARCHAR` | Enum: `parcel`, `building`, `road`, `pipe`, `zone`, `permit`, `person`, `organization` |
| `department_owner` | `VARCHAR` | Originating department: `engineering`, `planning`, `public_health`, `transit`, etc. |
| `source_system_id` | `VARCHAR` | The ID from the originating system (e.g. GIS parcel ID, permit number) |
| `source_system` | `VARCHAR` | Name of the originating system (e.g. `kitchener_gis`, `amanda_permits`) |
| `label` | `VARCHAR` | Human-readable name or address |
| `geom` | `GEOMETRY` | Spatial representation (point, polygon, linestring) — PostGIS / WKT |
| `latitude` | `FLOAT` | Centroid latitude (denormalized for convenience) |
| `longitude` | `FLOAT` | Centroid longitude (denormalized for convenience) |
| `status` | `VARCHAR` | Current lifecycle status: `active`, `inactive`, `pending`, `demolished` |
| `privacy_class` | `VARCHAR` | `public`, `internal`, `confidential`, `pii` |
| `created_at` | `TIMESTAMP` | Record creation time (UTC) |
| `updated_at` | `TIMESTAMP` | Last modification time (UTC) |
| `valid_from` | `DATE` | Start of real-world validity |
| `valid_to` | `DATE` | End of real-world validity (NULL = currently active) |

**Notes:**
- `source_system_id` + `source_system` together form a natural deduplication key across departments.
- `privacy_class` drives row-level access control — `pii` rows are never exposed via shared APIs without anonymization.
- `geom` is the **primary cross-departmental join key** — spatial intersection replaces fragile ID matching.

---

## 2. `events`
**Purpose:** Immutable log of everything that happens to an asset. Supports both change tracking and cross-departmental notification.

| Column | Type | Description |
|---|---|---|
| `event_id` | `UUID` | Globally unique identifier (primary key) |
| `asset_id` | `UUID` | Foreign key → `assets.asset_id` |
| `event_type` | `VARCHAR` | Enum: `created`, `updated`, `status_changed`, `inspection`, `permit_issued`, `permit_closed`, `flag_raised`, `data_accessed` |
| `event_subtype` | `VARCHAR` | Department-specific detail (e.g. `foundation_inspection`, `infill_permit`, `water_capacity_flag`) |
| `department_source` | `VARCHAR` | Department that generated the event |
| `triggered_by` | `VARCHAR` | System or user that caused the event |
| `payload` | `JSONB` | Flexible field for event-specific data (old/new values, measurements, notes) |
| `severity` | `VARCHAR` | `info`, `warning`, `critical` — used for cross-dept alerting |
| `occurred_at` | `TIMESTAMP` | When the real-world event happened (UTC) |
| `recorded_at` | `TIMESTAMP` | When it was written to the database (UTC) |
| `is_audit_event` | `BOOLEAN` | TRUE for data access/export events (compliance) |

**Notes:**
- This table is **append-only**. No updates, no deletes. This is the audit trail.
- `payload` as JSONB allows each department to attach their own fields without schema changes.
- `is_audit_event = TRUE` rows capture who accessed what data and when — satisfies privacy compliance requirements.

**Example rows:**

```json
// Planning issues an infill permit
{
  "event_type": "permit_issued",
  "event_subtype": "infill_permit",
  "department_source": "planning",
  "payload": {
    "permit_number": "B24-01234",
    "permit_type": "infill",
    "units": 4,
    "zoning": "R4"
  },
  "severity": "info"
}

// Engineering raises a water capacity flag
{
  "event_type": "flag_raised",
  "event_subtype": "water_capacity_flag",
  "department_source": "engineering",
  "payload": {
    "capacity_zone": "WZ-07",
    "current_utilization_pct": 94,
    "threshold_pct": 90
  },
  "severity": "critical"
}
```

---

## 3. `accounts`
**Purpose:** Represents any actor — a person, organization, or system — that owns, interacts with, or is associated with an asset.

| Column | Type | Description |
|---|---|---|
| `account_id` | `UUID` | Globally unique identifier (primary key) |
| `account_type` | `VARCHAR` | Enum: `resident`, `property_owner`, `developer`, `contractor`, `department`, `external_agency`, `system` |
| `display_name` | `VARCHAR` | Non-PII label (e.g. "Owner-123", "Dept of Engineering") |
| `department` | `VARCHAR` | Owning department if `account_type = department` |
| `privacy_class` | `VARCHAR` | `public`, `internal`, `confidential`, `pii` |
| `pii_vault_ref` | `UUID` | Reference to encrypted PII store (actual name/contact never stored here) |
| `created_at` | `TIMESTAMP` | Record creation time (UTC) |
| `is_active` | `BOOLEAN` | Whether the account is currently active |

**Notes:**
- **No PII is stored directly.** Sensitive identity data lives in a separate encrypted vault; this table stores only a reference UUID.
- `display_name` is always anonymized for `privacy_class = pii` rows (e.g. hashed or replaced with a role label).
- Cross-departmental queries join on `account_id`, never on name or contact info.

---

## 4. `asset_accounts` (Junction Table)
**Purpose:** Links assets to accounts with a typed relationship.

| Column | Type | Description |
|---|---|---|
| `asset_id` | `UUID` | FK → `assets` |
| `account_id` | `UUID` | FK → `accounts` |
| `relationship_type` | `VARCHAR` | Enum: `owner`, `applicant`, `inspector`, `responsible_dept`, `tenant` |
| `valid_from` | `DATE` | Start of relationship |
| `valid_to` | `DATE` | End of relationship (NULL = current) |

---

## Integration Key: Geography

Because most municipal data is spatial, **geometry intersection is the primary cross-departmental join** — not fragile shared IDs.

```sql
-- Example: Find all infill permits inside a water capacity warning zone
SELECT
    a.asset_id,
    a.label AS permit_address,
    e.payload->>'permit_type' AS permit_type,
    wz.label AS capacity_zone,
    wz_event.payload->>'current_utilization_pct' AS utilization
FROM assets a
JOIN events e ON a.asset_id = e.asset_id
    AND e.event_type = 'permit_issued'
    AND e.occurred_at >= '2024-01-01'
JOIN assets wz ON ST_Within(a.geom, wz.geom)
    AND wz.asset_type = 'zone'
JOIN events wz_event ON wz.asset_id = wz_event.asset_id
    AND wz_event.event_subtype = 'water_capacity_flag'
WHERE a.privacy_class IN ('public', 'internal');
```

---

## Privacy Access Tiers

| Tier | Who | What they see |
|---|---|---|
| `public` | Anyone / citizen portal | Aggregated, anonymized, no addresses |
| `internal` | Any municipal staff | Asset-level data, no PII |
| `departmental` | Specific department only | Full departmental records |
| `confidential` | Director+ approval | Cross-dept PII-adjacent data |
| `pii_vault` | Authorized + audited | Raw identity data via vault only |

Every query against `assets`, `events`, or `accounts` is **row-filtered by privacy tier at the database level** — not enforced in application code.

---

## Mapping Kitchener Data Sources to This Schema

| Source Dataset | Maps To | `asset_type` | `privacy_class` |
|---|---|---|---|
| Building Permits (ArcGIS) | `assets` + `events` | `permit` | `internal` |
| Parcel Fabric (GIS) | `assets` | `parcel` | `public` |
| Water Capacity Zones | `assets` | `zone` | `public` |
| Zoning Layers | `assets` | `zone` | `public` |
| Property Owners | `accounts` (PII vault) | — | `pii` |
| Infrastructure Assets | `assets` | `pipe`, `road` | `internal` |
