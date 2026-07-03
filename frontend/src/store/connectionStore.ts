/**
 * connectionStore — live status of each monitored subsystem (server, ESP32, camera,
 * microphone) plus the last connection error. Fed by health/telemetry hooks.
 */
import {create} from 'zustand';
import type {ComponentKey, ComponentStatus} from '@/types';

type StatusMap = Record<ComponentKey, ComponentStatus>;

const OFFLINE: StatusMap = {
  server: 'offline',
  esp32: 'offline',
  camera: 'offline',
  microphone: 'offline',
};

interface ConnectionState {
  statuses: StatusMap;
  lastError: string | null;
  setStatus: (key: ComponentKey, status: ComponentStatus) => void;
  setStatuses: (statuses: Partial<StatusMap>) => void;
  setError: (message: string | null) => void;
  reset: () => void;
}

export const useConnectionStore = create<ConnectionState>(set => ({
  statuses: {...OFFLINE},
  lastError: null,
  setStatus: (key, status) => set(state => ({statuses: {...state.statuses, [key]: status}})),
  setStatuses: statuses => set(state => ({statuses: {...state.statuses, ...statuses}})),
  setError: message => set({lastError: message}),
  reset: () => set({statuses: {...OFFLINE}, lastError: null}),
}));

/** Selector: overall connectivity derived from the server subsystem. */
export const selectIsConnected = (s: ConnectionState): boolean => s.statuses.server === 'online';
