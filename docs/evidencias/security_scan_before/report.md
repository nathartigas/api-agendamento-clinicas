# Security Review: nathalia_artigas_DR2_AT

## Scope

Complete static review of authored executable source, tests that establish security behavior, dependency manifests, environment template, and repository security policy.

- Scan mode: repository
- Target kind: directory_snapshot
- Target ID: target_sha256_834f8ea84ec8b8be108d716d0ff622c0b00bfac17d8ed26a581b9badab02e83e
- Snapshot digest: codex-security-snapshot/v1:sha256:06d08d93a36a357ad26e7b387c337121bd44830822f16fbee728997e14a68e55
- Inventory strategy: directory
- Included paths: .
- Excluded paths: none
- Runtime or test status: Static source review only; no vulnerability-triggering runtime inputs were executed during the scan.

Limitations and exclusions:
- No independent delegated baseline was permitted.
- No production infrastructure configuration was available.
- Excluded .venv/\*\*: Third-party installed dependencies, not authored product source.
- Excluded data/\*\*: Generated local database artifacts; contents were not inspected.
- Excluded docs/\*\*: Narrative assessment artifacts used as context, not executable product source.

### Scan Summary

| Field | Value |
| --- | --- |
| Scan outcome | completed |
| Reportable findings | 3 |
| Severity mix | high: 1, medium: 1, low: 1 |
| Confidence mix | high: 3 |
| Coverage | complete |
| Validation mode | Source-backed sequential baseline and focused investigation. |

Canonical artifacts: `scan-manifest.json`, `findings.json`, and `coverage.json`. This report is a deterministic projection of those files.

## Threat Model

FastAPI healthcare scheduling API with human JWT sessions, a scoped M2M availability endpoint, Jinja2 reception HTML, SQLModel persistence, and no supplied production edge configuration.

### Assets

- Patient identity and health-related scheduling data
- Appointment integrity and availability
- Human passwords and JWT authority
- Laboratory client secret and restricted service scope

### Trust Boundaries

- Untrusted HTTP clients to FastAPI
- JWT claims to current application authority
- FastAPI to SQLModel database
- Persisted user content to reception browser
- Laboratory client to availability-only service surface

### Attacker Capabilities

- Unauthenticated clients can reach both token endpoints
- Authenticated professionals control appointment identifiers and public notes
- A token thief may possess a valid pre-deactivation JWT
- Attackers do not initially control database, JWT key, host, or administrator account

### Security Objectives

- Enforce role, scope, MFA, and ownership for every protected object
- Permit rapid revocation of compromised identities
- Bound expensive authentication work
- Never expose clinical data to M2M clients
- Encode HTML and parameterize database access
- Apply explicit browser and transport hardening

### Assumptions

- Current SQLite deployment is development-only
- TLS is expected at a future reverse proxy but no manifest proves it
- MFA is intentionally simulated for the academic exercise
- Documents and generated environments are excluded from executable-source coverage

## Findings

