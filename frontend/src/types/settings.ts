/** Persisted operator settings (stored locally via MMKV). */
export type ImageQuality = 'low' | 'medium' | 'high';
export type ThemeMode = 'dark' | 'system';

export interface AppSettings {
  serverUrl: string;
  robotName: string;
  robotId: string;
  cameraFps: number;
  imageQuality: ImageQuality;
  bluetoothDevice: string;
  autoConnect: boolean;
  autoStart: boolean;
  themeMode: ThemeMode;
  /** When true, screens render generated mock telemetry instead of hitting the server. */
  demoMode: boolean;
}
