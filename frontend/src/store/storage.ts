/**
 * MMKV-backed persistence + a Zustand `persist` adapter.
 *
 * MMKV is synchronous and fast, so state rehydration happens instantly on launch
 * (no async AsyncStorage flash). Screens never touch MMKV directly — they go through
 * stores/services.
 */
import {MMKV} from 'react-native-mmkv';

export const storage = new MMKV({id: 'robot-controller'});

/** Typed convenience helpers used by SettingsService. */
export const kv = {
  getObject<T>(key: string): T | null {
    const raw = storage.getString(key);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  },
  setObject<T>(key: string, value: T): void {
    storage.set(key, JSON.stringify(value));
  },
  remove(key: string): void {
    storage.delete(key);
  },
};