| Finding | Severity | Confidence | Detailed write-up |
| --- | --- | --- | --- |
| [Unlimited token attempts permit credential attacks and bcrypt resource exhaustion](#finding-1) | high | high | inline below |
| [Disabled users and OAuth clients retain access until JWT expiry](#finding-2) | medium | high | inline below |
| [Responses omit required transport and browser hardening headers](#finding-3) | low | high | inline below |

### Confidence Scale

| Label | Meaning |
| --- | --- |
| high | Direct evidence supports the finding with no material unresolved blocker. |
| medium | Evidence supports a plausible issue, but material runtime or reachability proof remains. |
| low | Evidence is incomplete and the item is retained only for explicit follow-up. |

<a id="finding-1"></a>

### [1] Unlimited token attempts permit credential attacks and bcrypt resource exhaustion

| Field | Value |
| --- | --- |
| Severity | high |
| Confidence | high |
| Confidence rationale | Both externally reachable token handlers invoke bcrypt-backed authentication without any application-level request limiter or lockout. |
| Category | OWASP API4:2023 Unrestricted Resource Consumption / API2:2023 Broken Authentication |
| CWE | CWE-307, CWE-400 |
| Affected lines | app/routes/auth.py:28-40, app/routes/auth.py:69-79 |

#### Summary

Remote clients can submit unlimited password, MFA, and client-secret guesses to both token endpoints, enabling credential stuffing and CPU exhaustion against the healthcare API.

#### Root Cause

The token routes enforce credential correctness but no consumption policy. Because bcrypt intentionally costs CPU, an attacker can combine credential guessing with application-level resource exhaustion.

**Password endpoint directly verifies every request** — `app/routes/auth.py:28-40`

Attacker-controlled credentials reach bcrypt verification on every request; no rate dependency, cooldown, or lockout is present.

```python
@router.post("/token", response_model=TokenResponse)
def issue_user_token(...):
    user = authenticate_user(session, username, password)
    if user is None:
        raise _unauthorized()
```

**Client Credentials endpoint shares the same missing limit** — `app/routes/auth.py:69-79`

The laboratory secret can also be guessed without a request budget, and every attempt performs an expensive bcrypt check.

```python
@router.post("/client-token", response_model=TokenResponse)
def issue_client_token(...):
    client = authenticate_client(session, credentials.username, credentials.password)
    if client is None:
        raise _unauthorized()
```

#### Validation

The route dependencies and application middleware were reviewed; neither endpoint has a limiter and `app/main.py` installs no rate-limiting middleware.

Validation method: static source trace

**Password endpoint directly verifies every request** — `app/routes/auth.py:28-40`

Attacker-controlled credentials reach bcrypt verification on every request; no rate dependency, cooldown, or lockout is present.

```python
@router.post("/token", response_model=TokenResponse)
def issue_user_token(...):
    user = authenticate_user(session, username, password)
    if user is None:
        raise _unauthorized()
```

**Client Credentials endpoint shares the same missing limit** — `app/routes/auth.py:69-79`

The laboratory secret can also be guessed without a request budget, and every attempt performs an expensive bcrypt check.

```python
@router.post("/client-token", response_model=TokenResponse)
def issue_client_token(...):
    client = authenticate_client(session, credentials.username, credentials.password)
    if client is None:
        raise _unauthorized()
```

Assertions:
- Every syntactically valid attempt reaches authentication.
- The same missing control affects the unlisted M2M sibling endpoint.

Limitations:
- No load test was run against the development machine.

#### Dataflow

HTTP form or Basic credentials -\> token route -\> bcrypt verification

- **Source:** unauthenticated request

- **Sink:** bcrypt check

- **Outcome:** credential compromise or degraded availability

**Password endpoint directly verifies every request** — `app/routes/auth.py:28-40`

Attacker-controlled credentials reach bcrypt verification on every request; no rate dependency, cooldown, or lockout is present.

```python
@router.post("/token", response_model=TokenResponse)
def issue_user_token(...):
    user = authenticate_user(session, username, password)
    if user is None:
        raise _unauthorized()
```

**Client Credentials endpoint shares the same missing limit** — `app/routes/auth.py:69-79`

The laboratory secret can also be guessed without a request budget, and every attempt performs an expensive bcrypt check.

```python
@router.post("/client-token", response_model=TokenResponse)
def issue_client_token(...):
    client = authenticate_client(session, credentials.username, credentials.password)
    if client is None:
        raise _unauthorized()
```

#### Reachability

Both endpoints are public by design and require no prior token.

- **Attacker:** remote unauthenticated client

- **Entry point:** /api/v1/auth/token and /api/v1/auth/client-token

- **Outcome:** unbounded authentication work

#### Severity

**High** — The scan assigned high severity; no separate canonical severity rationale was recorded.

Additional runtime or deployment evidence could raise or lower this severity.

Impact assessment:
- **Level:** high
- **Why:** A guessed professional credential exposes health scheduling data; high-volume bcrypt work can also disrupt appointment operations.

Likelihood assessment:
- **Level:** high
- **Why:** Credential stuffing and request flooding require only network reachability.

#### Remediation

Apply centralized per-client rate limits with stricter budgets for human and M2M token endpoints, return 429 with Retry-After, and use a distributed limiter at production scale.

Tests:
- Send attempts up to the login budget and assert the next request receives 429.
- Verify ordinary API routes use a higher request budget.

Preventive controls:
- Define every public route's resource budget centrally and alert on repeated authentication failures.

<a id="finding-2"></a>

### [2] Disabled users and OAuth clients retain access until JWT expiry

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | The principal builder has no database dependency while both persistent identity models expose an `is_active` revocation flag. |
| Category | OWASP API2:2023 Broken Authentication |
| CWE | CWE-613, CWE-284 |
| Affected lines | app/security/authentication.py:44-66, app/models/user.py:22-24, app/models/user.py:35 |

#### Summary

Bearer-token validation trusts identity, role, ownership attributes, and scopes from the signed JWT without checking whether the backing user or OAuth client remains active.

#### Root Cause

The authorization boundary uses a self-contained JWT but omits a current-state lookup. Disabling an identity affects future token issuance only, not already-issued bearer tokens.

**Principal is reconstructed only from JWT claims** — `app/security/authentication.py:44-66`

A valid signature is treated as sufficient current authority; the user/client record is never loaded after token issuance.

```python
def get_current_principal(security_scopes, token):
    payload = decode_access_token(token)
    token_scopes = frozenset(payload.get("scope", "").split())
    ...
    return Principal(subject=str(payload["sub"]), token_type=payload["token_type"], role=payload.get("role"), ...)
```

**Persistent identities already expose active-state flags** — `app/models/user.py:22-35`

The data model provides a revocation decision, but protected requests do not consult it.

```python
is_active: bool = Field(default=True)
...
class OAuthClient(SQLModel, table=True):
    ...
    is_active: bool = Field(default=True)
```

#### Validation

Token issuance checks `is_active`, while protected-request principal construction does not query either identity table.

Validation method: static source trace

**Principal is reconstructed only from JWT claims** — `app/security/authentication.py:44-66`

A valid signature is treated as sufficient current authority; the user/client record is never loaded after token issuance.

```python
def get_current_principal(security_scopes, token):
    payload = decode_access_token(token)
    token_scopes = frozenset(payload.get("scope", "").split())
    ...
    return Principal(subject=str(payload["sub"]), token_type=payload["token_type"], role=payload.get("role"), ...)
```

**Persistent identities already expose active-state flags** — `app/models/user.py:22-35`

The data model provides a revocation decision, but protected requests do not consult it.

```python
is_active: bool = Field(default=True)
...
class OAuthClient(SQLModel, table=True):
    ...
    is_active: bool = Field(default=True)
```

Assertions:
- A previously issued token remains cryptographically valid for the configured 30-minute lifetime after deactivation.

Limitations:
- Exploitation requires possession of a token issued before deactivation.

#### Dataflow

previously issued JWT -\> signature validation -\> claims-only Principal -\> protected route

- **Source:** valid pre-deactivation bearer token

- **Sink:** authorized API operation

- **Outcome:** continued access after administrative revocation

**Principal is reconstructed only from JWT claims** — `app/security/authentication.py:44-66`

A valid signature is treated as sufficient current authority; the user/client record is never loaded after token issuance.

```python
def get_current_principal(security_scopes, token):
    payload = decode_access_token(token)
    token_scopes = frozenset(payload.get("scope", "").split())
    ...
    return Principal(subject=str(payload["sub"]), token_type=payload["token_type"], role=payload.get("role"), ...)
```

**Persistent identities already expose active-state flags** — `app/models/user.py:22-35`

The data model provides a revocation decision, but protected requests do not consult it.

```python
is_active: bool = Field(default=True)
...
class OAuthClient(SQLModel, table=True):
    ...
    is_active: bool = Field(default=True)
```

#### Reachability

Requires a still-unexpired token; no administrator privilege is required after the token has been obtained.

- **Attacker:** disabled account holder or token thief

- **Entry point:** any protected Bearer route

- **Outcome:** continued access during the residual session window

#### Severity

**Medium** — The scan assigned medium severity; no separate canonical severity rationale was recorded.

Additional runtime or deployment evidence could raise or lower this severity.

Impact assessment:
- **Level:** high
- **Why:** The residual token can read protected scheduling data within its existing role and ownership.

Likelihood assessment:
- **Level:** medium
- **Why:** The path depends on prior token issuance or theft and a later deactivation event.

#### Remediation

Resolve the token subject against the database on protected requests, reject inactive or missing users and clients, and verify role, professional link, and allowed scopes still match current state.

Tests:
- Issue a token, deactivate its user, and assert the next protected request returns 401.
- Repeat for a disabled OAuth client.

Preventive controls:
- Add a token-version or revocation mechanism if immediate per-token invalidation is required beyond account status.

<a id="finding-3"></a>

### [3] Responses omit required transport and browser hardening headers

| Field | Value |
| --- | --- |
| Severity | low |
| Confidence | high |
| Confidence rationale | Application construction installs no response-security middleware and the repository contains no proxy or deployment manifest that supplies the headers. |
| Category | OWASP API8:2023 Security Misconfiguration |
| CWE | CWE-693, CWE-1021 |
| Affected lines | app/main.py:17-29 |

#### Summary

The FastAPI application returns API and reception HTML responses without HSTS, frame restrictions, or MIME-sniffing protection, leaving deployment safety dependent on undocumented external infrastructure.

#### Root Cause

HTTP hardening is neither application-owned nor defined in a deployment manifest, so every response lacks the required defense-in-depth headers in the current runnable configuration.

**Application registers routers without response hardening** — `app/main.py:17-29`

No middleware or response hook adds Strict-Transport-Security, X-Frame-Options, or X-Content-Type-Options.

```python
app = FastAPI(...)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(reception.router)
```

#### Validation

All application setup and root configuration files were reviewed; no alternate header-enforcement layer exists in the repository.

Validation method: static configuration review

**Application registers routers without response hardening** — `app/main.py:17-29`

No middleware or response hook adds Strict-Transport-Security, X-Frame-Options, or X-Content-Type-Options.

```python
app = FastAPI(...)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(reception.router)
```

Assertions:
- Reception HTML can be framed.
- Clients receive no application-declared HSTS or nosniff policy.

Limitations:
- An external production proxy could add these headers, but no such configuration was supplied.

#### Dataflow

HTTP request -\> FastAPI route -\> response without hardening headers

- **Source:** browser navigation

- **Sink:** browser security policy

- **Outcome:** missing clickjacking and transport defense

**Application registers routers without response hardening** — `app/main.py:17-29`

No middleware or response hook adds Strict-Transport-Security, X-Frame-Options, or X-Content-Type-Options.

```python
app = FastAPI(...)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(reception.router)
```

#### Reachability

Requires the application to be deployed without a compensating edge policy.

- **Attacker:** remote web attacker

- **Entry point:** reception HTML or any API response

- **Outcome:** weaker browser and transport protections

#### Severity

**Low** — The scan assigned low severity; no separate canonical severity rationale was recorded.

Additional runtime or deployment evidence could raise or lower this severity.

Impact assessment:
- **Level:** medium
- **Why:** Framing or downgrade-related conditions can support attacks on an authenticated clinical workflow.

Likelihood assessment:
- **Level:** low
- **Why:** Exploitability depends on browser session behavior and deployment topology not present in the repository.

#### Remediation

Add centralized middleware that sets HSTS, X-Frame-Options: DENY, and X-Content-Type-Options: nosniff on every response, with production TLS enforced at the edge.

Tests:
- Assert all representative JSON and HTML responses include the three required headers.

Preventive controls:
- Keep a single header policy in application middleware and verify equivalent edge configuration during deployment.

## Reviewed Surfaces

| Surface | Risk Area | Outcome | Notes |
| --- | --- | --- | --- |
| Human and M2M token issuance | not recorded | Reported | Unlimited attempts affect both sibling token endpoints. |
| JWT validation and identity revocation | not recorded | Reported | Signature and expiry are enforced; current active state is not. |
| FastAPI response and browser hardening | not recorded | Reported | Required security headers are absent; CORS is absent rather than permissive. |
| Appointment RBAC, scopes, and ownership | not recorded | Rejected | BOLA was present in the stage-1 baseline but current routes call centralized ownership checks; cross-professional access is tested. |
| SQL construction, Pydantic contracts, and Jinja output | not recorded | Rejected | SQLModel parameterization, extra=forbid, response models, and Jinja autoescape provide source-backed counterevidence; stricter text whitelist remains defense in depth. |

## Open Questions And Follow Up

- No production reverse-proxy or infrastructure manifest was supplied, so compensating headers and distributed rate limits could not be verified.
- An independent baseline worker was unavailable because delegation was not authorized; the audit used sequential baseline and focused passes.
