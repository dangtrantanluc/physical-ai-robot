/** SectionHeader — uppercase section label with an optional right-side accessory. */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {palette, spacing, typography} from '@/theme';

interface SectionHeaderProps {
  title: string;
  right?: React.ReactNode;
}

export function SectionHeader({title, right}: SectionHeaderProps) {
  return (
    <View style={styles.row}>
      <Text style={styles.title}>{title.toUpperCase()}</Text>
      {right ? <View>{right}</View> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: spacing.xs,
  },
  title: {...typography.sectionTitle, color: palette.textMuted},
});
