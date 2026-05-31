# Backend API Validation

> Real-system validation for HTTP/JSON APIs: start the server, hit real endpoints with real `curl`, verify response shape + status + headers + side effects. No mocks. No stubs. The handler you run is the handler you ship.

## Detection signals

A project is API when frontend files are absent OR present alongside backend handlers, and you can identify:

| Framework | Marker | Run command |
|-----------|--------|-------------|
| FastAPI | `from fastapi import` + `app = FastAPI()` | `uvicorn main:app --reload` |
| Flask | `from flask import` + `app = Flask(__name__)` | `flask run` or `python -m flask run` |
| Express | `require('express')` + `app.listen(PORT)` | `node server.js` or `npm start` |
| Django | `manage.py`, `urls.py` | `python manage.py runserver` |
| Rails | `Gemfile` with `rails` | `rails server` |
| Gin | Go `gin.New()` | `go run .` |
| Actix-web | Rust `HttpServer::new` | `cargo run --release` |
| Axum | Rust `axum::Router` | `cargo run --release` |

Look for an OpenAPI spec (`openapi.yaml`, `swagger.json`) — it lists every endpoint you need to validate.

## Validation protocol

### Phase 1 — Start the server

The real server. Not a mock. Capture the boot log:

```bash
# FastAPI / uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 \
  > e2e-evidence/server.log 2>&1 &
SERVER_PID=$!
echo "server pid: $SERVER_PID" > e2e-evidence/server.pid

# Wait for readiness (don't just sleep — poll)
for i in $(seq 1 30); do
  curl -sf http://localhost:8000/health >/dev/null && break
  sleep 1
done
```

Always trap the PID so the validation script can shut the server down on exit:

```bash
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT
```

### Phase 2 — Health check (smoke)

Most servers expose `/health`, `/healthz`, `/ping`, or similar. Validate it returns 200 with reasonable content:

```bash
curl -sf -w '\nstatus=%{http_code}\nrtt=%{time_total}s\n' \
  http://localhost:8000/health \
  | tee e2e-evidence/smoke-health.txt
```

**PASS:** status=200, RTT < 1s, body is parseable (JSON or plain "OK"). **FAIL:** status != 200 or connection refused.

If the server has no health endpoint, hit the simplest GET route as the smoke test.

### Phase 3 — Per-endpoint journey

For every endpoint in the OpenAPI spec (or every route discovered by code-grep), capture:
- request method + path + headers + body
- response status + headers + body
- timing (`-w '%{time_total}s'`)

```bash
# GET — list resource
curl -s -w '\n---\nstatus=%{http_code}\nrtt=%{time_total}s' \
  -H 'Accept: application/json' \
  http://localhost:8000/api/sessions \
  | tee e2e-evidence/journey-01-list-sessions.txt

# POST — create resource
curl -s -X POST \
  -H 'Content-Type: application/json' \
  -d '{"name":"test-session","status":"active"}' \
  -w '\n---\nstatus=%{http_code}\nrtt=%{time_total}s' \
  http://localhost:8000/api/sessions \
  | tee e2e-evidence/journey-02-create-session.txt

# PATCH — update resource
SESSION_ID=$(jq -r '.id' e2e-evidence/journey-02-create-session.txt)
curl -s -X PATCH \
  -H 'Content-Type: application/json' \
  -d '{"status":"complete"}' \
  -w '\n---\nstatus=%{http_code}\nrtt=%{time_total}s' \
  http://localhost:8000/api/sessions/$SESSION_ID \
  | tee e2e-evidence/journey-03-update-session.txt

# DELETE — remove resource
curl -s -X DELETE \
  -w '\n---\nstatus=%{http_code}\nrtt=%{time_total}s' \
  http://localhost:8000/api/sessions/$SESSION_ID \
  | tee e2e-evidence/journey-04-delete-session.txt
```

### Phase 4 — Response-shape verification

A 200 response with the wrong body shape is still a FAIL. Use `jq` to assert structure:

```bash
# Required fields present?
jq -e '.id and .name and .status and .created_at' \
  e2e-evidence/journey-02-create-session.txt \
  > /dev/null || { echo "missing required fields"; exit 1; }

# Status enum is one of the allowed values?
status=$(jq -r '.status' e2e-evidence/journey-02-create-session.txt)
case "$status" in
  active|pending|complete|failed) echo "status OK: $status" ;;
  *) echo "unexpected status: $status"; exit 1 ;;
esac

# Pagination shape correct?
jq -e '.items | type == "array"' \
  e2e-evidence/journey-01-list-sessions.txt \
  > /dev/null || { echo "items is not an array"; exit 1; }
jq -e '.total | type == "number"' \
  e2e-evidence/journey-01-list-sessions.txt \
  > /dev/null || { echo "total is not a number"; exit 1; }
```

