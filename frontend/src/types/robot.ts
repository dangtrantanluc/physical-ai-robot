/**
 * Robot domain types. The backend-facing shapes (RobotRead, StepResponse,
 * HealthResponse) mirror the FastAPI contract exactly; the dashboard aggregates
 * them (plus robot-reported hardware status) into RobotTelemetry.
 */

/** Behaviors the brain can switch between (matches backend BehaviorType). */
export type BehaviorType = 'idle' | 'follow' | 'search' | 'stop';

/** High-level running state shown on the dashboard. */
export type RobotRunState = 'offline' | 'idle' | 'running' | 'error' | 'estopped';

/** Status of a single monitored component. */
export type ComponentStatus = 'online' | 'offline' | 'connecting' | 'error';

/** Which subsystems the dashboard shows as StatusCards. */
export type ComponentKey = 'server' | 'esp32' | 'camera' | 'microphone';

/** GET /robot/{id} — durable robot record. */
export interface RobotRead {
  id: string;
  name: string;
  status: string;
  battery: number | null;
  current_behavior: BehaviorType;
  current_mission_id: string | null;
  last_seen_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

/** POST /robot/step — request body. */
export interface StepRequest {
  robot_id: string;
  image?: string | null;
  audio?: string | null;
  state?: string | null;
  battery?: number | null;
}

/** POST /robot/step — flat actuation command the robot applies. */
export interface StepResponse {
  behavior: BehaviorType;
  linear_velocity: number;
  angular_velocity: number;
  speech: string | null;
  metadata: Record<string, unknown>;
}

/** A control action an operator can trigger from the dashboard. */
export type RobotCommand = 'start' | 'stop' | 'reconnect' | 'emergency_stop';

export interface VelocityCommand {
  linear: number;
  angular: number;
}

export interface Mission {
  id: string;
  name: string;
  goal: string;
  status: 'pending' | 'active' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0..1
}

/** Everything the dashboard renders for one robot at one instant. */
export interface RobotTelemetry {
  robotId: string;
  robotName: string;
  runState: RobotRunState;
  behavior: BehaviorType;
  state: string;
  battery: number; // 0..100
  latencyMs: number;
  fps: number;
  mission: Mission | null;
  lastCommand: VelocityCommand;
  updatedAt: number; // epoch ms
}
