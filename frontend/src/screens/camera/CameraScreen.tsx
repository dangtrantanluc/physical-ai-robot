/**
 * CameraScreen — large live preview (React Native Vision Camera) with a telemetry HUD.
 *
 * Gracefully degrades: prompts for permission if needed, and shows a placeholder on
 * devices without a camera (e.g. emulators) so the overlay is still demonstrable.
 */
import React, {useMemo, useState} from 'react';
import {LayoutChangeEvent, StyleSheet, Text, View} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import {useIsFocused} from '@react-navigation/native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {
  Camera,
  useCameraDevice,
  useCameraPermission,
} from 'react-native-vision-camera';
import {ActionButton, ScreenHeader} from '@/components';
import {useInterval} from '@/hooks';
import {useRobotStore} from '@/store';
import {palette, spacing, typography} from '@/theme';
import type {CameraOverlayInfo} from '@/types';
import {POLL, mockCameraOverlay} from '@/utils';
import {CameraOverlay} from './CameraOverlay';

export function CameraScreen() {
  const isFocused = useIsFocused();
  const {hasPermission, requestPermission} = useCameraPermission();
  const device = useCameraDevice('back');
  const fps = useRobotStore(s => s.telemetry.fps);

  const [size, setSize] = useState({width: 0, height: 0});
  const [overlay, setOverlay] = useState<CameraOverlayInfo>(() => mockCameraOverlay(fps));

  // Refresh the mock overlay periodically so detections/boxes look live.
  useInterval(() => setOverlay(mockCameraOverlay(fps)), isFocused ? POLL.telemetry : null);

  const onLayout = (e: LayoutChangeEvent) => {
    const {width, height} = e.nativeEvent.layout;
    setSize({width, height});
  };

  const preview = useMemo(() => {
    if (!hasPermission) {
      return (
        <Placeholder
          icon="camera-off-outline"
          title="Camera permission required"
          subtitle="Grant access to stream the robot's forward camera."
          action={<ActionButton label="Grant access" icon="camera" onPress={requestPermission} />}
        />
      );
    }
    if (device == null) {
      return (
        <Placeholder
          icon="camera-off-outline"
          title="No camera device"
          subtitle="No physical camera found (e.g. emulator). The overlay is still shown."
        />
      );
    }
    return (
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={isFocused}
        photo={false}
        video={false}
      />
    );
  }, [hasPermission, device, isFocused, requestPermission]);

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <ScreenHeader title="Camera" subtitle="Forward camera · live" />
      <View style={styles.preview} onLayout={onLayout}>
        {preview}
        <CameraOverlay info={overlay} width={size.width} height={size.height} />
      </View>
    </SafeAreaView>
  );
}

function Placeholder({
  icon,
  title,
  subtitle,
  action,
}: {
  icon: string;
  title: string;
  subtitle: string;
  action?: React.ReactNode;
}) {
  return (
    <View style={styles.placeholder}>
      <MaterialCommunityIcons name={icon} size={44} color={palette.textMuted} />
      <Text style={styles.placeholderTitle}>{title}</Text>
      <Text style={styles.placeholderSubtitle}>{subtitle}</Text>
      {action ? <View style={styles.placeholderAction}>{action}</View> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: {flex: 1, backgroundColor: palette.background},
  preview: {
    flex: 1,
    margin: spacing.lg,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: palette.black,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: palette.border,
  },
  placeholder: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
    gap: spacing.sm,
  },
  placeholderTitle: {...typography.bodyStrong, color: palette.text, marginTop: spacing.sm},
  placeholderSubtitle: {
    ...typography.caption,
    color: palette.textMuted,
    textAlign: 'center',
  },
  placeholderAction: {marginTop: spacing.lg},
});
