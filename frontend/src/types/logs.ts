/** Log stream types for the Logs screen. */
export type LogLevel = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';

export interface LogEntry {
  id: string;
  timestamp: number; // epoch ms
  level: LogLevel;
  source: string; // e.g. "planner", "esp32", "camera"
  message: string;
}

/** Filter selection on the Logs screen ('ALL' = no filter). */
export type LogFilter = LogLevel | 'ALL';