### Phase 5 — Side-effect verification

For mutating endpoints (POST/PATCH/DELETE), verify the side effect by reading back:

```bash
# After POST /api/sessions, GET /api/sessions/{id} should return it
curl -s http://localhost:8000/api/sessions/$SESSION_ID \
  | tee e2e-evidence/journey-02-readback.txt
jq -e ".id == \"$SESSION_ID\"" e2e-evidence/journey-02-readback.txt \
  > /dev/null || { echo "POST created resource not readable"; exit 1; }

# After DELETE, the same GET should return 404
status=$(curl -s -o /dev/null -w '%{http_code}' \
  http://localhost:8000/api/sessions/$SESSION_ID)
[ "$status" = "404" ] || { echo "DELETE didn't actually delete (got $status)"; exit 1; }
```

If the API talks to a database, validate at the database layer too — read the rows directly:

```bash
psql -d $DB_NAME -c "SELECT id, status FROM sessions WHERE id = '$SESSION_ID';" \
  | tee e2e-evidence/journey-02-db-readback.txt
```

### Phase 6 — Error path validation

A working happy path with broken error paths is still incomplete. For each endpoint, hit it with bad input and verify the error response is well-formed:

```bash
# 400 on bad JSON body
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{not valid json}' \
  -w '\nstatus=%{http_code}' \
  http://localhost:8000/api/sessions \
  | tee e2e-evidence/journey-05-bad-json.txt
# expect status=400

# 404 on missing resource
curl -s -w '\nstatus=%{http_code}' \
  http://localhost:8000/api/sessions/does-not-exist \
  | tee e2e-evidence/journey-06-not-found.txt
# expect status=404

# 401 if auth required (no token)
curl -s -w '\nstatus=%{http_code}' \
  http://localhost:8000/api/admin/something \
  | tee e2e-evidence/journey-07-no-auth.txt
# expect status=401 (or 403 depending on convention)

# 422 / validation error on missing required field
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{}' \
  -w '\nstatus=%{http_code}' \
  http://localhost:8000/api/sessions \
  | tee e2e-evidence/journey-08-validation.txt
# expect status=422 (FastAPI) or 400
```

### Phase 7 — Verdict

```
e2e-evidence/journey-02-create-session.verdict.md
---
**Journey**: POST /api/sessions
**Request**: {"name":"test-session","status":"active"}
**Expected**: status=201, response has id/name/status/created_at, readback returns same
**Observed**:
  - status: 201 ✓
  - response: {"id":"abc123","name":"test-session","status":"active","created_at":"…"} ✓
  - readback: same ✓
  - DB row: present, status=active ✓
**Verdict**: PASS
**Evidence**: journey-02-create-session.txt, journey-02-readback.txt, journey-02-db-readback.txt
```

## Concurrency / load (optional)

If the API is meant to serve concurrent traffic, hit it with parallel curls:

```bash
seq 1 100 | xargs -P 20 -I {} \
  curl -s -o /dev/null -w '%{http_code}\n' \
  http://localhost:8000/api/sessions \
  | sort | uniq -c \
  | tee e2e-evidence/load-100-parallel-20.txt

# Expected: 100 lines of "200" — any 500 or 503 is a finding
```

## Iron Rule for APIs

NEVER replace the database, HTTP client, auth layer, or downstream service with a mock during validation. If a dependency is unavailable, start it (Docker, local install, real cloud instance). If you can't start it, the validation FAILs — don't paper over with a stub.

If the API talks to a paid external service (Stripe, Twilio, etc.), use the SANDBOX/TEST mode of that real service — not a local mock. Real `https://api.stripe.com/.../test` behaves like real Stripe; a local mock doesn't.

## Common anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|------------------|
| Mocking the database in tests | Mock returns whatever you scripted, hides real bugs | Start a real Postgres (Docker is fine); curl + verify DB |
| Status-200-only verdict | 200 with wrong body still passes | jq-assert response shape per journey |
| Skipping error paths | Happy-path PASS gives false confidence | Hit every endpoint with bad input; expect documented error codes |
| One curl per validation | Sequential journeys miss races, leaks, state issues | Add a concurrent journey for load-tested endpoints |
| Validating against staging instead of local | Staging has different config, different data | Validate against the build you intend to ship |

## Cross-references

- `references/cli-validation.md` — if a CLI hits this API, validate both layers
- `references/web-validation.md` — if a frontend hits this API, validate both layers
- `references/fullstack-validation.md` — full-stack composition order
- `skills/agent-browser/` — for frontend-driven validation that triggers API calls
- `skills/no-mocking-validation-gates/` — prevents the DB-mock temptation
- `skills/gate-validation-discipline/` — Iron Rule on the API verdict
