/**
 * CameraOverlay — HUD drawn on top of the live preview: info chips (FPS, resolution,
 * upload status, detection count) + SVG detection boxes (mock now, model-fed later).
 */
import React from 'react';
import {StyleSheet, Text, View} from 'react-native';
import Svg, {Rect, Text as SvgText} from 'react-native-svg';
import {palette, radius, spacing, typography} from '@/theme';
import type {CameraOverlayInfo, UploadStatus} from '@/types';
import {formatFps} from '@/utils';

const UPLOAD_COLOR: Record<UploadStatus, string> = {
  ok: palette.success,
  uploading: palette.warning,
  error: palette.error,
  idle: palette.textMuted,
};

interface CameraOverlayProps {
  info: CameraOverlayInfo;
  width: number;
  height: number;
}

function Chip({label, value, color}: {label: string; value: string; color?: string}) {
  return (
    <View style={styles.chip}>
      <Text style={styles.chipLabel}>{label}</Text>
      <Text style={[styles.chipValue, color ? {color} : null]}>{value}</Text>
    </View>
  );
}

export function CameraOverlay({info, width, height}: CameraOverlayProps) {
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      {/* Detection boxes */}
      {width > 0 && height > 0 ? (
        <Svg style={StyleSheet.absoluteFill} width={width} height={height}>
          {info.boxes.map(box => {
            const x = box.x * width;
            const y = box.y * height;
            const w = box.width * width;
            const h = box.height * height;
            return (
              <React.Fragment key={box.id}>
                <Rect
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  stroke={palette.primary}
                  strokeWidth={2}
                  rx={4}
                  fill="transparent"
                />
                <SvgText x={x + 4} y={y - 6} fill={palette.primary} fontSize={12} fontWeight="700">
                  {`${box.label} ${Math.round(box.confidence * 100)}%`}
                </SvgText>
              </React.Fragment>
            );
          })}
        </Svg>
      ) : null}

      {/* Info chips */}
      <View style={styles.topRow}>
        <Chip label="FPS" value={formatFps(info.fps)} />
        <Chip label="RES" value={info.resolution} />
      </View>
      <View style={styles.bottomRow}>
        <Chip label="UPLOAD" value={info.uploadStatus.toUpperCase()} color={UPLOAD_COLOR[info.uploadStatus]} />
        <Chip label="DETECTIONS" value={String(info.detectionCount)} color={palette.primary} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  topRow: {
    position: 'absolute',
    top: spacing.lg,
    left: spacing.lg,
    right: spacing.lg,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  bottomRow: {
    position: 'absolute',
    bottom: spacing.lg,
    left: spacing.lg,
    right: spacing.lg,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    backgroundColor: palette.overlay,
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  chipLabel: {...typography.caption, color: palette.textMuted, letterSpacing: 0.5},
  chipValue: {...typography.mono, color: palette.text},
});
