# CLI Automation

> The discipline of using CLIs / APIs instead of asking the human to do something manually. If a CLI exists, Claude uses it. Period.

## The rule

```
If Claude CAN do it via CLI / API / tool, Claude MUST do it.
Don't ask the human to:
  - Deploy to a service (CLIs exist)
  - Create cloud resources (CLIs exist)
  - Set env vars (CLIs exist)
  - Run builds / tests (Bash)
  - Write files (Write tool)
  - Commit / push (git)
  - Create webhooks (provider CLIs)
```

The exception is checkpoint:human-action — and even those should be re-checked against the rule.

## Common automatable operations

### Cloud deploys

| Provider | CLI |
|----------|-----|
| Vercel | `vercel deploy --prod` |
| Netlify | `netlify deploy --prod` |
| Railway | `railway up` |
| Fly.io | `fly deploy` |
| Cloudflare Pages / Workers | `wrangler deploy` |
| AWS Amplify | `amplify publish` |
| Heroku | `git push heroku main` |

### Cloud resource creation

| Provider | CLI examples |
|----------|--------------|
| AWS | `aws s3 mb`, `aws lambda create-function`, ... |
| GCP | `gcloud compute instances create`, ... |
| Azure | `az vm create`, ... |
| DigitalOcean | `doctl compute droplet create`, ... |

### Database operations

| DB | CLI |
|----|-----|
| Postgres | `psql`, `createdb`, `pg_dump` |
| MySQL | `mysql`, `mysqldump` |
| SQLite | `sqlite3` |
| Redis | `redis-cli` |
| MongoDB | `mongosh`, `mongoexport` |

### Migration tools

| Tool | Command |
|------|---------|
| Prisma | `npx prisma migrate dev` / `deploy` |
| Sequelize | `sequelize db:migrate` |
| Alembic | `alembic upgrade head` |
| Django | `python manage.py migrate` |
| Rails | `rails db:migrate` |
| Knex | `knex migrate:latest` |

### Service APIs

| Service | CLI |
|---------|-----|
| Stripe | `stripe webhooks create`, `stripe trigger ...` |
| Twilio | `twilio api:core:messages:create` |
| SendGrid | `sendgrid mail send` |
| GitHub | `gh pr create`, `gh issue create`, `gh release create` |
| GitLab | `glab pr create`, ... |
| Linear | `linear issue create` (via API) |

### Environment / secrets

| Provider | CLI |
|----------|-----|
| Vercel | `vercel env add VAR_NAME` |
| Netlify | `netlify env:set VAR_NAME value` |
| Heroku | `heroku config:set VAR_NAME=value` |
| AWS Parameter Store | `aws ssm put-parameter` |
| Doppler | `doppler secrets set VAR_NAME=value` |

## When the CLI doesn't exist

Sometimes there genuinely isn't a CLI. The escape order:

1. Check for an HTTP API → use `curl` from Bash
2. Check for an MCP server → use it
3. Check for browser automation → `agent-browser` for web UIs
4. Last resort: `checkpoint:human-action` — but document WHY (no API exists)

If you reach the last resort, your justification should be: "I searched <provider> docs for 'API' and 'CLI' and found neither covers this operation."

## Reducing human-action by infrastructure

If the project keeps hitting `human-action` for the same operation, add infrastructure:

```
Pattern: Account creation requires 2FA + manual phone code

Bad: human-action every time
Better: invest in a test-only account with 2FA disabled, used only for
        automation. The "real users have 2FA" property is tested elsewhere.

Best: API key with appropriate scope (no 2FA for service-to-service auth)
```

Infrastructure investment > checkpoint friction.

## CLI hygiene in plans

When a plan invokes a CLI:

```markdown
Task 3: Deploy preview environment to Vercel

Command: `vercel deploy --pre`
Expected output: deployment URL on the last line
Verify: curl the deployment URL; expect 200 + page content
On failure: capture stderr, check token validity, retry once
```

Spec the command, expected output, verification, and failure handling. Not just the command.

## Token / credential management

CLIs need credentials. Plans should reference:
- Where the credential lives (env var, secret manager)
- How to refresh if expired
- What to do if missing (`checkpoint:human-action` to set it up — once)

```markdown
Prereq: VERCEL_TOKEN environment variable set
If missing: see vercel.com/account/tokens to create one, then
            `doppler secrets set VERCEL_TOKEN=...`
            (one-time human-action)
```

## Anti-patterns

| Anti-pattern | Why | Do instead |
|---|---|---|
| `checkpoint:human-action: deploy` | CLI exists | Use the CLI |
| `checkpoint:human-action: set env var` | CLI exists | Use the CLI |
| `checkpoint:human-action: create cloud resource` | CLI exists | Use the CLI |
| Hand-rolled curl when SDK / CLI exists | More fragile, less ergonomic | Use the official tool |
| Hardcoded credential in command | Leaks in logs | Reference env var |
| No verification after command | "Looks like it worked" | Verify expected post-state |

## Cross-references

- _Historical: this content was absorbed from the legacy `create-plans` skill into its absorbing parent. The original `create-plans` skill no longer exists in v1._
- `references/checkpoints.md` — sibling reference
- `references/git-integration.md` — git-specific CLI patterns
- `references/user-gates.md` — when to surface to user vs automate
