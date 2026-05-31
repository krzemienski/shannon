# Full-Stack Validation

> Real-system validation across the full stack: database → backend API → frontend (or CLI / mobile client). Validate bottom-up so an apparent frontend bug isn't actually a backend bug isn't actually a database bug. No mocks at any layer.

## Detection signals

A project is full-stack when frontend framework files AND backend routes/handlers BOTH exist:

```bash
HAS_FRONTEND=$(find . -maxdepth 3 \( -name '*.jsx' -o -name '*.tsx' -o -name '*.vue' -o -name '*.svelte' -o -name 'next.config*' \) 2>/dev/null | head -1)
HAS_BACKEND=$(find . -maxdepth 3 \( -name 'routes*' -o -name 'handlers*' -o -name 'main.py' -o -name 'server.js' -o -name 'app.py' \) 2>/dev/null | head -1)
[ -n "$HAS_FRONTEND" ] && [ -n "$HAS_BACKEND" ] && echo "fullstack"
```

Monorepos with `apps/web` + `apps/api`, T3 stack, Remix loaders + actions, Next.js with `pages/api/`, Nuxt with `server/api/`, SvelteKit `+server.ts` — all fullstack.

## The bottom-up rule

Validate in dependency order. A failure at layer N should be attributed to layer N, not to layer N+1.

```
   Database         ← validate first
       ↓
   Backend API      ← validate second
       ↓
   Frontend / CLI / Mobile  ← validate last
```

Common attribution bugs:
- "The button doesn't work" → actually backend returned 500 → actually DB query timed out
- "Data doesn't render" → actually API returned wrong shape → actually migration didn't run
- "Login fails" → actually JWT secret mismatch between client and server config

Bottom-up validation catches the real layer immediately.

## Validation protocol

### Phase 1 — Database (deepest layer)

```bash
# 1. Start the database
# Postgres via Docker:
docker run -d --name validation-pg \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=app_validation \
  -p 5432:5432 \
  postgres:16

# Wait for readiness
for i in $(seq 1 30); do
  pg_isready -h localhost -U postgres && break
  sleep 1
done

# 2. Apply schema / migrations
psql -h localhost -U postgres -d app_validation \
  -f db/schema.sql 2>&1 | tee e2e-evidence/db-schema.log

# Or with the framework's tool:
# npm run db:migrate
# python manage.py migrate
# alembic upgrade head
# rails db:migrate

# 3. Seed minimal test data (NOT mocks — real rows with realistic values)
psql -h localhost -U postgres -d app_validation -c "
  INSERT INTO users (id, email, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'alice@example.com', 'Alice'),
    ('22222222-2222-2222-2222-222222222222', 'bob@example.com', 'Bob');
" 2>&1 | tee e2e-evidence/db-seed.log

# 4. Verify schema by querying
psql -h localhost -U postgres -d app_validation -c "
  SELECT table_name FROM information_schema.tables
  WHERE table_schema = 'public';
" | tee e2e-evidence/db-tables.txt

# 5. PASS criterion: all expected tables exist, seed rows readable
```

For SQLite, replace `psql` with `sqlite3 ./db.sqlite`. For MongoDB, use `mongosh`. Don't substitute an ORM-level dump for the raw DB inspection — verify the actual schema.

### Phase 2 — Backend API

Now that the DB is real, start the backend pointing at it:

```bash
# Set the env var pointing at the real validation DB
export DATABASE_URL="postgres://postgres:test@localhost:5432/app_validation"
export NODE_ENV="validation"

# Start the API
npm run start --workspace=apps/api > e2e-evidence/api-server.log 2>&1 &
API_PID=$!
trap 'kill $API_PID 2>/dev/null; docker rm -f validation-pg 2>/dev/null' EXIT

# Wait for /health
for i in $(seq 1 30); do
  curl -sf http://localhost:8000/health && break
  sleep 1
done
```

Now run the api-validation.md protocol (smoke + per-endpoint + side-effect + error paths). Every API journey verdict goes into `e2e-evidence/api-journeys/journey-NN.verdict.md`.

**Critical:** when an API journey writes data, immediately verify at the DB layer:

```bash
# After POST /api/sessions
SESSION_ID=$(jq -r '.id' e2e-evidence/api-journeys/journey-02-create.txt)
psql -h localhost -U postgres -d app_validation -c "
  SELECT id, status, created_at FROM sessions WHERE id = '$SESSION_ID';
" | tee e2e-evidence/api-journeys/journey-02-db-readback.txt
```

If the API said "created" but the DB has no row, that's a backend bug (probably transaction-not-committed).

### Phase 3 — Frontend / CLI / Mobile

With DB + API running, start the client. Configure it to talk to the real local API (not a mock, not a remote staging):

