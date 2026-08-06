# Feature Store Schema Design

**Version:** 1.0.0  
**Aligned with PRD:** Yes  

---

### 1. Architecture Overview

Dual-store architecture:

- **Online Store**: Redis Cluster / DynamoDB / Cassandra (low-latency key-value)
- **Offline Store**: Delta Lake / Apache Iceberg on object storage (S3 / GCS / ADLS)
- **Feature Registry**: Central metadata service (PostgreSQL + API)

### 2. Core Entities

#### 2.1 Entity

```yaml
Entity:
  name: string                    # e.g. "user", "transaction"
  join_keys: list[string]         # primary keys for joining
  description: string
  tags: map[string, string]
```

#### 2.2 Feature View

```yaml
FeatureView:
  name: string
  entities: list[Entity]
  features: list[Feature]
  ttl: duration                   # online retention
  online: boolean
  offline: boolean
  batch_source: Source            # for materialization
  stream_source: Source           # for real-time updates
  description: string
  owner: string
  created_at: timestamp
  version: int
```

#### 2.3 Feature

```yaml
Feature:
  name: string
  dtype: enum[int64, float64, string, bool, bytes, array, map]
  description: string
  tags: map[string, string]
  # Optional statistics for monitoring baselines
  baseline_stats:
    mean: float
    std: float
    quantiles: map[string, float]
    unique_count: int             # for categoricals
```

### 3. Example Feature Views

#### User Profile Features (entity: user)

| Feature Name          | Type     | Description                        | Source          |
|-----------------------|----------|------------------------------------|-----------------|
| user_age_days         | int64    | Days since account creation        | batch           |
| lifetime_txn_count    | int64    | Total transactions ever            | stream + batch  |
| avg_txn_amount_7d     | float64  | Rolling 7-day average amount       | stream          |
| preferred_device      | string   | Most frequent device type (30d)    | stream          |
| risk_score_v2         | float64  | Latest risk model score            | stream          |

#### Transaction Context Features (entity: transaction)

| Feature Name          | Type     | Description                        |
|-----------------------|----------|------------------------------------|
| amount                | float64  | Transaction amount                 |
| merchant_category     | string   | MCC code                           |
| is_international      | bool     | Cross-border flag                  |
| hour_of_day           | int64    | Local hour                         |
| distance_from_home_km | float64  | Geo distance                       |

### 4. Storage Schemas

#### Online Store Key Design

```
{entity_name}:{join_key_value}:{feature_view_name}
```

Value: MessagePack / Protobuf serialized feature vector with timestamp.

#### Offline Store Table Layout (Delta / Iceberg)

```sql
CREATE TABLE feature_store.user_features (
  user_id           STRING,
  event_timestamp   TIMESTAMP,
  created_timestamp TIMESTAMP,
  user_age_days     BIGINT,
  lifetime_txn_count BIGINT,
  avg_txn_amount_7d DOUBLE,
  preferred_device   STRING,
  risk_score_v2     DOUBLE
)
USING DELTA
PARTITIONED BY (date(event_timestamp));
```

### 5. Materialization & Freshness

- Stream processors (Flink / Spark Structured Streaming / Kafka Streams) continuously update online store and write to offline append-only logs.
- Batch materialization jobs (daily / hourly) ensure offline completeness and backfill.
- Feature freshness SLOs defined per view (e.g. risk_score_v2 must be < 5 min old).

### 6. Point-in-Time Correctness

All training dataset generation uses point-in-time correct joins to guarantee no future leakage.

### 7. Versioning Strategy

- Feature views are immutable once registered at a major version.
- Minor updates (description, tags) allowed.
- Breaking changes require new major version + migration plan.
- Consumers pin to specific versions in training and serving configs.

### 8. Access Control

- Feature-level RBAC via registry.
- Online store supports request-level authentication tokens.
- Audit log of all feature reads for compliance.

---

*Schema is intentionally vendor-agnostic. Concrete implementations (Feast, Tecton, custom) must map to these concepts.*
