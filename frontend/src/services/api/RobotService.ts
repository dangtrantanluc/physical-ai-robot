/** RobotService — talks to the backend's robot endpoints. */
import type {RobotCommand, RobotRead, StepRequest, StepResponse} from '@/types';
import {http} from './client';

/** Backend management endpoints wrap payloads in this envelope. */
interface Envelope<T> {
  success: boolean;
  data: T;
  meta?: unknown;
}

export const RobotService = {
  /** GET /robot/{id} — unwraps the {success, data} envelope. */
  getRobot(robotId: string): Promise<RobotRead> {
    return http.get<Envelope<RobotRead>>(`/robot/${robotId}`).then(e => e.data);
  },

  /** POST /robot/step — one control tick; returns the flat actuation command. */
  step(payload: StepRequest): Promise<StepResponse> {
    return http.post<StepResponse>('/robot/step', payload);
  },

  /**
   * Operator control action (Start / Stop / Reconnect / Emergency Stop).
   *
   * NOTE: the backend control endpoint is not implemented yet; this targets the
   * intended `POST /robot/{id}/command` contract. In demo mode the store applies the
   * action optimistically and this call is skipped.
   */
  sendCommand(robotId: string, command: RobotCommand): Promise<void> {
    return http.post<void>(`/robot/${robotId}/command`, {command});
  },
};