```bash
export API_URL="http://localhost:8000"
export NEXT_PUBLIC_API_URL="http://localhost:8000"

npm run dev --workspace=apps/web > e2e-evidence/web-dev.log 2>&1 &
WEB_PID=$!

for i in $(seq 1 60); do
  curl -sf http://localhost:3000 >/dev/null 2>&1 && break
  sleep 1
done
```

Now run web-validation.md (or cli-validation.md, or ios-validation.md depending on client). Every frontend journey verdict goes into `e2e-evidence/web-journeys/journey-NN.verdict.md`.

When a frontend journey triggers a backend call, capture the network log and verify:
1. The expected request fired (`agent-browser network`)
2. The API journey for that endpoint also PASSed (cross-reference)
3. The UI state reflects what the API returned

### Phase 4 — Integration journeys (the actual end-to-end)

Pure single-layer journeys aren't enough. Add scenarios that touch every layer:

```
Journey: "User creates a session, logs out, logs back in, sees their session"

Steps:
  1. UI: navigate to /signup, fill form, submit
  2. API: POST /api/users → DB: row in users table
  3. UI: navigate to /dashboard, click "Create Session"
  4. API: POST /api/sessions → DB: row in sessions table linked to user
  5. UI: click "Logout"
  6. UI: navigate to /login, fill form, submit
  7. API: POST /api/auth/login → returns JWT
  8. UI: navigate to /dashboard, see the session created in step 4

Verdict: PASS only if every step's evidence is captured AND the final dashboard
         shows the session created several steps earlier (proves the data round-tripped
         through the DB correctly).
```

Save the integration journey verdicts at `e2e-evidence/integration-journeys/`.

### Phase 5 — Concurrent / multi-user journeys

```
Journey: "Two users edit the same session simultaneously; last-write-wins resolves correctly"

Steps:
  1. User A signs up, creates session S
  2. User B signs up, gets access to S (sharing flow)
  3. User A starts editing S (long-poll or websocket)
  4. User B sends a PATCH to S
  5. User A's UI receives a notification
  6. User A's final commit doesn't clobber B's PATCH

Verdict: requires careful timing, real concurrency through real network — no mocks.
```

These journeys are rare but expose the bugs unit tests miss.

### Phase 6 — Teardown

```bash
# Stop client
kill $WEB_PID 2>/dev/null

# Stop API
kill $API_PID 2>/dev/null

# Stop DB
docker rm -f validation-pg 2>/dev/null

# Keep evidence directory; nothing else
```

## Iron Rule for full-stack

NEVER mock any layer. Not the DB, not the API, not the frontend. Each layer runs as the real production code would, against real dependencies.

If a layer is genuinely unavailable (third-party that you don't control), use that third-party's REAL sandbox/test mode. Real Stripe Test mode beats local Stripe mock. Real SendGrid sandbox beats local SMTP mock.

NEVER skip the bottom-up order. Validating frontend-first means a backend bug looks like a frontend bug — wasted hours.

NEVER share a validation DB between runs. Each validation should start from a clean schema + seed, so journey-2's evidence isn't polluted by journey-1's writes.

## Layer-attribution table

When something fails, attribute correctly:

| Symptom | Likely layer | Verify by |
|---------|--------------|-----------|
| 500 from API | Backend or DB | Check api-server.log + DB query log |
| 404 from API | Backend (route missing) | Check route table |
| Frontend shows "loading…" forever | API not responding | Check API journey for that endpoint |
| Frontend shows stale data | API + caching | Compare DB to API response to UI rendering |
| API returns empty list | DB or API filter logic | Query DB directly with same filter |
| Test passes locally, fails in CI | Environment / config | Diff env vars; check CI's DB setup |

## Common anti-patterns

| Anti-pattern | Why it's wrong | Do this instead |
|--------------|----------------|------------------|
| Validating UI without checking the DB | UI can show stale / cached / wrong data while DB is fine, or vice versa | After every mutation, verify at BOTH API and DB |
| Sharing a DB across runs | Stale rows from run N pollute run N+1's evidence | Fresh schema + seed per run |
| Mocking the API "for speed" | Mocks lie; speed savings are paid for in debugging | Real local API, started once per run |
| Validating against staging | Staging has different data, different config, different env | Local stack only; staging is for separate pre-release checks |
| Skipping the integration journey | Per-layer PASS doesn't guarantee end-to-end works | Always add at least 1 cross-layer journey |

## Cross-references

- `references/cli-validation.md` — when the client is a CLI
- `references/api-validation.md` — backend-layer protocol
- `references/web-validation.md` — frontend-layer protocol
- `references/ios-validation.md` — when the client is iOS
- `skills/agent-browser/` — for the web client layer
- `skills/no-mocking-validation-gates/` — prevents the mock-the-other-layer temptation
- `skills/gate-validation-discipline/` — per-layer verdict gates
- `skills/full-functional-audit/` — full-app audit on top of this protocol
