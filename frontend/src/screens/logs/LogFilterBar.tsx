/** LogFilterBar — segmented level filter (All / Info / Success / Warning / Error). */
import React from 'react';
import {Pressable, ScrollView, StyleSheet, Text} from 'react-native';
import {palette, radius, spacing, typography} from '@/theme';
import type {LogFilter} from '@/types';
import {logLevelColor} from '@/utils';

const FILTERS: LogFilter[] = ['ALL', 'INFO', 'SUCCESS', 'WARNING', 'ERROR'];

interface LogFilterBarProps {
  value: LogFilter;
  onChange: (filter: LogFilter) => void;
}

export function LogFilterBar({value, onChange}: LogFilterBarProps) {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={styles.container}>
      {FILTERS.map(filter => {
        const active = filter === value;
        const color = filter === 'ALL' ? palette.primary : logLevelColor(filter);
        return (
          <Pressable
            key={filter}
            onPress={() => onChange(filter)}
            style={[
              styles.chip,
              active ? {backgroundColor: color, borderColor: color} : styles.chipIdle,
            ]}>
            <Text style={[styles.label, {color: active ? palette.textInverse : palette.textSecondary}]}>
              {filter}
            </Text>
          </Pressable>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {gap: spacing.sm, paddingRight: spacing.lg},
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    borderWidth: StyleSheet.hairlineWidth,
  },
  chipIdle: {backgroundColor: palette.surface, borderColor: palette.border},
  label: {...typography.caption, fontWeight: '700', letterSpacing: 0.5},
});
