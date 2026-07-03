/**
 * RobotStatusIndicator — colored status dot + run-state label for the app bar.
 *
 * The only animation in the app: a subtle "live" pulse shown ONLY while the robot is
 * running, to signal an active control loop at a glance. Static otherwise.
 */
import React, {useEffect} from 'react';
import {StyleSheet, Text, View} from 'react-native';
import Animated, {
  cancelAnimation,
  Easing,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';
import {radius, spacing, typography} from '@/theme';
import type {RobotRunState} from '@/types';
import {runStateColor, runStateLabel} from '@/utils';

interface RobotStatusIndicatorProps {
  runState: RobotRunState;
}

export function RobotStatusIndicator({runState}: RobotStatusIndicatorProps) {
  const color = runStateColor(runState);
  const active = runState === 'running';
  const progress = useSharedValue(0);

  useEffect(() => {
    if (active) {
      progress.value = withRepeat(
        withTiming(1, {duration: 1600, easing: Easing.out(Easing.ease)}),
        -1,
        false,
      );
    } else {
      cancelAnimation(progress);
      progress.value = 0;
    }
    return () => cancelAnimation(progress);
  }, [active, progress]);

  const ringStyle = useAnimatedStyle(() => ({
    transform: [{scale: 1 + progress.value * 1.6}],
    opacity: 0.5 * (1 - progress.value),
  }));

  return (
    <View style={styles.container}>
      <View style={styles.dotWrap}>
        <Animated.View style={[styles.ring, {backgroundColor: color}, ringStyle]} />
        <View style={[styles.dot, {backgroundColor: color}]} />
      </View>
      <Text style={[styles.label, {color}]}>{runStateLabel(runState)}</Text>
    </View>
  );
}

const DOT = 9;

const styles = StyleSheet.create({
  container: {flexDirection: 'row', alignItems: 'center', gap: spacing.sm},
  dotWrap: {width: DOT, height: DOT, alignItems: 'center', justifyContent: 'center'},
  ring: {position: 'absolute', width: DOT, height: DOT, borderRadius: radius.pill},
  dot: {width: DOT, height: DOT, borderRadius: radius.pill},
  label: {...typography.caption, fontWeight: '800', letterSpacing: 0.6},
});
