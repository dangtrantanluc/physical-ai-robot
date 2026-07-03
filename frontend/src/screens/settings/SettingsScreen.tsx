/**
 * SettingsScreen — operator configuration. Edits a local draft; Save persists via the
 * settings store (MMKV). Toggling Demo Mode switches the app between generated mock
 * telemetry and live backend polling.
 */
import React, {useMemo, useState} from 'react';
import {StyleSheet, Text, View} from 'react-native';
import {Button, SegmentedButtons, Snackbar, Switch, TextInput} from 'react-native-paper';
import {Card, Screen, ScreenHeader, SectionHeader} from '@/components';
import {useSettingsStore} from '@/store';
import {palette, spacing, typography} from '@/theme';
import type {AppSettings, ImageQuality, ThemeMode} from '@/types';

const FPS_OPTIONS = ['10', '15', '24', '30'];

export function SettingsScreen() {
  const settings = useSettingsStore(s => s.settings);
  const commit = useSettingsStore(s => s.commit);
  const reset = useSettingsStore(s => s.reset);

  const [draft, setDraft] = useState<AppSettings>(settings);
  const [saved, setSaved] = useState(false);

  const dirty = useMemo(() => JSON.stringify(draft) !== JSON.stringify(settings), [draft, settings]);

  const set = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) =>
    setDraft(prev => ({...prev, [key]: value}));

  const onSave = () => {
    commit(draft);
    setSaved(true);
  };

  const onReset = () => {
    reset();
    setDraft(useSettingsStore.getState().settings);
  };

  return (
    <Screen scroll>
      <ScreenHeader title="Settings" subtitle="Connection & robot configuration" />

      <View style={styles.section}>
        <SectionHeader title="Connection" />
        <Card style={styles.card}>
          <Field label="Server URL">
            <TextInput
              mode="outlined"
              dense
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="url"
              value={draft.serverUrl}
              onChangeText={t => set('serverUrl', t)}
              placeholder="http://10.0.2.2:8000"
            />
          </Field>
          <ToggleRow
            label="Demo mode"
            hint="Render generated mock telemetry instead of polling the server"
            value={draft.demoMode}
            onValueChange={v => set('demoMode', v)}
          />
          <ToggleRow
            label="Auto connect"
            hint="Connect to the robot automatically on launch"
            value={draft.autoConnect}
            onValueChange={v => set('autoConnect', v)}
          />
        </Card>
      </View>

      <View style={styles.section}>
        <SectionHeader title="Robot" />
        <Card style={styles.card}>
          <Field label="Robot name">
            <TextInput
              mode="outlined"
              dense
              value={draft.robotName}
              onChangeText={t => set('robotName', t)}
            />
          </Field>
          <Field label="Robot ID">
            <TextInput
              mode="outlined"
              dense
              autoCapitalize="none"
              value={draft.robotId}
              onChangeText={t => set('robotId', t)}
            />
          </Field>
          <Field label="Bluetooth device (ESP32)">
            <TextInput
              mode="outlined"
              dense
              value={draft.bluetoothDevice}
              onChangeText={t => set('bluetoothDevice', t)}
            />
          </Field>
          <ToggleRow
            label="Auto start"
            hint="Start the control loop as soon as the robot connects"
            value={draft.autoStart}
            onValueChange={v => set('autoStart', v)}
          />
        </Card>
      </View>

      <View style={styles.section}>
        <SectionHeader title="Camera" />
        <Card style={styles.card}>
          <Field label="Camera FPS">
            <SegmentedButtons
              density="small"
              value={String(draft.cameraFps)}
              onValueChange={v => set('cameraFps', Number(v))}
              buttons={FPS_OPTIONS.map(v => ({value: v, label: v}))}
            />
          </Field>
          <Field label="Image quality">
            <SegmentedButtons
              density="small"
              value={draft.imageQuality}
              onValueChange={v => set('imageQuality', v as ImageQuality)}
              buttons={[
                {value: 'low', label: 'Low'},
                {value: 'medium', label: 'Medium'},
                {value: 'high', label: 'High'},
              ]}
            />
          </Field>
        </Card>
      </View>

      <View style={styles.section}>
        <SectionHeader title="Appearance" />
        <Card style={styles.card}>
          <Field label="Theme">
            <SegmentedButtons
              density="small"
              value={draft.themeMode}
              onValueChange={v => set('themeMode', v as ThemeMode)}
              buttons={[
                {value: 'dark', label: 'Dark'},
                {value: 'system', label: 'System'},
              ]}
            />
          </Field>
        </Card>
      </View>

      <View style={styles.actions}>
        <Button mode="contained" onPress={onSave} disabled={!dirty} icon="content-save">
          Save changes
        </Button>
        <Button mode="text" onPress={onReset} textColor={palette.textSecondary}>
          Reset to defaults
        </Button>
      </View>

      <Snackbar
        visible={saved}
        onDismiss={() => setSaved(false)}
        duration={2000}
        style={styles.snackbar}>
        Settings saved
      </Snackbar>
    </Screen>
  );
}

function Field({label, children}: {label: string; children: React.ReactNode}) {
  return (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      {children}
    </View>
  );
}

function ToggleRow({
  label,
  hint,
  value,
  onValueChange,
}: {
  label: string;
  hint: string;
  value: boolean;
  onValueChange: (v: boolean) => void;
}) {
  return (
    <View style={styles.toggleRow}>
      <View style={styles.toggleText}>
        <Text style={styles.toggleLabel}>{label}</Text>
        <Text style={styles.toggleHint}>{hint}</Text>
      </View>
      <Switch value={value} onValueChange={onValueChange} color={palette.primary} />
    </View>
  );
}

const styles = StyleSheet.create({
  section: {gap: spacing.sm},
  card: {gap: spacing.lg},
  field: {gap: spacing.sm},
  fieldLabel: {...typography.cardLabel, color: palette.textSecondary},
  toggleRow: {flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: spacing.lg},
  toggleText: {flex: 1, gap: 2},
  toggleLabel: {...typography.body, color: palette.text},
  toggleHint: {...typography.caption, color: palette.textMuted},
  actions: {gap: spacing.sm, marginTop: spacing.sm},
  snackbar: {backgroundColor: palette.surfaceElevated},
});
