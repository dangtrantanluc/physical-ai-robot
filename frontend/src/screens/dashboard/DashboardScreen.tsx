/**
 * DashboardScreen — the primary monitoring view.
 *
 * Top bar (robot name + live status) · subsystem connection cards · key metrics ·
 * current mission · control buttons · last velocity command. All data comes from the
 * stores (kept live by the telemetry engine); control actions go through useRobotControl.
 */
import React from 'react';
import {StyleSheet, View} from 'react-native';
import {
  ActionButton,
  Card,
  Grid,
  InfoRow,
  MetricCard,
  RobotStatusIndicator,
  Screen,
  ScreenHeader,
  SectionHeader,
  StatusCard,
} from '@/components';
import {useHealth, useRobotControl} from '@/hooks';
import {useConnectionStore, useRobotStore, useSettingsStore} from '@/store';
import {spacing} from '@/theme';
import {
  batteryColor,
  formatFps,
  formatLatency,
  formatPercent,
  formatVelocity,
  formatRelativeTime,
  titleCase,
} from '@/utils';
import {MissionCard} from './MissionCard';

export function DashboardScreen() {
  const telemetry = useRobotStore(s => s.telemetry);
  const statuses = useConnectionStore(s => s.statuses);
  const demoMode = useSettingsStore(s => s.settings.demoMode);
  const control = useRobotControl();
  const health = useHealth();

  const serverDetail = demoMode
    ? 'demo mode'
    : health.data
      ? `v${health.data.version} · ${health.data.environment}`
      : 'no response';

  return (
    <Screen scroll>
      <ScreenHeader
        title={telemetry.robotName}
        subtitle={telemetry.robotId}
        right={<RobotStatusIndicator runState={telemetry.runState} />}
      />

      <View style={styles.section}>
        <SectionHeader title="Connections" />
        <Grid columns={2}>
          <StatusCard title="Server" icon="server-network" status={statuses.server} detail={serverDetail} />
          <StatusCard title="ESP32" icon="chip" status={statuses.esp32} detail="motor controller" />
          <StatusCard title="Camera" icon="camera" status={statuses.camera} detail="video uplink" />
          <StatusCard
            title="Microphone"
            icon="microphone"
            status={statuses.microphone}
            detail="audio uplink"
          />
        </Grid>
      </View>

      <View style={styles.section}>
        <SectionHeader title="Telemetry" />
        <Grid columns={2}>
          <MetricCard label="Behavior" value={titleCase(telemetry.behavior)} icon="robot" />
          <MetricCard label="State" value={titleCase(telemetry.state)} icon="state-machine" />
          <MetricCard
            label="Battery"
            value={formatPercent(telemetry.battery)}
            unit="%"
            icon="battery"
            valueColor={batteryColor(telemetry.battery)}
          />
          <MetricCard label="Latency" value={formatLatency(telemetry.latencyMs)} unit="ms" icon="timer-outline" />
          <MetricCard label="FPS" value={formatFps(telemetry.fps)} icon="speedometer" />
        </Grid>
      </View>

      <View style={styles.section}>
        <SectionHeader title="Current Mission" />
        <MissionCard mission={telemetry.mission} />
      </View>

      <View style={styles.section}>
        <SectionHeader title="Controls" />
        <View style={styles.controlsCol}>
          <View style={styles.controlsRow}>
            <ActionButton
              label="Start"
              icon="play"
              tone="success"
              onPress={control.start}
              disabled={control.isPending}
              style={styles.controlItem}
            />
            <ActionButton
              label="Stop"
              icon="stop"
              tone="neutral"
              variant="outlined"
              onPress={control.stop}
              disabled={control.isPending}
              style={styles.controlItem}
            />
          </View>
          <ActionButton
            label="Reconnect"
            icon="refresh"
            tone="primary"
            variant="outlined"
            onPress={control.reconnect}
            loading={control.isPending}
          />
          <ActionButton
            label="Emergency Stop"
            icon="alert-octagon"
            tone="error"
            onPress={control.emergencyStop}
          />
        </View>
      </View>

      <View style={styles.section}>
        <SectionHeader title="Last Command" />
        <Card>
          <InfoRow label="Behavior" value={titleCase(telemetry.behavior)} divider />
          <InfoRow
            label="Linear velocity"
            value={`${formatVelocity(telemetry.lastCommand.linear)} m/s`}
            mono
            divider
          />
          <InfoRow
            label="Angular velocity"
            value={`${formatVelocity(telemetry.lastCommand.angular)} rad/s`}
            mono
            divider
          />
          <InfoRow label="Updated" value={formatRelativeTime(telemetry.updatedAt)} />
        </Card>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  section: {gap: spacing.sm},
  controlsCol: {gap: spacing.md},
  controlsRow: {flexDirection: 'row', gap: spacing.md},
  controlItem: {flex: 1},
});
