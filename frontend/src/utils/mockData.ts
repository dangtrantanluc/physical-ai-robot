/**
 * Mock data generators. The app ships with demoMode ON so every screen is fully
 * populated without a running backend. Generators evolve values slightly over time
 * to look "live" (battery drains, fps/latency jitter, velocities wander).
 */
import type {
  BehaviorType,
  BoundingBox,
  CameraOverlayInfo,
  ComponentKey,
  ComponentStatus,
  LogEntry,
  LogLevel,
  Mission,
  RobotTelemetry,
} from '@/types';
import {clamp, round} from './format';

const BEHAVIORS: BehaviorType[] = ['idle', 'follow', 'search', 'stop'];
const STATES = ['tracking', 'scanning', 'holding', 'navigating', 'braking'];

const randIn = (min: number, max: number) => min + Math.random() * (max - min);
const pick = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

export const mockMission = (): Mission => ({
  id: 'mission-042',
  name: 'Warehouse Perimeter Patrol',
  goal: 'Follow the night-shift operator along the perimeter route.',
  status: 'active',
  progress: 0.62,
});

export function initialTelemetry(robotId: string, robotName: string): RobotTelemetry {
  return {
    robotId,
    robotName,
    runState: 'running',
    behavior: 'follow',
    state: 'tracking',
    battery: 82,
    latencyMs: 38,
    fps: 24,
    mission: mockMission(),
    lastCommand: {linear: 0.18, angular: -0.32},
    updatedAt: Date.now(),
  };
}

/** Produce the next telemetry frame from the previous one (a gentle random walk). */
export function nextTelemetry(prev: RobotTelemetry): RobotTelemetry {
  const running = prev.runState === 'running';
  const behavior = Math.random() < 0.08 ? pick(BEHAVIORS) : prev.behavior;
  return {
    ...prev,
    behavior: running ? behavior : 'stop',
    state: running ? (Math.random() < 0.1 ? pick(STATES) : prev.state) : 'holding',
    battery: clamp(prev.battery - randIn(0, 0.15), 0, 100),
    latencyMs: round(clamp(prev.latencyMs + randIn(-6, 6), 12, 140), 0),
    fps: round(clamp(prev.fps + randIn(-2, 2), 8, 30), 1),
    lastCommand: running
      ? {
          linear: round(clamp(prev.lastCommand.linear + randIn(-0.05, 0.05), -0.6, 0.6), 3),
          angular: round(clamp(prev.lastCommand.angular + randIn(-0.1, 0.1), -1.5, 1.5), 3),
        }
      : {linear: 0, angular: 0},
    updatedAt: Date.now(),
  };
}

export const mockComponentStatuses = (): Record<ComponentKey, ComponentStatus> => ({
  server: 'online',
  esp32: 'online',
  camera: 'online',
  microphone: 'connecting',
});

const LOG_TEMPLATES: Array<{level: LogLevel; source: string; message: string}> = [
  {level: 'INFO', source: 'planner', message: 'Behavior switch idle → follow (voice_command)'},
  {level: 'SUCCESS', source: 'vision', message: 'Person acquired (confidence 0.83)'},
  {level: 'INFO', source: 'esp32', message: 'Motor command applied: v=0.18 ω=-0.32'},
  {level: 'WARNING', source: 'battery', message: 'Battery at 24% — approaching low threshold'},
  {level: 'ERROR', source: 'camera', message: 'Frame upload timed out, retrying (1/3)'},
  {level: 'INFO', source: 'speech', message: 'Transcript: "follow me"'},
  {level: 'SUCCESS', source: 'server', message: 'Health check OK (redis, database)'},
  {level: 'WARNING', source: 'planner', message: 'Person lost — switching to search'},
  {level: 'INFO', source: 'mission', message: 'Waypoint 4/8 reached'},
  {level: 'ERROR', source: 'esp32', message: 'Bluetooth link dropped, reconnecting'},
];

let logSeq = 0;
export function makeLogEntry(at = Date.now()): LogEntry {
  const t = pick(LOG_TEMPLATES);
  logSeq += 1;
  return {id: `log-${at}-${logSeq}`, timestamp: at, level: t.level, source: t.source, message: t.message};
}

export function seedLogs(count = 40): LogEntry[] {
  const now = Date.now();
  return Array.from({length: count}, (_, i) => makeLogEntry(now - (count - i) * 3200)).reverse();
}

const DETECTION_LABELS = ['person', 'chair', 'door', 'box'];

export function mockCameraOverlay(fps: number): CameraOverlayInfo {
  const boxes: BoundingBox[] = Array.from({length: Math.floor(randIn(1, 4))}, (_, i) => ({
    id: `box-${i}`,
    label: pick(DETECTION_LABELS),
    confidence: round(randIn(0.55, 0.95), 2),
    x: round(randIn(0.1, 0.6), 3),
    y: round(randIn(0.1, 0.5), 3),
    width: round(randIn(0.15, 0.3), 3),
    height: round(randIn(0.25, 0.4), 3),
  }));
  return {
    fps: round(fps, 1),
    resolution: '1280x720',
    uploadStatus: Math.random() < 0.9 ? 'ok' : 'uploading',
    detectionCount: boxes.length,
    boxes,
  };
}
