/** ActionButton — the dashboard control button (Start / Stop / Reconnect / E-Stop). */
import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleProp,
  StyleSheet,
  Text,
  View,
  ViewStyle,
} from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {palette, radius, spacing, typography} from '@/theme';

export type ButtonTone = 'primary' | 'success' | 'warning' | 'error' | 'neutral';
type Variant = 'filled' | 'outlined';

interface ActionButtonProps {
  label: string;
  onPress: () => void;
  icon?: string;
  tone?: ButtonTone;
  variant?: Variant;
  loading?: boolean;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
}

const TONE_COLOR: Record<ButtonTone, string> = {
  primary: palette.primary,
  success: palette.success,
  warning: palette.warning,
  error: palette.error,
  neutral: palette.textSecondary,
};

export function ActionButton({
  label,
  onPress,
  icon,
  tone = 'primary',
  variant = 'filled',
  loading = false,
  disabled = false,
  style,
}: ActionButtonProps) {
  const color = TONE_COLOR[tone];
  const filled = variant === 'filled';
  const contentColor = filled ? palette.textInverse : color;
  const isDisabled = disabled || loading;

  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      style={({pressed}) => [
        styles.base,
        filled ? {backgroundColor: color} : {borderColor: color, borderWidth: 1.5},
        isDisabled && styles.disabled,
        pressed && !isDisabled && styles.pressed,
        style,
      ]}>
      <View style={styles.content}>
        {loading ? (
          <ActivityIndicator size="small" color={contentColor} />
        ) : icon ? (
          <MaterialCommunityIcons name={icon} size={18} color={contentColor} />
        ) : null}
        <Text style={[styles.label, {color: contentColor}]}>{label}</Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radius.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    minHeight: 48,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {flexDirection: 'row', alignItems: 'center', gap: spacing.sm},
  label: {...typography.bodyStrong, letterSpacing: 0.3},
  disabled: {opacity: 0.45},
  pressed: {opacity: 0.85},
});
