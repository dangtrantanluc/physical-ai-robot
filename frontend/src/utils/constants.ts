import type {AppSettings} from '@/types';

/** Default server URL (Android emulator maps host localhost to 10.0.2.2). */
export const DEFAULT_SERVER_URL = 'http://10.0.2.2:8000';

/** Polling cadences (ms). */
export const POLL = {
  telemetry: 1000,
  health: 5000,
  logs: 2000,
} as const;

/** React Query staleness/cache windows (ms). */
export const QUERY = {
  staleTime: 800,
  gcTime: 30_000,
  retry: 1,
} as const;

export const DEFAULT_SETTINGS: AppSettings = {
  serverUrl: DEFAULT_SERVER_URL,
  robotName: 'Realme-Q Rover',
  robotId: 'realme-q-01',
  cameraFps: 15,
  imageQuality: 'medium',
  bluetoothDevice: 'ESP32-ROBOT',
  autoConnect: true,
  autoStart: false,
  themeMode: 'dark',
  demoMode: true,
};

export const BATTERY_LOW_PCT = 25;
export const BATTERY_CRITICAL_PCT = 12;
