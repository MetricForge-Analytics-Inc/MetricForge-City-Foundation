---
title: Data Governance
---

<!-- ═══════════════════════════════════════════════════════════════════
     HERO
     ═══════════════════════════════════════════════════════════════════ -->

<div style="background: linear-gradient(135deg, #713f12 0%, #ca8a04 45%, #fde047 100%); border-radius: 1.25rem; padding: 2rem 2.5rem 1.5rem; margin-bottom: 2rem; color: #fff; position: relative; overflow: hidden;">
  <div style="position: absolute; top: -20px; left: 60%; width: 160px; height: 160px; background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%); border-radius: 50%;"></div>
  <a href="/" style="color: #fef9c3; text-decoration: none; font-size: 0.85rem;">&larr; Back to Dashboard</a>
  <h1 style="margin: 0.5rem 0 0.3rem; font-size: 2rem; font-weight: 800;">📊 Data Governance</h1>
  <p style="margin: 0; color: #fef3c7; font-size: 1rem;">Data catalog, quality metrics, departmental ownership, and the governance framework that makes cross-departmental integration trustworthy.</p>
</div>

---

## Data Catalog

_The foundation of municipal data infrastructure: knowing what data exists, who owns it, and how it connects._

| Dataset | Department | Source | Update Frequency | PII Risk | Quality |
|---|---|---|---|---|---|
| Road Segments | Engineering | ArcGIS Open Data | Weekly | None | ✅ High |
| Bridges | Engineering | ArcGIS Open Data | Monthly | None | ✅ High |
| Water Distribution Mains | Utilities | ArcGIS Open Data | Weekly | None | ✅ High |
| Sanitary Sewers | Utilities | ArcGIS Open Data | Weekly | None | ✅ High |
| Storm Sewers | Utilities | ArcGIS Open Data | Weekly | None | ✅ High |
| Building Permits | Planning | ArcGIS Open Data | Daily | ⚠️ Low (address) | ✅ High |
| Zoning | Planning | ArcGIS Open Data | Monthly | None | ✅ High |
| Official Plan Land Use | Planning | ArcGIS Open Data | Annually | None | ✅ High |
| Ward Boundaries | Governance | ArcGIS Open Data | Per election cycle | None | ✅ High |
| Neighbourhood Boundaries | Planning | ArcGIS Open Data | As needed | None | ✅ High |
| Parks | Parks & Rec | ArcGIS Open Data | Monthly | None | ✅ High |
| Tree Inventory | Parks & Rec | ArcGIS Open Data | Annually | None | ✅ High |
| Transit Routes | Transit (GRT) | ArcGIS Open Data | Per schedule change | None | ✅ High |
| Transit Stops | Transit (GRT) | ArcGIS Open Data | Per schedule change | None | ✅ High |
| Property Boundaries | Planning | ArcGIS Open Data | Monthly | ⚠️ Low (address) | ✅ High |

---

## Data Governance Framework

### Ownership & Stewardship

| Role | Responsibility |
|---|---|
| **Data Owner** (Department Head) | Accountable for data accuracy, access policies, and retention |
| **Data Steward** (Domain Expert) | Daily quality management, metadata maintenance, issue resolution |
| **Data Custodian** (IT/Platform) | Technical infrastructure, backup, security, access provisioning |
| **Data Consumer** (Analyst/Planner) | Responsible use, reporting issues, respecting access controls |

### Access Control Architecture

This platform implements **Role-Based Access Control (RBAC)** with three tiers:

| Level | Access | Example Roles |
|---|---|---|
| **Public** | Open data, aggregated metrics, dashboard views | Citizens, researchers, media |
| **Internal** | Department data + cross-dept aggregates | City staff, analysts, planners |
| **Restricted** | PII, individual records, sensitive data | Department heads, legal, auditors |

### Privacy-by-Design Principles

1. **Aggregation by default** — Individual records are aggregated to ward/neighbourhood level before cross-department sharing
2. **Minimum necessary access** — Users receive only the access required for their role
3. **Audit logging** — All data access is logged with user, timestamp, and query
4. **PII flagging** — Datasets containing personal information are tagged and subject to additional controls
5. **Anonymization pipeline** — Addresses and individual identifiers are hashed or removed before analytical use

---

## Data Quality Rules

| Rule | Scope | Implementation |
|---|---|---|
| No null primary keys | All atomic models | SQLMesh audit (`assert_no_null_*_ids.sql`) |
| Valid ward references | Permits, roads, water | Foreign key check against `boundaries_atomic` |
| Reasonable value ranges | Permits (est. value > 0) | SQLMesh audit |
| Temporal consistency | All incremental models | `INCREMENTAL_BY_TIME_RANGE` ensures no gaps |
| Schema drift detection | DLT extraction | DLT built-in schema evolution tracking |

---

## Integration Standards

### Common Integration Keys

| Key | Type | Departments Connected |
|---|---|---|
| **Ward** | Geographic | Engineering, Planning, Utilities, Transit, Parks |
| **Neighbourhood** | Geographic | Planning, Social Services, Public Health |
| **Address / Location** | Spatial | All departments (with privacy controls) |
| **Permit Number** | Business | Planning, Engineering, Utilities |

### Interoperability Pattern

```
Department A (source system)
    │
    ├─► DLT Extract → normalized_opendata_extract (landing)
    │
    ├─► SQLMesh atomic model → city.{entity}_atomic (standardized)
    │
    ├─► SQLMesh integration model → Cross-dept JOINs on ward/address
    │
    ├─► Cube semantic layer → Time-attributed measures & dimensions
    │
    └─► Evidence dashboard → Federated view across departments
```

<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 3rem;">
  MetricForge City Foundation &middot; Data Governance &middot; Powered by Cube + Evidence
</div>
