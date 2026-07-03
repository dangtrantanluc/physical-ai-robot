/** MetricCard — a big numeric/textual metric tile (battery, latency, fps, behavior…). */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {palette, spacing, typography} from '@/theme';

interface MetricCardProps {
  label: string;
  value: string;
  unit?: string;
  icon?: string;
  valueColor?: string;
  footer?: string;
}

export function MetricCard({label, value, unit, icon, valueColor, footer}: MetricCardProps) {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.label}>{label.toUpperCase()}</Text>
        {icon ? (
          <MaterialCommunityIcons name={icon} size={16} color={palette.textMuted} />
        ) : null}
      </View>
      <View style={styles.valueRow}>
        <Text style={[styles.value, valueColor ? {color: valueColor} : null]} numberOfLines={1}>
          {value}
        </Text>
        {unit ? <Text style={styles.unit}>{unit}</Text> : null}
      </View>
      {footer ? <Text style={styles.footer}>{footer}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: palette.surface,
    borderRadius: 16,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: palette.border,
    padding: spacing.lg,
    gap: spacing.sm,
    justifyContent: 'space-between',
  },
  header: {flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between'},
  label: {...typography.cardLabel, color: palette.textMuted},
  valueRow: {flexDirection: 'row', alignItems: 'flex-end', gap: spacing.xs},
  value: {...typography.metricValue, color: palette.text},
  unit: {...typography.metricUnit, color: palette.textSecondary, marginBottom: 3},
  footer: {...typography.caption, color: palette.textMuted},
});
