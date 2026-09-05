# KhetSetu Developer & AI Agent Guidelines (AGENTS.md)

## 1. Project Mission & Context
- **Project**: KhetSetu — Direct-to-Consumer & B2B Digital Marketplace for Farmers & FPOs.
- **Context**: Smart India Hackathon (SIH 2026) — Problem Statement ID 26033.
- **Problem Statement**: *Multiple intermediaries reduce farmers’ earnings and increase consumer prices.*
- **Theme**: Agriculture, FoodTech & Rural Development.
- **Core Objective**: Eliminate intermediaries through direct produce listing, transparent dynamic price discovery with resilient fallback, pooled cold-chain delivery route optimization, an escrow-protected transaction cycle, and vernacular/voice accessibility for low-literacy farmers.

---

## 2. Architectural Rules & Discipline
1. **Single Backend Service**:
   - Built exclusively with **FastAPI** (`Python 3.11+`).
   - Native WebSockets (`FastAPI.websocket`) handle real-time driver telemetry, order events, and notifications.
   - No standalone Node.js/Socket.io microservice.
2. **PostgreSQL JSONB Over Speculative NoSQL**:
   - Relational data (users, auth, orders, escrow ledger, routes) resides in PostgreSQL 16.
   - Dynamic produce attributes, harvest specifications, and seasonal grading parameters are stored in PostgreSQL **`JSONB`** columns with GIN indexes.
   - No separate MongoDB instance.
3. **Zero Speculative Provisioning**:
   - Do **NOT** introduce Redis until caching, distributed pub-sub, or rate-limiting thresholds strictly demand it.
   - In-memory state and PostgreSQL queries suffice for initial phases.
4. **Resilient Mandi Price Discovery ("Never Fail Silently")**:
   - The Mandi Price Engine connects to live/market price feeds (e.g., Agmarknet/eNAM APIs).
   - If an external feed times out, returns HTTP 5xx, or serves malformed data, the engine **MUST NOT** return a 500 error or silent null.
   - It **MUST** fall back to indexed historical crop averages, apply an explicit confidence score/flag (`is_fallback=True`), and log a structured warning.
5. **Rigid Escrow State Machine**:
   - Order status transitions must follow a strict finite-state machine:
     ```
     INITIATED ──> IN_ESCROW ──> DISPATCHED ──> DELIVERED_VERIFIED ──> RELEASED
         │             │
         ▼             ▼
     CANCELLED      REFUNDED / DISPUTED
     ```
   - Direct illegal transitions (e.g., `INITIATED` directly to `RELEASED`) must be rejected with domain-specific exceptions (HTTP 400/409).
   - State mutations must occur within atomic database transactions with concurrency checks.
6. **Hosted Routing for Prototype**:
   - Use hosted routing APIs (public OSRM, OpenRouteService, or client adapter mocks) rather than hosting a local heavy OSRM server.
   - The Vehicle Routing Problem (VRP) solver (Google OR-Tools) operates on pooled orders created in the database.

---

## 3. Strict Phased Implementation Sequence
All implementation work must proceed in this precise order:

### Phase 1: Database Schema, Alembic Migrations & Schema-Constraint Tests (TDD RED First)
- Define declarative SQLAlchemy 2.0 models for:
  - `User` (roles: `FARMER`, `FPO`, `BUYER`, `ADMIN`, `LOGISTICS_PARTNER`)
  - `Produce` (pricing, quantity, unit, harvest date, location, attributes via `JSONB`)
  - `MandiPriceHistory` (crop, mandi name, state, modal price, date)
  - `Order` & `EscrowTransaction` (order state enum, amounts, escrow status)
  - `DeliveryRoute` & `LogisticsHub` (stops, vehicle capacity, assigned orders)
- **TDD RED step**: Write tests verifying constraints (foreign keys, non-negative quantities/prices, valid state enums, non-null fields, JSONB schema validation) before applying migrations.
- Set up Alembic migrations and apply to the database.
- Verify tests turn **GREEN**.

### Phase 2a: Produce Listing Engine (Plain CRUD)
- Implement isolated CRUD endpoints for produce listing (`POST`, `GET`, `PUT`, `DELETE`, search/filter by crop, location, harvest window).
- Pydantic v2 schemas for request validation and response serialization.
- Pure CRUD with **no external price feed dependency**.
- Strict TDD (`tdd-workflows-tdd-red` / `tdd-workflows-tdd-green`) and `fastapi-pro` patterns.

