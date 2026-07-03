/**
 * React Native Paper (MD3) dark theme, wired to our palette.
 * Also merged with the React Navigation dark theme so both libraries agree.
 */
import {MD3DarkTheme} from 'react-native-paper';
import {DarkTheme as NavDarkTheme} from '@react-navigation/native';
import {palette} from './colors';

export const paperTheme = {
  ...MD3DarkTheme,
  dark: true,
  roundness: 3,
  colors: {
    ...MD3DarkTheme.colors,
    primary: palette.primary,
    onPrimary: palette.white,
    secondary: palette.info,
    background: palette.background,
    surface: palette.surface,
    surfaceVariant: palette.surfaceVariant,
    onSurface: palette.text,
    onSurfaceVariant: palette.textSecondary,
    outline: palette.border,
    error: palette.error,
    elevation: {
      ...MD3DarkTheme.colors.elevation,
      level0: palette.background,
      level1: palette.surface,
      level2: palette.surfaceVariant,
      level3: palette.surfaceElevated,
    },
  },
};

export const navigationTheme = {
  ...NavDarkTheme,
  colors: {
    ...NavDarkTheme.colors,
    primary: palette.primary,
    background: palette.background,
    card: palette.surface,
    text: palette.text,
    border: palette.border,
    notification: palette.error,
  },
};

export type AppTheme = typeof paperTheme;
