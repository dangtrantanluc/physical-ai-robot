/** ConnectionBadge — small colored pill showing a component's connection status. */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {radius, spacing, typography} from '@/theme';
import type {ComponentStatus} from '@/types';
import {statusColor, titleCase} from '@/utils';

interface ConnectionBadgeProps {
  status: ComponentStatus;
  label?: string;
}

export function ConnectionBadge({status, label}: ConnectionBadgeProps) {
  const color = statusColor(status);
  return (
    <View style={[styles.badge, {borderColor: color}]}>
      <View style={[styles.dot, {backgroundColor: color}]} />
      <Text style={[styles.label, {color}]}>{label ?? titleCase(status)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: 3,
    borderRadius: radius.pill,
    borderWidth: StyleSheet.hairlineWidth,
  },
  dot: {width: 7, height: 7, borderRadius: radius.pill},
  label: {...typography.caption, textTransform: 'capitalize'},
});
