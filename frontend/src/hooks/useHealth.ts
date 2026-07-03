/**
 * useHealth — polls GET /health (live mode only) and reflects the result into the
 * connection store's `server` status. Returns the raw query for detail display.
 */
import {useEffect} from 'react';
import {useQuery} from '@tanstack/react-query';
import {HealthService} from '@/services';
import {useConnectionStore, useSettingsStore} from '@/store';
import {POLL, QUERY} from '@/utils';

export function useHealth() {
  const demoMode = useSettingsStore(s => s.settings.demoMode);
  const setStatus = useConnectionStore(s => s.setStatus);
  const setError = useConnectionStore(s => s.setError);

  const query = useQuery({
    queryKey: ['health'],
    queryFn: HealthService.getHealth,
    enabled: !demoMode,
    refetchInterval: POLL.health,
    retry: QUERY.retry,
    staleTime: QUERY.staleTime,
  });

  useEffect(() => {
    if (demoMode) return;
    if (query.isSuccess) {
      setStatus('server', query.data.status === 'ok' ? 'online' : 'error');
      setError(null);
    } else if (query.isError) {
      setStatus('server', 'error');
      setError(query.error instanceof Error ? query.error.message : 'Health check failed');
    } else if (query.isLoading) {
      setStatus('server', 'connecting');
    }
  }, [demoMode, query.isSuccess, query.isError, query.isLoading, query.data, query.error, setStatus, setError]);

  return query;
}
