# EazyInvest

EazyInvest is a deterministic portfolio-planning app with a React/Vite frontend and a FastAPI backend.

It is built around four product tabs:

1. `Dashboard`
2. `My Holdings`
3. `Scenario Planner`
4. `Audit Layer`

The system does **not** use live market APIs. Pricing, lookup, and market context come from the backend CSV proxy dataset.

## What This Repo Does

- Uses a syndicated CSV dataset for supported symbols and proxy prices
- Stores only user profile and user-added holdings
- Computes valuation and portfolio math in backend services
- Uses rule-based agents to classify, route, explain, and validate
- Returns request audit traces and recommendation audit results in API responses
- Keeps audit data in memory / API payloads only for MVP

## Repo Layout

```text
EazyInvest/
  backend/
    app/
      api/routes/
      agents/
      audit/
      config/
      data/
      db/
      models/
      schemas/
      services/
      utils/
  frontend/
    src/
      components/
      pages/
      services/
      state/
      types/
```

## How To Run

Open two terminals.

### Backend

```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If you use the local virtual environment instead:

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### Open

- Frontend app: `http://127.0.0.1:5173`
- Backend docs: `http://127.0.0.1:8000/docs`
- Backend health: `http://127.0.0.1:8000/health`

Note:
- `http://127.0.0.1:8000/` returns backend JSON. That is normal.
- The actual UI runs on `http://127.0.0.1:5173`.

## Test / Build

### Backend tests

```powershell
cd backend
py -m pytest -q
```

### Frontend build

```powershell
cd frontend
npm run build
```

## Core Product Rules

- Product name is `EazyInvest`
- Exactly 4 top-level tabs
- No live pricing APIs
- No `yfinance`
- No Marketstack
- CSV-backed market proxy pricing only
- Deterministic backend math only
- Agents do not invent returns or arithmetic
- Audit validates recommendation output but does not create recommendations

## Backend Architecture

### 1. Data layer

- CSV pricing dataset: [backend/app/data/syndicated_prices.csv](backend/app/data/syndicated_prices.csv)
- Loader/search service: [backend/app/services/syndicated_data_service.py](backend/app/services/syndicated_data_service.py)
- Compatibility lookup wrapper: [backend/app/services/market_dataset_service.py](backend/app/services/market_dataset_service.py)

### 2. Persistence

- DB config: [backend/app/db/database.py](backend/app/db/database.py)
- Models: [backend/app/models/models.py](backend/app/models/models.py)
- Stored entities:
  - `User`
  - `Holding`

### 3. Deterministic valuation + portfolio math

- Holding enrichment and pricing: [backend/app/services/valuation_service.py](backend/app/services/valuation_service.py)
- Portfolio math helpers: [backend/app/services/portfolio_math_service.py](backend/app/services/portfolio_math_service.py)
- Portfolio summary builder: [backend/app/services/portfolio_service.py](backend/app/services/portfolio_service.py)

### 4. Agents

- Profiler: [backend/app/agents/profiler_agent.py](backend/app/agents/profiler_agent.py)
- Scenario routing: [backend/app/agents/scenario_agent.py](backend/app/agents/scenario_agent.py)
- Market context: [backend/app/agents/market_context_agent.py](backend/app/agents/market_context_agent.py)
- Rebalancing: [backend/app/agents/rebalancing_agent.py](backend/app/agents/rebalancing_agent.py)
- Transparency: [backend/app/agents/transparency_agent.py](backend/app/agents/transparency_agent.py)

### 5. Scenario orchestration

- Request orchestration: [backend/app/services/scenario_service.py](backend/app/services/scenario_service.py)
- Deterministic scenario engine: [backend/app/services/scenario_engine_service.py](backend/app/services/scenario_engine_service.py)

### 6. Audit

- Request audit helpers: [backend/app/services/audit_service.py](backend/app/services/audit_service.py)
- Basic request/source guardrails: [backend/app/services/audit_guardrail_agent.py](backend/app/services/audit_guardrail_agent.py)
- Recommendation audit package: [backend/app/audit](backend/app/audit)

## API Surface

### User / onboarding

- `GET /users/profile`
- `POST /users/onboarding`
- `PUT /users/profile`

### Holdings

- `GET /holdings/`
- `GET /holdings/lookup?q=...`
- `POST /holdings/`
- `PUT /holdings/{id}`
- `DELETE /holdings/{id}`

### Portfolio

- `GET /portfolio/summary`

### Scenarios

- `GET /scenarios/`
- `POST /scenarios/analyze`

### Audit

- `POST /audit/evaluate`
- `GET /audit/demo-results`
- `GET /audit/demo-logs`

## Frontend Architecture

### Shell and routing

- App shell: [frontend/src/App.tsx](frontend/src/App.tsx)
- Top nav: [frontend/src/components/Navbar.tsx](frontend/src/components/Navbar.tsx)

Routes:

- `/dashboard`
- `/holdings`
- `/scenarios`
- `/audit`
- `/onboarding`

### API client

- Shared client: [frontend/src/services/api.ts](frontend/src/services/api.ts)

This is the main backend/frontend connection point.

Every page calls the API client, not `fetch` directly.

### State

- Audit session store: [frontend/src/state/auditStore.tsx](frontend/src/state/auditStore.tsx)

### Pages

- Dashboard: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx)
- Holdings: [frontend/src/pages/Holdings.tsx](frontend/src/pages/Holdings.tsx)
- Scenario Planner: [frontend/src/pages/ScenarioPlanner.tsx](frontend/src/pages/ScenarioPlanner.tsx)
- Audit Layer: [frontend/src/pages/AuditLayer.tsx](frontend/src/pages/AuditLayer.tsx)

