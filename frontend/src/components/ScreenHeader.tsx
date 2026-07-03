/** ScreenHeader — top bar for a screen (title + optional subtitle + right accessory). */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {palette, spacing, typography} from '@/theme';

interface ScreenHeaderProps {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
}

export function ScreenHeader({title, subtitle, right}: ScreenHeaderProps) {
  return (
    <View style={styles.container}>
      <View style={styles.textCol}>
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
        {subtitle ? (
          <Text style={styles.subtitle} numberOfLines={1}>
            {subtitle}
          </Text>
        ) : null}
      </View>
      {right ? <View style={styles.right}>{right}</View> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.md,
    paddingBottom: spacing.md,
    backgroundColor: palette.background,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: palette.border,
    gap: spacing.md,
  },
  textCol: {flex: 1, gap: 2},
  title: {...typography.screenTitle, color: palette.text},
  subtitle: {...typography.caption, color: palette.textMuted},
  right: {flexShrink: 0},
});
