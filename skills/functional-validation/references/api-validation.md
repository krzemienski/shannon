# Backend API Functional Validation

This reference is loaded by the `functional-validation` skill ONLY when the project exposes HTTP, gRPC, or WebSocket endpoints (REST routes, OpenAPI spec, FastAPI, Express, Vapor, Actix, Gin). It expands the start/exercise/verify protocol for backend-only validation.

Do not load this file for client-only apps — those go through `ios-validation.md` or `web-validation.md`. For full-stack work, load this AND the relevant client reference.

## The protocol at a glance

```
start backend + dependencies -> poll health -> exercise endpoints with curl
or grpcurl -> capture response bodies + headers + status codes ->
verify against PASS criteria -> verdict
```

API validation is the only platform where the "real system" is unambiguously the running process plus its data stores. There is no UI ambiguity, no rendering delay, no user-input simulation. Everything is observable through the wire protocol.

## Detection signals (parent skill already checked)

| File present | Implication | Start command |
|---|---|---|
| `package.json` + Express/Fastify/Koa | Node API | `npm run dev` or `npm start` |
| `pyproject.toml` + FastAPI/Flask/Django | Python API | `uvicorn app:app` / `flask run` / `python manage.py runserver` |
| `go.mod` + `net/http` or Gin/Echo | Go API | `go run ./cmd/server` |
| `Cargo.toml` + Actix/Axum/Rocket | Rust API | `cargo run --release --bin server` |
| `Gemfile` + Rails/Sinatra | Ruby API | `bundle exec rails s` |
| `Package.swift` + Vapor | Swift API | `swift run App serve` |
| `.proto` files + gRPC stubs | gRPC API | start as above + use `grpcurl` |
| `openapi.yaml` or `swagger.json` | OpenAPI-described | derive endpoint list from spec |

## Phase 1 — Start the real backend AND its dependencies

NEVER validate an API while its database, cache, message broker, or auth provider is mocked or absent. The point of API validation is that the real system, end to end, behaves correctly.

```bash
RUN_DIR="e2e-evidence/$(date +%Y-%m-%dT%H-%M-%S)/api-journey"
mkdir -p "$RUN_DIR"

# Start database (if any)
docker compose up -d postgres redis 2>&1 | tee "$RUN_DIR/deps-up.log"
# OR start native services as a developer would
brew services start postgresql@15 2>&1 | tee "$RUN_DIR/deps-up.log"

# Run migrations against the live database
( cd backend && npm run db:migrate ) 2>&1 | tee "$RUN_DIR/migrate.log"

# Start the backend
( cd backend && npm run dev ) > "$RUN_DIR/server.log" 2>&1 &
SERVER_PID=$!

# Health gate — DO NOT proceed until /health returns 200
for i in $(seq 1 60); do
  if curl -fsS http://localhost:3000/health > "$RUN_DIR/healthz.json" 2>/dev/null; then
    echo "Backend ready on attempt $i"
    break
  fi
  sleep 1
  if [ "$i" = "60" ]; then
    echo "FAIL: backend did not become healthy in 60s"
    tail -50 "$RUN_DIR/server.log"
    kill "$SERVER_PID" 2>/dev/null
    exit 1
  fi
done

# Verify dependencies the backend connected to
curl -fsS http://localhost:3000/health/deep | jq . | tee "$RUN_DIR/health-deep.json"
```

If the backend uses a third-party API (Stripe, Twilio, SendGrid), use their sandbox / test environment endpoint — that IS still the real system. Local mocks that imitate Stripe are not.

## Phase 2 — Exercise endpoints with curl

Pass real headers including `Authorization`, `Content-Type`, and any custom auth header the API requires. Capture the full response — status code, headers, body — for every call.

```bash
# A canonical curl invocation that captures everything
curl -fsS \
  -X POST http://localhost:3000/api/users \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User"}' \
  -o "$RUN_DIR/step-01-create-user.body.json" \
  -D "$RUN_DIR/step-01-create-user.headers.txt" \
  -w "%{http_code}" \
  > "$RUN_DIR/step-01-create-user.status.txt"
```

NEVER use `-s` without `-f` — silent mode swallows server errors. Use `-fsS`:
- `-f` fails on HTTP error (4xx, 5xx) with non-zero exit
- `-s` silent (no progress meter)
- `-S` show errors even when silent

If `-f` returns non-zero, capture the body too — error responses contain the diagnostic message.

```bash
# Negative-path capture: server returns 4xx/5xx
curl -sS \
  -X POST http://localhost:3000/api/users \
  -d '{}' \
  -o "$RUN_DIR/step-02-bad-request.body.json" \
  -w "%{http_code}" \
  > "$RUN_DIR/step-02-bad-request.status.txt"
```

For gRPC:

```bash
grpcurl -plaintext \
  -d '{"email":"test@example.com"}' \
  localhost:50051 user.UserService/CreateUser \
  2>&1 | tee "$RUN_DIR/step-01-grpc-create.txt"
```

