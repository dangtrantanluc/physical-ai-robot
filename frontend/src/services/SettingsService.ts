/**
 * SettingsService — persistence for operator settings.
 *
 * Settings live locally (MMKV); the backend has no settings endpoint. Keeping this
 * behind a service means screens/stores depend on an abstraction, so a future
 * server-sync backend can be added here without touching callers.
 */
import {kv} from '@/store/storage';
import type {AppSettings} from '@/types';
import {DEFAULT_SETTINGS} from '@/utils';

const KEY = 'app-settings';

export const SettingsService = {
  /** Load persisted settings merged over defaults (forward-compatible with new keys). */
  load(): AppSettings {
    const stored = kv.getObject<Partial<AppSettings>>(KEY);
    return {...DEFAULT_SETTINGS, ...(stored ?? {})};
  },

  save(settings: AppSettings): void {
    kv.setObject(KEY, settings);
  },

  reset(): AppSettings {
    kv.remove(KEY);
    return {...DEFAULT_SETTINGS};
  },
};
