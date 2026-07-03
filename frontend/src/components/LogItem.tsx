/** LogItem — one row in the Logs screen (time · level · source · message). */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {palette, radius, spacing, typography} from '@/theme';
import type {LogEntry} from '@/types';
import {formatClockTime, logLevelColor} from '@/utils';

interface LogItemProps {
  log: LogEntry;
}

function LogItemComponent({log}: LogItemProps) {
  const color = logLevelColor(log.level);
  return (
    <View style={styles.row}>
      <View style={[styles.rail, {backgroundColor: color}]} />
      <View style={styles.body}>
        <View style={styles.header}>
          <Text style={styles.time}>{formatClockTime(log.timestamp)}</Text>
          <View style={[styles.levelChip, {borderColor: color}]}>
            <Text style={[styles.levelText, {color}]}>{log.level}</Text>
          </View>
          <Text style={styles.source}>{log.source}</Text>
        </View>
        <Text style={styles.message}>{log.message}</Text>
      </View>
    </View>
  );
}

export const LogItem = React.memo(LogItemComponent);

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    backgroundColor: palette.surface,
    borderRadius: radius.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: palette.border,
    overflow: 'hidden',
  },
  rail: {width: 3},
  body: {flex: 1, padding: spacing.md, gap: spacing.xs},
  header: {flexDirection: 'row', alignItems: 'center', gap: spacing.sm},
  time: {...typography.mono, color: palette.textMuted},
  levelChip: {
    borderWidth: StyleSheet.hairlineWidth,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.xs,
    paddingVertical: 1,
  },
  levelText: {fontSize: 10, fontWeight: '800', letterSpacing: 0.5},
  source: {...typography.caption, color: palette.textSecondary},
  message: {...typography.body, color: palette.text},
});
