# Dusseldorf API Observability: Logging

This file documents the logging and auditing built into the Dusseldorf control plane.


### 1. Correlation ID Middleware
- **File**: `dusseldorf/api/src/api/middleware/correlation.py`
- **Activated in**: `dusseldorf/api/src/api/main.py`
- **Purpose**: Every request gets a unique `X-Correlation-ID` (from header or auto-generated UUID)
- **Behavior**: ID is stored in `request.state.correlation_id` and echoed in response headers

**Usage**: All downstream code can now access `request.state.correlation_id` for request tracing.

---

### 2. Structured Logging Helper
- **File**: `dusseldorf/api/src/api/dependencies.py`
- **Function**: `get_log_context(current_user, zone=None, operation=None, **extra_fields)`
- **Purpose**: Build consistent logging context dicts with correlation ID, user, zone, and operation

**Usage Pattern**:
```python
from dependencies import get_log_context

logger.info(
    "operation_name",
    extra=get_log_context(
        current_user,
        zone="example.com",
        operation="create_zone",
        custom_field="value"
    )
)
```

**Output** (JSON when structured logging is configured):
```json
{
  "message": "operation_name",
  "correlation_id": "a1b2c3d4-...",
  "user": "user@example.com",
  "user_id": "oid-from-entra-id",
  "zone": "example.com",
  "operation": "create_zone",
  "custom_field": "value"
}
```

---

### 3. Enhanced `get_current_user` Dependency
- **File**: `dusseldorf/api/src/api/dependencies.py`
- **Changes**:
  - Now accepts `Request` parameter to access `correlation_id` from state
  - Logs auth failures with context (`auth_failed_no_token`, `auth_failed_invalid_scheme`, `auth_failed_invalid_token`)
  - Logs successful auth (`auth_success`)
  - Injects `correlation_id` into the `current_user` dict for downstream use

**Why**: Every controller already gets `current_user` via `Depends(get_current_user)`, so correlation context is automatically available.

---

### 4. Permission Audit Trail
- **File**: `dusseldorf/api/src/api/services/permissions.py`
- **Function**: `has_at_least_permissions_on_zone()`
- **Changes**:
  - Added `correlation_id` parameter (defaults to `"unknown"`)
  - Logs **every** permission check with:
    - Zone, user, required permission level (int + name), actual level, allowed/denied result
  - Logs permission denials as `logger.warning()` with `permission_denied` event

**Log Events**:
```python
# Every check:
logger.info("permission_check", extra={
    "zone": "abc123.example.com",
    "user": "user@example.com",
    "required_level": 0,
    "required_level_name": "READONLY",
    "actual_level": 999,
    "allowed": True,
    "correlation_id": "..."
})

# On denial:
logger.warning("permission_denied", extra={
    "zone": "abc123.example.com",
    "user": "user@example.com",
    "required_level": 10,
    "correlation_id": "..."
})
```

---

### 5. Example Controller Updates
- **File**: `dusseldorf/api/src/api/controllers/zones_controller.py`
- **Demonstrates**:
  - Importing `get_log_context` from dependencies
  - Passing `correlation_id` to `permission_service.has_at_least_permissions_on_zone()`
  - Structured logging for key operations:
    - `list_zones_success` — logs zone count and domain filter
    - `zone_not_found` — logs failed lookups
    - `zone_retrieved` — logs successful reads
    - `domain_access_denied` — logs domain permission failures
    - `zone_created` — logs single zone creation
    - `zones_bulk_created` — logs batch creation

---

## How to Use in Other Controllers

### Step 1: Import
```python
from dependencies import get_current_user, get_db, get_log_context
```

### Step 2: Log Operations
```python
@router.post("/rules")
async def create_rule(
    rule: RuleCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_db),
    permission_service: PermissionService = Depends()
):
    # Check permissions (will auto-log)
    can_write = await permission_service.has_at_least_permissions_on_zone(
        rule.zone,
        current_user["preferred_username"],
        Permission.READWRITE,
        current_user.get("correlation_id", "unknown")
    )
    
    if not can_write:
        raise HTTPException(403, "Unauthorized")
    
    # Create the rule
    result = await db.rules.insert_one(rule.dict())
    
    # Log success
    logger.info(
        "rule_created",
        extra=get_log_context(
            current_user,
            zone=rule.zone,
            operation="create_rule",
            rule_id=str(result.inserted_id),
            protocol=rule.networkprotocol
        )
    )
    
    return {"id": str(result.inserted_id)}
```

### Step 3: Pass correlation_id
Whenever calling `permission_service.has_at_least_permissions_on_zone()`, pass:
```python
current_user.get("correlation_id", "unknown")
```

---

## Viewing Logs

### Local Development (console)
Logs currently go to stdout/stderr. You'll see:
```
INFO:zones_controller:zone_created
INFO:permissions:permission_check
WARNING:permissions:permission_denied
```

### With Azure Monitor (Application Insights)
If `APPLICATIONINSIGHTS_CONNECTION_STRING` is set, logs are auto-shipped. Query in Azure Portal:
```kusto
traces
| where customDimensions.correlation_id == "a1b2c3d4-..."
| project timestamp, message, customDimensions
| order by timestamp asc
```

This gives you **end-to-end request tracing** across all services.

---

## Next Steps (Not Yet Implemented)

### 3. Database Operation Timing
Add timing measurements for Motor queries:
```python
import time

start = time.perf_counter()
result = await db.zones.find_one({"fqdn": fqdn})
duration_ms = (time.perf_counter() - start) * 1000

logger.info("db_query", extra={
    "operation": "find_one",
    "collection": "zones",
    "duration_ms": duration_ms,
    "slow": duration_ms > 100
})
```

### 4. Rule Evaluation Tracing
Instrument `zentralbibliothek/ruleengine.py` to log:
- Which rules loaded
- Which predicates matched/failed
- Which actions executed

### 5. OpenTelemetry Metrics
Activate `telemetry.py` middleware and add meters:
```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
request_counter = meter.create_counter("api.requests")
response_timer = meter.create_histogram("api.response_time_ms")

# In middleware or routes:
request_counter.add(1, {"endpoint": "/zones", "status": 200})
```

---

## Testing

Run existing integration tests:
```bash
cd dusseldorf/api/src/api
pytest test_main.py -v
```

All tests should pass. Check logs for:
- `auth_success` events
- `permission_check` events
- `zone_created` / `zone_deleted` events

---

