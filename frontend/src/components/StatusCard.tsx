/** StatusCard — a subsystem tile (icon + name + ConnectionBadge + optional detail). */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {palette, spacing, typography} from '@/theme';
import type {ComponentStatus} from '@/types';
import {statusColor} from '@/utils';
import {Card} from './Card';
import {ConnectionBadge} from './ConnectionBadge';

interface StatusCardProps {
  title: string;
  icon: string;
  status: ComponentStatus;
  detail?: string;
}

export function StatusCard({title, icon, status, detail}: StatusCardProps) {
  const color = statusColor(status);
  return (
    <Card style={styles.card}>
      <View style={styles.header}>
        <MaterialCommunityIcons name={icon} size={20} color={color} />
        <Text style={styles.title}>{title}</Text>
      </View>
      <ConnectionBadge status={status} />
      {detail ? <Text style={styles.detail}>{detail}</Text> : null}
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {gap: spacing.md},
  header: {flexDirection: 'row', alignItems: 'center', gap: spacing.sm},
  title: {...typography.cardLabel, color: palette.textSecondary},
  detail: {...typography.caption, color: palette.textMuted},
});