### Phase 2b: Mandi Price Engine & Resilient Fallback
- Ingestion client for live mandi rates.
- Historical mandi price store and regional aggregation logic.
- Implement and test-drive the **fallback-to-historical-average** mechanism using `tdd-workflows-tdd-cycle` and `error-handling-patterns`.
- Validate that network outages, timeouts, and API errors gracefully return fallback estimates with transparency.

### Phase 3: Order Lifecycle & Escrow State Machine
- Implement the order placement and escrow lock flow.
- Enforce transactional state transitions: `INITIATED` → `IN_ESCROW` → `DISPATCHED` → `DELIVERED_VERIFIED` → `RELEASED`.
- Implement payment webhook handlers and escrow release simulation.
- Test-driven validation covering unauthorized transitions, double-release prevention, and cancellation refunds.

### Phase 4: Route Optimization Engine (Google OR-Tools VRP)
- Consume active orders in `IN_ESCROW` / ready for pickup.
- Implement capacity-constrained, time-windowed vehicle routing (CVRP/VRPTW) using Google OR-Tools.
- Integrate with hosted routing service for real distance and travel time matrices.
- Provide pooled delivery route suggestions to cut transit time and perishable spoilage.

### Phase 5: Real-Time Updates (FastAPI Native WebSockets)
- Native WebSocket endpoints for live order state notifications and driver tracking.
- In-memory connection manager tracking active client connections per user/order.

### Phase 6: Web & Mobile Frontends
- **Web Portal** (`apps/web`): React 18 + Vite + Tailwind CSS for FPOs, bulk buyers, and administrative management.
- **Mobile App** (`apps/mobile`): React Native / Expo SDK 57 with offline SQLite/AsyncStorage queuing and vernacular voice support for farmers.

---

## 4. TDD & Code Quality Discipline
- **RED Phase**: Write failing unit or contract tests first. Failures must fail for the right reason (missing implementation, not syntax or fixture errors).
- **GREEN Phase**: Write only the minimal code necessary to make the tests pass.
- **REFACTOR Phase**: Clean up duplication, enforce PEP 8 / clean code principles, and ensure all tests stay green.
- **Coverage**: Minimum 85% branch coverage on order state transitions, escrow logic, and price fallback handling.
- **Isolation**: Unit tests must not depend on live external networks; mock external HTTP calls with `pytest-mock` or `httpx` transport mocks.

---

## 5. Technology Stack & Exact Versions
- **Runtime**: Python `3.11.9`, Node.js `v22.16.0`
- **Backend**: FastAPI `^0.115.0`, Pydantic `^2.9.0`, SQLAlchemy `^2.0.35`, asyncpg `^0.29.0`, Alembic `^1.13.0`
- **Database**: PostgreSQL `16.x` (relational data + `JSONB`)
- **Optimization & ML**: Google OR-Tools `^9.10.0`, scikit-learn `^1.5.0`, Prophet `^1.1.5`
- **Frontend**: React `^18.3.1`, Vite `^5.4.0`, Tailwind CSS `^3.4.10`, Lucide React `^0.440.0`
- **Mobile**: React Native / Expo SDK `^57.0.0`

---

## 6. Code Style & Conventions
- **Python**:
  - Adhere to PEP 8 using `ruff` and `black`.
  - Use modern type annotations (`typing` / Python 3.10+ union types `X | Y`).
  - Use `async/await` across all database and external I/O interactions.
  - Pydantic models must use `model_config = ConfigDict(from_attributes=True)`.
- **TypeScript / React**:
  - `strict: true` in `tsconfig.json`.
  - Prefer functional components and custom hooks.
  - Tailored Tailwind utility classes; avoid unstructured CSS.
- **Git Commit Protocol**:
  - Follow Conventional Commits: `feat(scope): message`, `fix(scope): message`, `test(scope): message`, `docs: message`.

---

## 7. Security & Environmental Configuration
- No credentials, secrets, or API keys in source control.
- Configuration loaded strictly via Pydantic `BaseSettings` reading from `.env`.
- Sensitive data (farmer banking details, phone numbers, exact geolocations) must be treated as protected PII.
