/**
 * useTelemetryEngine — the single source that keeps the stores "live".
 *
 * Mounted once at the app root (see App.tsx). In DEMO mode it drives an interval that
 * evolves robot telemetry, streams log entries and sets peripheral statuses. In LIVE
 * mode it polls GET /robot/{id} via React Query and maps the record into the stores.
 * Health/server status is owned by useHealth().
 */
import {useCallback, useEffect} from 'react';
import {useQuery} from '@tanstack/react-query';
import {RobotService} from '@/services';
import {useConnectionStore, useLogStore, useRobotStore, useSettingsStore} from '@/store';
import {POLL, QUERY, makeLogEntry, mockComponentStatuses, nextTelemetry} from '@/utils';
import {useHealth} from './useHealth';
import {useInterval} from './useInterval';

export function useTelemetryEngine(): void {
  const demoMode = useSettingsStore(s => s.settings.demoMode);
  const robotId = useSettingsStore(s => s.settings.robotId);
  const robotName = useSettingsStore(s => s.settings.robotName);

  // Owns the server/health status.
  useHealth();

  // Keep robot identity in telemetry in sync with settings.
  useEffect(() => {
    useRobotStore.getState().patchTelemetry({robotId, robotName});
  }, [robotId, robotName]);

  // ---- DEMO stream ----
  const demoTick = useCallback(() => {
    const robot = useRobotStore.getState();
    robot.setTelemetry(nextTelemetry(robot.telemetry));
    useConnectionStore.getState().setStatuses(mockComponentStatuses());
    if (Math.random() < 0.5) {
      useLogStore.getState().append(makeLogEntry());
    }
  }, []);
  useInterval(demoTick, demoMode ? POLL.telemetry : null);

  // ---- LIVE stream ----
  const robotQuery = useQuery({
    queryKey: ['robot', robotId],
    queryFn: () => RobotService.getRobot(robotId),
    enabled: !demoMode,
    refetchInterval: POLL.telemetry,
    retry: QUERY.retry,
    staleTime: QUERY.staleTime,
  });

  useEffect(() => {
    if (demoMode || !robotQuery.isSuccess) return;
    const r = robotQuery.data;
    const prev = useRobotStore.getState().telemetry;
    useRobotStore.getState().setTelemetry({
      ...prev,
      robotId: r.id,
      robotName: r.name,
      runState: r.status === 'online' ? 'idle' : 'offline',
      behavior: r.current_behavior,
      battery: r.battery ?? prev.battery,
      updatedAt: Date.now(),
    });
    // These subsystems are robot-reported; unknown from /robot until wired.
    useConnectionStore.getState().setStatuses({
      esp32: 'connecting',
      camera: 'connecting',
      microphone: 'connecting',
    });
  }, [demoMode, robotQuery.isSuccess, robotQuery.data]);
}
