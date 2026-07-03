/**
 * useRobotControl — the dashboard's control actions (Start / Stop / Reconnect /
 * Emergency Stop). Optimistically updates the robot store + logs, and (in live mode)
 * calls the backend command endpoint.
 */
import {useMutation} from '@tanstack/react-query';
import {RobotService} from '@/services';
import {useConnectionStore, useLogStore, useRobotStore, useSettingsStore} from '@/store';
import type {LogEntry, LogLevel, RobotCommand} from '@/types';

const COMMAND_LOG: Record<RobotCommand, {level: LogLevel; message: string}> = {
  start: {level: 'SUCCESS', message: 'Robot started'},
  stop: {level: 'WARNING', message: 'Robot stopped'},
  reconnect: {level: 'INFO', message: 'Reconnecting to robot…'},
  emergency_stop: {level: 'ERROR', message: 'EMERGENCY STOP engaged'},
};

function commandLog(command: RobotCommand): LogEntry {
  const {level, message} = COMMAND_LOG[command];
  return {
    id: `cmd-${Date.now()}-${command}`,
    timestamp: Date.now(),
    level,
    source: 'operator',
    message,
  };
}

export interface RobotControl {
  start: () => void;
  stop: () => void;
  reconnect: () => void;
  emergencyStop: () => void;
  isPending: boolean;
}

export function useRobotControl(): RobotControl {
  const demoMode = useSettingsStore(s => s.settings.demoMode);
  const robotId = useSettingsStore(s => s.settings.robotId);
  const applyCommand = useRobotStore(s => s.applyCommand);

  const mutation = useMutation({
    mutationFn: (command: RobotCommand) =>
      demoMode ? Promise.resolve() : RobotService.sendCommand(robotId, command),
    onMutate: (command: RobotCommand) => {
      // Optimistic: reflect intent immediately for a responsive control feel.
      applyCommand(command);
      useLogStore.getState().append(commandLog(command));
    },
    onError: error => {
      const message = error instanceof Error ? error.message : 'Command failed';
      useConnectionStore.getState().setError(message);
      useLogStore.getState().append({
        id: `cmd-err-${Date.now()}`,
        timestamp: Date.now(),
        level: 'ERROR',
        source: 'operator',
        message: `Command failed: ${message}`,
      });
    },
  });

  const run = (command: RobotCommand) => mutation.mutate(command);

  return {
    start: () => run('start'),
    stop: () => run('stop'),
    reconnect: () => run('reconnect'),
    emergencyStop: () => run('emergency_stop'),
    isPending: mutation.isPending,
  };
}
