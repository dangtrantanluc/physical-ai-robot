# Physical AI Robot — Backend "Robot Brain"

The server-side **brain** for a physical AI robot. The robot itself is a thin client
(Android phone — Realme Q — for camera/audio/speech, plus an ESP32 for motor control).
**All AI runs on the server.** Each control tick the robot uploads a frame + audio +
telemetry and receives back a single flat command: *which behavior, what velocity, what
to say*.

Built with **Clean Architecture + Domain-Driven Design** so that today's mock detector,
rule planner and Postgres memory can each be swapped for YOLO / an LLM planner / a vector
DB **without touching business logic**.

```
┌────────────────────┐   POST /robot/step (image, audio, state, battery)   ┌────────────────────┐
│  Robot (Android +  │  ────────────────────────────────────────────────▶  │   Robot Brain      │
│  ESP32 motors)     │                                                      │   (this backend)   │
│                    │  ◀────────────────────────────────────────────────  │                    │
└────────────────────┘   { behavior, linear_velocity, angular_velocity,     └────────────────────┘
                            speech, metadata }
```

---

## Table of contents

- [Capabilities](#capabilities)
- [Architecture](#architecture)
- [The robot control loop](#the-robot-control-loop)
- [Behavior system](#behavior-system)
- [Extension points](#extension-points-swap-without-touching-business-logic)
- [Project layout](#project-layout)
- [API reference](#api-reference)
- [Configuration](#configuration)
- [Running it](#running-it)
- [Database & migrations](#database--migrations)
- [Testing](#testing)
- [Observability](#observability)
- [Roadmap](#roadmap)

---

## Capabilities

**Now**

- **Follow person** — proportional visual servoing (center + distance control).
- **Voice command** — EN/VI keywords (`follow`, `stop`, `search`, `idle` / `theo`, `dừng`…).
- **Object detection** — pluggable detector (mock heuristic today).
- **Behavior management** — registry + planner, no giant `if/else`.

**Designed for (drop-in later)** — obstacle avoidance, memory, navigation, VLM, RL policy,
multi-agent. See [Roadmap](#roadmap).

---

## Architecture

Clean Architecture with a strict **dependency rule**: outer layers depend on inner
layers, never the reverse. The domain has zero framework imports (no FastAPI, SQLAlchemy,
Redis, OpenCV, PyTorch) and is fully unit-testable.

```
         ┌───────────────────────────────────────────────────────────┐
         │                          api/                              │  HTTP / WebSocket
         │   routers · schemas · deps (DI) · middleware · errors      │  (transport only)
         └───────────────────────────┬───────────────────────────────┘
                                      │ depends on
         ┌───────────────────────────▼───────────────────────────────┐
         │                      application/                          │  use cases
         │  RobotService · Vision/Speech/Planner/Memory/Mission svc   │  (orchestration)
         └───────────────────────────┬───────────────────────────────┘
                                      │ depends on
         ┌───────────────────────────▼───────────────────────────────┐
         │                        domain/                             │  pure business core
         │  entities · value objects · PORTS (abstract interfaces)    │  (no frameworks)
         └───────────────────────────▲───────────────────────────────┘
                                      │ implements ports (Dependency Inversion)
         ┌───────────────────────────┴───────────────────────────────┐
         │                    infrastructure/                         │  adapters
         │  db (SQLAlchemy) · redis · vision · speech · planner ·      │
         │  memory · behaviors                                        │
         └────────────────────────────────────────────────────────────┘

   core/  = cross-cutting: config (pydantic-settings), logging (structlog),
            exceptions, DI container (composition root)
```

**Ports & adapters** — the domain declares interfaces; infrastructure implements them:

| Port (domain)        | Adapter today (infrastructure) | Swap to later                       |
|----------------------|--------------------------------|-------------------------------------|
| `VisionDetector`     | `MockDetector` (OpenCV)        | `YoloDetector`, RT-DETR, Grounding DINO |
| `SpeechRecognizer`   | `MockRecognizer`               | Whisper                             |
| `Planner`            | `RulePlanner`                  | `LLMPlanner`, `RLPlanner`           |
| `MemoryRepository`   | `PostgresMemoryRepository`     | ChromaDB, Qdrant                    |
| `RobotStateStore`    | `RedisRobotStateStore`         | any KV store                        |
| `Behavior`           | Idle/Follow/Search/Stop        | Avoid, Navigate, Dock, …            |

The one place that picks concrete implementations from config is the **DI container**
(`app/core/container.py`). Business logic only ever sees the ports.

---

## The robot control loop

`POST /robot/step` (and the WebSocket) run one tick through `RobotService.step()`:

```
      image, audio, state, battery
                 │
                 ▼
   ┌── load hot state (Redis) ──────────────────────────────┐
   │                                                         │
   │   ┌───────────── concurrently (asyncio.gather) ─────────┐
   │   │  VisionService.perceive(image) → Perception          │
   │   │  SpeechService.listen(audio)  → Transcript           │
   │   └──────────────────────────────────────────────────────┘
   │                 │                                        │
   │                 ▼   build RobotContext                   │
   │        PlannerService.decide(ctx) → Plan (which behavior)│
   │                 │                                        │
   │                 ▼   BehaviorManager.switch + execute     │
   │           Behavior.execute(ctx)   → BehaviorOutput (v, ω)│
   │                 │                                        │
   │                 ▼   persist: Redis (always) +            │
   │                     Postgres logs/robot/memory (sampled) │
   └─────────────────┼──────────────────────────────────────┘
                     ▼
   { behavior, linear_velocity, angular_velocity, speech, metadata }
```

**Decide vs. act** are separate concerns: the **planner** chooses *which* behavior should
be active (safety → voice command → perception-driven transitions); the **behavior**
computes *how* (the actual velocity). That is why a `RulePlanner` can later become an
`LLMPlanner` without any behavior changing, and vice-versa.

The loop is **stateless per request**: the "current behavior" lives in Redis, so any
worker can serve any robot's next tick (horizontal scale).

---

## Behavior system

No large state-machine `if/else`. Behaviors are self-contained classes registered in a
manager and selected by the planner.

```python
class Behavior(ABC):
    behavior_type: BehaviorType
    def start(self, ctx): ...          # lifecycle hook on activation
    def stop(self, ctx): ...           # lifecycle hook on deactivation
    async def update(self, ctx) -> BehaviorOutput: ...   # core control logic
    async def execute(self, ctx) -> BehaviorOutput: ...  # template: update + safety clamp

class BehaviorManager(ABC):
    def register(self, behavior): ...
    def get(self, behavior_type): ...
    def switch_behavior(self, current, target, ctx) -> Behavior: ...
    async def execute(self, behavior, ctx) -> BehaviorOutput: ...
```

`BaseBehavior.execute()` wraps every behavior with a **motion-limit safety clamp**, so no
behavior can ever command an unsafe velocity. Adding a behavior = one class + one line in
`infrastructure/behaviors/registry.py` (Open/Closed — existing behaviors untouched).

**Follow controller** — two decoupled proportional loops, resolution-independent
(normalized coordinates): steer to horizontally center the person; drive so the person's
bounding-box height matches a target ratio (a monocular distance proxy). All gains come
from config — no magic numbers.

---

## Extension points (swap without touching business logic)

**Use a real detector**

```env
VISION_DETECTOR=yolo
MODEL_PATH=/app/models/yolov8n.pt
```

Then implement `YoloDetector.detect()` (a stub already imports torch/ultralytics lazily so
startup stays fast). Nothing in `application/` or `behaviors/` changes.

**Add a behavior** (e.g. obstacle avoidance)

1. `class AvoidBehavior(BaseBehavior)` in `infrastructure/behaviors/avoid.py`.
2. Add `BehaviorType.AVOID` in `domain/value_objects/enums.py`.
3. Register it in `registry.py` and add a rule to `RulePlanner`.

**Swap the planner / memory backend** — set `PLANNER=llm` / `MEMORY_BACKEND=qdrant`, add
the adapter, wire it in the container factory. Ports keep the rest of the system stable.

---

## Project layout

```
app/
  api/               HTTP/WebSocket transport (NO business logic)
    deps.py            DI providers (Depends) — request-scoped wiring
    errors.py          global exception → house error envelope
    middleware.py      correlation-id binding
    v1/routes/         health · robot · mission · ws
  application/       use cases
    dto/               StepCommand / StepResult
    services/          Robot, Vision, Speech, Planner, Memory, Mission
  core/              config · logging · exceptions · container (composition root)
  domain/            pure business core
    entities/          Robot, Mission, Task, MemoryRecord
    value_objects/     Velocity, Perception, Transcript, RobotContext, Plan, enums
    interfaces/        PORTS: Behavior, Vision, Speech, Planner, Memory, repos, state store
  infrastructure/    adapters implementing the ports
    behaviors/         Idle, Follow, Search, Stop + manager + registry
    vision/            MockDetector (+ YoloDetector stub)
    speech/            MockRecognizer
    planner/           RulePlanner
    memory/            PostgresMemoryRepository
    redis/             RedisRobotStateStore
    database/          models, session, repositories, mappers
  schemas/           Pydantic request/response
  utils/             media decoding, timing
alembic/             async migrations env + versions
tests/               unit + api tests (fakes, no infra needed)
```

---

## API reference

Routes are mounted at root to honor the device-facing contract. Interactive docs at
`/docs` (Swagger) and `/redoc`.

| Method | Path              | Description                                   |
|--------|-------------------|-----------------------------------------------|
| GET    | `/health`         | Liveness + Redis/DB readiness (200 / 503)     |
| POST   | `/robot/step`     | One control tick → **flat** actuation command |
| GET    | `/robot/{id}`     | Robot record (enveloped)                      |
| POST   | `/mission`        | Create a mission (+ ordered tasks)            |
| GET    | `/mission/{id}`   | Read a mission                                |
| WS     | `/robot/ws`       | Streaming control loop (same semantics)       |

**`POST /robot/step`** — the robot understands *exactly* this flat body (management
endpoints use the `{success, data}` / `{success, error}` envelope; the device contract does
not, for size/latency):

```jsonc
// request
{ "robot_id": "realme-q-01", "image": "<base64>", "audio": "<base64>", "battery": 82.5 }

// response
{
  "behavior": "follow",
  "linear_velocity": -0.18,      // m/s
  "angular_velocity": -0.38,     // rad/s (+ = left / CCW)
  "speech": "Okay, following you.",
  "metadata": { "reason": "voice_command", "detections": {"person": 1},
                "inference_ms": 3.5, "latency_ms": 12.4, "fps": 80.1 }
}
```

> **Mock conventions for local testing**: `MockDetector` reports the largest bright blob as
> a `person`; `MockRecognizer` treats the `audio` bytes as UTF-8 text, so
> `audio = base64("follow me")` issues a voice command. Both are swapped for real models via
> config.

Every response carries an `x-correlation-id` header; send your own to trace FE→BE→DB.

---

## Configuration

All settings live in `app/core/config.py` (pydantic-settings); override via env or `.env`
(see `.env.example`). Nested groups use `__`, e.g. `MOTION__MAX_LINEAR_SPEED=0.6`.

Key knobs: `DATABASE_URL`, `REDIS_URL`, `VISION_DETECTOR`, `SPEECH_RECOGNIZER`, `PLANNER`,
`MEMORY_BACKEND`, `MODEL_PATH`, `ROBOT_FPS`, motion limits, follow gains, battery
guardrails, `LOG_JSON`, `LOG_SAMPLE_N` (durable-write sampling).

---

## Running it

**Docker Compose (Postgres + Redis + API, migrations auto-applied):**

```bash
cp .env.example .env
docker compose up --build
# API on http://localhost:8000 — GET http://localhost:8000/health
```

**Local dev:**

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt          # or: make dev
# point DATABASE_URL / REDIS_URL at local services, then:
make migrate                                  # alembic upgrade head
make run                                       # uvicorn --reload
```

> **PyTorch**: pinned in `requirements.txt` and resolves to the CPU wheel
> (`torch==2.5.1+cpu`) on Linux via the official index. It is **not imported at startup** —
> only lazily by real detectors — so the service boots on the mock stack instantly. For a
> lighter dev image you may omit it and install `pip install -e ".[ml]"` when wiring a real
> model.

---

## Database & migrations

PostgreSQL tables: `robots`, `missions`, `tasks`, `logs`, `settings`, `memories`.
Redis holds hot per-robot state (current behavior, mission, last-frame metadata, step
counter) with a TTL.

```bash
make migrate                      # apply
alembic revision --autogenerate -m "add X"   # new migration (models drive schema)
alembic downgrade -1              # roll back
```

Async Alembic env (`alembic/env.py`) reads the URL from settings. The initial migration is
verified to match the ORM models exactly (`alembic check` → no drift).

---

## Testing

```bash
make test        # pytest — 33 tests, no Postgres/Redis required (in-memory fakes)
make lint        # ruff
make typecheck   # mypy
```

Coverage spans domain value objects, the rule planner's decision table, every behavior +
the follow control law, the mock detector/media decoding, a full `RobotService.step`
integration (fakes), and API routing incl. the flat contract and error envelope. The clean
seams (ports + constructor injection) are what make this fast to test.

---

## Observability

Structured logging via **structlog** (JSON in staging/prod, console in dev). A
correlation id is bound per request and echoed as `x-correlation-id`. The control loop logs
exactly the spec's metrics: `robot_id`, `behavior`, `latency_ms`, `inference_ms`, `fps`,
plus velocities and `reason`. Durable telemetry rows are written to `logs` (sampled via
`LOG_SAMPLE_N` to keep the hot loop off the DB at high FPS).

---

## Roadmap

| Capability          | How it slots in                                                        |
|---------------------|------------------------------------------------------------------------|
| Obstacle avoidance  | `AvoidBehavior` + planner safety rule (depth/US sensor in `RobotContext`) |
| Memory              | `MemoryRepository` already recorded per interaction; add recall to planner |
| Navigation          | `NavigateBehavior` + mission tasks (waypoints) already modelled          |
| VLM                 | new `VisionDetector`/scene-describer port; planner consumes captions     |
| RL policy           | `RLPlanner` implements `Planner`; behaviors stay the actuation layer     |
| Multi-agent         | per-robot hot state is already isolated; add a coordinator service       |

---

Built as a modular foundation: start on mocks, ship real models one adapter at a time.
