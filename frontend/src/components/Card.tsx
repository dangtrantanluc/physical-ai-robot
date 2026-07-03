/** Card — the base rounded surface every dashboard tile is built on. */
import React from 'react';
import {Pressable, StyleProp, StyleSheet, View, ViewStyle} from 'react-native';
import {palette, radius, spacing} from '@/theme';

interface CardProps {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  padded?: boolean;
  onPress?: () => void;
}

export function Card({children, style, padded = true, onPress}: CardProps) {
  const content = <View style={[styles.card, padded && styles.padded, style]}>{children}</View>;
  if (onPress) {
    return (
      <Pressable onPress={onPress} style={({pressed}) => (pressed ? styles.pressed : undefined)}>
        {content}
      </Pressable>
    );
  }
  return content;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: palette.surface,
    borderRadius: radius.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: palette.border,
  },
  padded: {padding: spacing.lg},
  pressed: {opacity: 0.85},
});
