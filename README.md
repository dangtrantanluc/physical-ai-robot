# Physical AI Robot

A physical AI robot system split into two independently developed apps.

```
physical-ai-robot/
├── backend/     FastAPI "Robot Brain" — all AI runs here (vision, speech, planner, behaviors)
└── frontend/    React Native controller — engineering dashboard to monitor & control the robot
```

The robot itself is a thin client: an Android phone (Realme Q) for camera/audio and an ESP32
for motors. Each control tick the robot uploads a frame + audio + telemetry to the backend and
receives back a command (behavior + velocity + speech). The **frontend** is a separate operator
tool used to watch the robot's live status and drive it.

---

## backend/ — Robot Brain (Python)

FastAPI · Clean Architecture + DDD · async SQLAlchemy · Redis · OpenCV · PyTorch-ready.

```bash
cd backend
cp .env.example .env
docker compose up --build      # API on http://localhost:8000  (GET /health)
```

See [backend/README.md](backend/README.md) for architecture, API reference and extension points.

Key endpoints the frontend talks to: `GET /health`, `POST /robot/step`, `GET /robot/{id}`,
`POST /mission`, `WS /robot/ws`.

---

## frontend/ — Robot Controller (React Native)

React Native CLI · TypeScript · React Navigation · React Native Paper · React Query · Zustand ·
Axios · Vision Camera · MMKV · Reanimated · SVG. A dark, industrial monitoring dashboard.

```bash
cd frontend
npm install
npm run start           # Metro
npm run android         # or: npm run ios (macOS)
```

Runs on **mock data by default** so the UI is fully populated without a running backend; point it
at the real server in Settings (or `DEFAULT_SERVER_URL`). See [frontend/README.md](frontend/README.md).
