/**
 * logStore — an in-memory ring buffer of log entries for the Logs screen.
 * Capped so the list can't grow unbounded during a long session.
 */
import {create} from 'zustand';
import type {LogEntry} from '@/types';
import {seedLogs} from '@/utils';

const MAX_LOGS = 300;

interface LogState {
  logs: LogEntry[];
  append: (entry: LogEntry) => void;
  prependMany: (entries: LogEntry[]) => void;
  clear: () => void;
}

export const useLogStore = create<LogState>(set => ({
  logs: seedLogs(),
  append: entry => set(state => ({logs: [entry, ...state.logs].slice(0, MAX_LOGS)})),
  prependMany: entries => set(state => ({logs: [...entries, ...state.logs].slice(0, MAX_LOGS)})),
  clear: () => set({logs: []}),
}));
