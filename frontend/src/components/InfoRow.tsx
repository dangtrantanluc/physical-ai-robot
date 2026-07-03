/** InfoRow — a label/value row (used for last command, velocities, settings summaries). */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {palette, spacing, typography} from '@/theme';

interface InfoRowProps {
  label: string;
  value: string;
  valueColor?: string;
  mono?: boolean;
  divider?: boolean;
}

export function InfoRow({label, value, valueColor, mono, divider}: InfoRowProps) {
  return (
    <View style={[styles.row, divider && styles.divider]}>
      <Text style={styles.label}>{label}</Text>
      <Text style={[mono ? styles.valueMono : styles.value, valueColor ? {color: valueColor} : null]}>
        {value}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing.sm,
  },
  divider: {borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: palette.border},
  label: {...typography.body, color: palette.textSecondary},
  value: {...typography.bodyStrong, color: palette.text},
  valueMono: {...typography.mono, color: palette.text},
});
