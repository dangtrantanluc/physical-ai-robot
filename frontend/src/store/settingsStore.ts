/**
 * settingsStore — operator settings (server URL, robot name, camera, toggles).
 *
 * Source of truth for configuration. Persisted via SettingsService (MMKV). The Axios
 * client reads `serverUrl` from here on every request, so edits apply immediately.
 */
import {create} from 'zustand';
import type {AppSettings} from '@/types';
import {SettingsService} from '@/services/SettingsService';

interface SettingsState {
  settings: AppSettings;
  /** Merge a partial update into memory (does not persist until save()). */
  update: (patch: Partial<AppSettings>) => void;
  /** Persist the current in-memory settings. */
  save: () => void;
  /** Replace all settings and persist. */
  commit: (settings: AppSettings) => void;
  reset: () => void;
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  settings: SettingsService.load(),
  update: patch => set(state => ({settings: {...state.settings, ...patch}})),
  save: () => SettingsService.save(get().settings),
  commit: settings => {
    SettingsService.save(settings);
    set({settings});
  },
  reset: () => set({settings: SettingsService.reset()}),
}));