## End-to-End Flow By Tab

### Dashboard flow

1. Frontend page loads: [frontend/src/pages/Dashboard.tsx](frontend/src/pages/Dashboard.tsx)
2. Calls `api.getPortfolioSummary()`
3. API client requests `GET /api/portfolio/summary`
4. FastAPI route: [backend/app/api/routes/portfolio.py](backend/app/api/routes/portfolio.py)
5. Backend flow:
   - load user + holdings
   - enrich holdings with valuation service
   - build centralized portfolio summary
   - build market context
   - build profiler summary
   - append request audit
6. Frontend renders cards, bars, tables, and profile context

### My Holdings flow

1. Frontend page: [frontend/src/pages/Holdings.tsx](frontend/src/pages/Holdings.tsx)
2. Calls:
   - `api.getHoldings()`
   - `api.lookupSymbols(query)`
   - `api.addHolding(...)`
   - `api.updateHolding(...)`
   - `api.deleteHolding(...)`
3. Backend route: [backend/app/api/routes/holdings.py](backend/app/api/routes/holdings.py)
4. Backend flow:
   - store only user-added holdings
   - enrich holdings through valuation service
   - return `current_price/current_value` for known CSV symbols
   - return `estimated_value` for unknown symbols
5. Frontend shows only owned holdings, never the full CSV universe

### Scenario Planner flow

1. Frontend page: [frontend/src/pages/ScenarioPlanner.tsx](frontend/src/pages/ScenarioPlanner.tsx)
2. Calls:
   - `api.listScenarios()`
   - `api.analyzeScenario(...)`
3. Backend route: [backend/app/api/routes/scenarios.py](backend/app/api/routes/scenarios.py)
4. Backend orchestration:
   - profiler output
   - scenario classification / routing
   - deterministic scenario engine math
   - allocation comparison vs dense target profile
   - transparency explanation
   - recommendation audit result
5. Frontend renders:
   - suggested cards
   - custom text
   - profiler summary
   - rebalancing actions
   - transparency panel
   - compact trust check

### Audit Layer flow

1. Frontend page: [frontend/src/pages/AuditLayer.tsx](frontend/src/pages/AuditLayer.tsx)
2. Reads:
   - request audits from `auditStore`
   - recommendation review results from `auditStore`
   - demo audit packets from audit endpoints
3. Backend routes:
   - [backend/app/api/routes/audit.py](backend/app/api/routes/audit.py)
4. Frontend renders:
   - KPI cards
   - control matrix
   - recent reviews
   - evidence packet
   - exceptions
   - request traces

## Key Response Contracts

### `GET /portfolio/summary`

Returns:

- `portfolio`
- `market_context`
- `profiler`
- `audit`

### `GET /holdings/`

Returns:

- `holdings`
- `audit`

### `POST /scenarios/analyze`

Returns:

- `scenario`
  - `profiler_output`
  - `current_allocation`
  - `proposed_allocation`
  - `actions`
  - `transparency`
  - `market_context`
  - `audit_result`
- `audit`

## How Deterministic Valuation Works

For each holding:

- `avg_cost` = user-entered purchase price
- `cost_basis` = `quantity * avg_cost`
- `current_price` = CSV `latest_price` if symbol exists
- `current_value` = `current_price * quantity` if symbol exists
- `estimated_value` = `avg_cost * quantity` if symbol is missing

There is no silent fallback price like `50`.

## How Audit Is Split

There are two distinct audit layers:

### Request audit

This is the lightweight API trace returned as `audit` in most responses.

It includes:

- feature
- request id
- agents touched
- checks
- events
- data sources

### Recommendation audit

This is the deeper validation result returned as `scenario.audit_result`.

It evaluates controls like:

- explanation presence
- cost disclosure
- tax caution
- allocation validity
- evidence completeness
- target profile selection
- unsupported guarantee language
- alignment with target profile

## If You Need To Extend The App

### Add a new portfolio metric

1. Compute it in backend summary services
2. Add it to backend schema
3. Add it to frontend `types`
4. Render it in a page/component

Do not calculate it independently in the frontend.

### Add a new scenario

1. Add catalog entry in [backend/app/utils/defaults.py](backend/app/utils/defaults.py)
2. Add classification/routing support in [backend/app/agents/scenario_agent.py](backend/app/agents/scenario_agent.py)
3. Add deterministic handler in [backend/app/services/scenario_engine_service.py](backend/app/services/scenario_engine_service.py)
4. If needed, update transparency text and audit expectations
5. Frontend will pick up the new card from `GET /scenarios/`

### Add a new audit control

1. Add evidence extraction in [backend/app/audit/audit_evidence_agent.py](backend/app/audit/audit_evidence_agent.py)
2. Add the control rule in [backend/app/audit/audit_rules.py](backend/app/audit/audit_rules.py)
3. Verify it appears through `/audit/demo-results` or scenario responses

## Quick Sanity Checklist

- Backend starts and `/health` returns `ok`
- Frontend dev server loads
- Onboarding redirects to `/dashboard`
- Holdings lookup works from CSV
- Dashboard updates after adding holdings
- Scenario Planner returns actions and `audit_result`
- Audit Layer shows demo packets plus session traces

## Current Recommended Dev Loop

1. Start backend
2. Start frontend
3. Complete onboarding
4. Add holdings in `My Holdings`
5. Check `Dashboard`
6. Run suggested and custom scenarios
7. Open `Audit Layer`
8. Run backend tests and frontend build before finishing
