/** useFilteredLogs — logs from the store, filtered by level. */
import {useMemo} from 'react';
import {useLogStore} from '@/store';
import type {LogFilter} from '@/types';

export function useFilteredLogs(filter: LogFilter) {
  const logs = useLogStore(s => s.logs);
  return useMemo(
    () => (filter === 'ALL' ? logs : logs.filter(log => log.level === filter)),
    [logs, filter],
  );
}