For WebSocket:

```bash
websocat -1 ws://localhost:3000/ws/events \
  > "$RUN_DIR/step-03-ws-events.txt" \
  2> "$RUN_DIR/step-03-ws-errors.txt"
```

## Phase 3 — Verify response content, not just status

A 200 response with the wrong body is still a failure. Read the body. Cross-check fields against PASS criteria.

```bash
# Verify status
STATUS=$(cat "$RUN_DIR/step-01-create-user.status.txt")
test "$STATUS" = "201" || { echo "FAIL: status=$STATUS"; exit 1; }

# Verify body schema and content
jq -e '.id and .email == "test@example.com"' \
  "$RUN_DIR/step-01-create-user.body.json" \
  || { echo "FAIL: body missing id or wrong email"; jq . "$RUN_DIR/step-01-create-user.body.json"; exit 1; }

# Verify side-effect — did the row appear in the database?
psql -At -c "SELECT email FROM users WHERE email='test@example.com'" \
  > "$RUN_DIR/db-check.txt"
test "$(cat "$RUN_DIR/db-check.txt")" = "test@example.com" \
  || { echo "FAIL: user not in DB"; exit 1; }
```

For authentication endpoints, verify the token AND the round-trip:

```bash
# Sign in -> capture token -> use token on protected endpoint
TOKEN=$(jq -r .access_token "$RUN_DIR/step-04-login.body.json")
test -n "$TOKEN" -a "$TOKEN" != "null" || { echo "FAIL: no token"; exit 1; }

curl -fsS \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/me \
  -o "$RUN_DIR/step-05-me.body.json"

jq -e '.email == "test@example.com"' "$RUN_DIR/step-05-me.body.json" \
  || { echo "FAIL: /me did not echo the signed-in user"; exit 1; }
```

## Phase 4 — Inspect server logs for hidden errors

A 200 OK with a stack trace in the server log is a hidden bug. Always tail the server log.

```bash
grep -iE 'error|panic|fatal|unhandled|stack trace' "$RUN_DIR/server.log" \
  | grep -v "200 OK" \
  > "$RUN_DIR/server-warnings.txt"

# A non-empty warnings file is a signal to investigate
test -s "$RUN_DIR/server-warnings.txt" \
  && echo "WARNING: server logged errors — see server-warnings.txt"
```

For databases, check the query log for slow queries or missing indices that would manifest as production issues:

```bash
docker logs postgres 2>&1 | grep -E 'duration: [0-9]{4,}' \
  > "$RUN_DIR/slow-queries.txt"
```

## Phase 5 — Tear down cleanly

```bash
kill "$SERVER_PID" 2>/dev/null
wait
docker compose down 2>&1 | tee "$RUN_DIR/teardown.log"
```

## Evidence quality table

| Evidence | Good | Bad |
|---|---|---|
| status code | `201` matches expected for resource creation | `200` from a route that should 401 |
| response body | `{"id": 42, "email": "test@example.com"}` parsed and field-checked | "got a JSON, didn't read it" |
| response headers | `Content-Type: application/json; charset=utf-8` verified | "headers were there" |
| server log | grep'd for error / panic / fatal — empty | "log was long, didn't check" |
| side-effect | Database row visible via direct SQL query | "API said 201 so the row must exist" |
| round-trip | Created resource is readable via GET on the same endpoint | "POST returned 201; trust it" |

## Common API failure modes

| Symptom | Likely cause | Remedy |
|---|---|---|
| Health endpoint 200 but deep endpoint 500 | Database connection lazy and broken | Hit a deep endpoint as part of health gate |
| `curl: (52) Empty reply from server` | Server crashed mid-request | Check `server.log` for stack trace |
| Different response for same request | Caching, state pollution, or race | Restart server between cases; isolate request order |
| 401 from supposedly-public endpoint | Auth middleware misconfigured | Read middleware order in app setup |
| `connection refused` | Server bound to wrong interface | Verify with `lsof -iTCP -sTCP:LISTEN -P` |
| All responses 200 but content wrong | Mock middleware accidentally active | Grep server source for mock/test-mode flags |

## When API path does NOT apply

- Server-Sent Events streams — use a streaming client; capture chunks to file
- Long-poll endpoints — set `--max-time` higher; expect eventual response, not instant
- Background-worker-only services (no HTTP surface) — verify via the queue or job log
- Webhook senders — set up an inbox endpoint (e.g., `ngrok` to a local capture server) and verify what was sent

## Evidence checklist

A PASS for an API endpoint requires at least:
- `migrate.log` ending in success
- `healthz.json` showing healthy status before any test calls
- `step-NN-<endpoint>.body.json` + `.headers.txt` + `.status.txt` per call
- `server-warnings.txt` checked (and ideally empty)
- A `verdict.md` citing specific JSON fields and HTTP status codes from the captured evidence
