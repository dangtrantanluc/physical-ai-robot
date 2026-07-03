/** MissionCard — current mission summary with a progress bar. */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {ProgressBar} from 'react-native-paper';
import {Card} from '@/components';
import {palette, radius, spacing, typography} from '@/theme';
import type {Mission} from '@/types';

const STATUS_COLOR: Record<Mission['status'], string> = {
  pending: palette.textMuted,
  active: palette.success,
  completed: palette.primary,
  failed: palette.error,
  cancelled: palette.textMuted,
};

interface MissionCardProps {
  mission: Mission | null;
}

export function MissionCard({mission}: MissionCardProps) {
  if (!mission) {
    return (
      <Card>
        <Text style={styles.empty}>No active mission</Text>
      </Card>
    );
  }

  const color = STATUS_COLOR[mission.status];
  return (
    <Card>
      <View style={styles.header}>
        <Text style={styles.name} numberOfLines={1}>
          {mission.name}
        </Text>
        <View style={[styles.chip, {borderColor: color}]}>
          <Text style={[styles.chipText, {color}]}>{mission.status.toUpperCase()}</Text>
        </View>
      </View>
      <Text style={styles.goal} numberOfLines={2}>
        {mission.goal}
      </Text>
      <View style={styles.progressRow}>
        <ProgressBar
          progress={mission.progress}
          color={palette.primary}
          style={styles.progress}
        />
        <Text style={styles.pct}>{Math.round(mission.progress * 100)}%</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  header: {flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: spacing.sm},
  name: {...typography.bodyStrong, color: palette.text, flex: 1},
  chip: {
    borderWidth: StyleSheet.hairlineWidth,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
  },
  chipText: {fontSize: 10, fontWeight: '800', letterSpacing: 0.5},
  goal: {...typography.caption, color: palette.textSecondary, marginTop: spacing.sm},
  progressRow: {flexDirection: 'row', alignItems: 'center', gap: spacing.md, marginTop: spacing.lg},
  progress: {flex: 1, height: 6, borderRadius: radius.pill, backgroundColor: palette.surfaceVariant},
  pct: {...typography.mono, color: palette.textSecondary},
  empty: {...typography.body, color: palette.textMuted, textAlign: 'center', paddingVertical: spacing.sm},
});
