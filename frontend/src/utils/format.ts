/** Pure formatting/helpers. No side effects, easily unit-tested. */
import {palette} from '@/theme';
import type {ComponentStatus, LogLevel, RobotRunState} from '@/types';
import {BATTERY_CRITICAL_PCT, BATTERY_LOW_PCT} from './constants';

export const clamp = (value: number, min: number, max: number): number =>
  Math.max(min, Math.min(max, value));

export const round = (value: number, decimals = 2): number => {
  const f = 10 ** decimals;
  return Math.round(value * f) / f;
};

export const formatVelocity = (v: number): string => `${v >= 0 ? '+' : ''}${round(v, 3).toFixed(3)}`;

export const formatPercent = (v: number): string => `${Math.round(clamp(v, 0, 100))}`;

export const formatLatency = (ms: number): string => `${Math.round(ms)}`;

export const formatFps = (fps: number): string => round(fps, 1).toFixed(1);

export const titleCase = (s: string): string =>
  s.length === 0 ? s : s[0].toUpperCase() + s.slice(1);

export function formatClockTime(epochMs: number): string {
  const d = new Date(epochMs);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

export function formatRelativeTime(epochMs: number, now = Date.now()): string {
  const diff = Math.max(0, Math.round((now - epochMs) / 1000));
  if (diff < 5) return 'just now';
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export function statusColor(status: ComponentStatus): string {
  switch (status) {
    case 'online':
      return palette.success;
    case 'connecting':
      return palette.warning;
    case 'error':
      return palette.error;
    case 'offline':
    default:
      return palette.textMuted;
  }
}

export function logLevelColor(level: LogLevel): string {
  switch (level) {
    case 'SUCCESS':
      return palette.success;
    case 'WARNING':
      return palette.warning;
    case 'ERROR':
      return palette.error;
    case 'INFO':
    default:
      return palette.info;
  }
}

export function batteryColor(pct: number): string {
  if (pct <= BATTERY_CRITICAL_PCT) return palette.error;
  if (pct <= BATTERY_LOW_PCT) return palette.warning;
  return palette.success;
}

export function runStateColor(state: RobotRunState): string {
  switch (state) {
    case 'running':
      return palette.success;
    case 'idle':
      return palette.info;
    case 'error':
    case 'estopped':
      return palette.error;
    case 'offline':
    default:
      return palette.textMuted;
  }
}

export function runStateLabel(state: RobotRunState): string {
  switch (state) {
    case 'estopped':
      return 'E-STOPPED';
    case 'offline':
      return 'OFFLINE';
    default:
      return state.toUpperCase();
  }
}
