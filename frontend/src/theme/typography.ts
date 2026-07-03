/**
 * Typographic scale. Uses the platform default font; sizes tuned for a dense,
 * legible engineering UI.
 */
import type {TextStyle} from 'react-native';

export const typography = {
  screenTitle: {fontSize: 22, fontWeight: '700', letterSpacing: 0.2},
  sectionTitle: {fontSize: 13, fontWeight: '700', letterSpacing: 0.8},
  cardLabel: {fontSize: 12, fontWeight: '600', letterSpacing: 0.4},
  metricValue: {fontSize: 26, fontWeight: '700'},
  metricUnit: {fontSize: 13, fontWeight: '600'},
  body: {fontSize: 14, fontWeight: '500'},
  bodyStrong: {fontSize: 14, fontWeight: '700'},
  caption: {fontSize: 12, fontWeight: '500'},
  mono: {fontSize: 12, fontWeight: '600', letterSpacing: 0.3},
} as const satisfies Record<string, TextStyle>;

export type TypographyVariant = keyof typeof typography;
