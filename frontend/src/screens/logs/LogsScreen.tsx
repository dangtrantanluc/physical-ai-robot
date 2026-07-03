/**
 * LogsScreen — scrollable, filterable event log. Entries stream in from the telemetry
 * engine (demo) or would be fed by a logs endpoint (live). Newest first.
 */
import React, {useState} from 'react';
import {FlatList, Pressable, StyleSheet, Text, View} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {LogItem, ScreenHeader} from '@/components';
import {useFilteredLogs} from '@/hooks';
import {useLogStore} from '@/store';
import {palette, spacing, typography} from '@/theme';
import type {LogEntry, LogFilter} from '@/types';
import {LogFilterBar} from './LogFilterBar';

export function LogsScreen() {
  const [filter, setFilter] = useState<LogFilter>('ALL');
  const logs = useFilteredLogs(filter);
  const clear = useLogStore(s => s.clear);

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      <ScreenHeader
        title="Logs"
        subtitle={`${logs.length} entries`}
        right={
          <Pressable onPress={clear} hitSlop={8} style={styles.clearBtn}>
            <MaterialCommunityIcons name="trash-can-outline" size={20} color={palette.textSecondary} />
          </Pressable>
        }
      />
      <View style={styles.filterWrap}>
        <LogFilterBar value={filter} onChange={setFilter} />
      </View>
      <FlatList
        data={logs}
        keyExtractor={item => item.id}
        renderItem={renderLog}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={<EmptyState />}
        removeClippedSubviews
        initialNumToRender={12}
        windowSize={9}
      />
    </SafeAreaView>
  );
}

const renderLog = ({item}: {item: LogEntry}) => <LogItem log={item} />;

function EmptyState() {
  return (
    <View style={styles.empty}>
      <MaterialCommunityIcons name="text-box-remove-outline" size={40} color={palette.textMuted} />
      <Text style={styles.emptyText}>No log entries match this filter</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: {flex: 1, backgroundColor: palette.background},
  filterWrap: {paddingHorizontal: spacing.lg, paddingVertical: spacing.md},
  clearBtn: {padding: spacing.xs},
  list: {paddingHorizontal: spacing.lg, paddingBottom: spacing.xl, gap: spacing.sm},
  empty: {alignItems: 'center', justifyContent: 'center', paddingTop: spacing.xxxl, gap: spacing.md},
  emptyText: {...typography.body, color: palette.textMuted},
});
