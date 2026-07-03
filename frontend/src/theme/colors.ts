/**
 * Color palette — dark, industrial, minimal.
 * Single source of truth for every color used in the app.
 */
export const palette = {
  // Base surfaces
  background: '#121212',
  surface: '#1E1E1E',
  surfaceVariant: '#262626',
  surfaceElevated: '#2A2A2A',
  border: '#2E2E2E',
  borderStrong: '#3A3A3A',

  // Brand / semantic
  primary: '#3B82F6', // blue
  primaryMuted: '#1D4ED8',
  success: '#22C55E', // green
  warning: '#F59E0B', // orange
  error: '#EF4444', // red
  info: '#38BDF8',

  // Text
  text: '#F5F5F5',
  textSecondary: '#B4B4B4',
  textMuted: '#7E7E7E',
  textInverse: '#0A0A0A',

  // Utility
  overlay: 'rgba(0, 0, 0, 0.55)',
  scrim: 'rgba(0, 0, 0, 0.7)',
  transparent: 'transparent',
  white: '#FFFFFF',
  black: '#000000',
} as const;

/** 12%-opacity tint of a semantic color, for badge/card backgrounds. */
export const tint = {
  primary: 'rgba(59, 130, 246, 0.14)',
  success: 'rgba(34, 197, 94, 0.14)',
  warning: 'rgba(245, 158, 11, 0.14)',
  error: 'rgba(239, 68, 68, 0.14)',
  neutral: 'rgba(255, 255, 255, 0.06)',
} as const;

export type PaletteColor = keyof typeof palette;
