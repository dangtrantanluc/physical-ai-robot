/**
 * robotStore — the live robot model rendered by the dashboard (behavior, state,
 * battery, latency, fps, mission, last velocity command) plus the operator-driven
 * run state. Telemetry hooks push frames in; control actions mutate the run state.
 */
import {create} from 'zustand';
import type {RobotCommand, RobotRunState, RobotTelemetry} from '@/types';
import {initialTelemetry} from '@/utils';
import {DEFAULT_SETTINGS} from '@/utils/constants';

interface RobotState {
  telemetry: RobotTelemetry;
  /** Set the full telemetry frame (from a poll / mock tick). */
  setTelemetry: (telemetry: RobotTelemetry) => void;
  /** Merge a partial telemetry update. */
  patchTelemetry: (patch: Partial<RobotTelemetry>) => void;
  setRunState: (runState: RobotRunState) => void;
  /** Apply an operator command's effect on run state (optimistic). */
  applyCommand: (command: RobotCommand) => void;
}

const runStateForCommand: Record<RobotCommand, RobotRunState> = {
  start: 'running',
  stop: 'idle',
  reconnect: 'idle',
  emergency_stop: 'estopped',
};

export const useRobotStore = create<RobotState>(set => ({
  telemetry: initialTelemetry(DEFAULT_SETTINGS.robotId, DEFAULT_SETTINGS.robotName),
  setTelemetry: telemetry => set({telemetry}),
  patchTelemetry: patch => set(state => ({telemetry: {...state.telemetry, ...patch}})),
  setRunState: runState => set(state => ({telemetry: {...state.telemetry, runState}})),
  applyCommand: command =>
    set(state => {
      const runState = runStateForCommand[command];
      const estop = command === 'emergency_stop';
      return {
        telemetry: {
          ...state.telemetry,
          runState,
          behavior: estop || command === 'stop' ? 'stop' : state.telemetry.behavior,
          lastCommand: estop ? {linear: 0, angular: 0} : state.telemetry.lastCommand,
        },
      };
    }),
}));
