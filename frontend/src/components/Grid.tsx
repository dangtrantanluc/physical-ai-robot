/**
 * Grid — lays children out in equal-width columns. Chunks into rows of `columns`
 * (flex:1 children + gap) so widths stay consistent across screen sizes, padding a
 * ragged final row with spacers.
 */
import React from 'react';
import {StyleSheet, View} from 'react-native';
import {spacing} from '@/theme';

interface GridProps {
  children: React.ReactNode;
  columns?: number;
  gap?: number;
}

export function Grid({children, columns = 2, gap = spacing.md}: GridProps) {
  const items = React.Children.toArray(children);
  const rows: React.ReactNode[][] = [];
  for (let i = 0; i < items.length; i += columns) {
    rows.push(items.slice(i, i + columns));
  }

  return (
    <View style={{gap}}>
      {rows.map((row, ri) => (
        <View key={ri} style={[styles.row, {gap}]}>
          {row.map((child, ci) => (
            <View key={ci} style={styles.cell}>
              {child}
            </View>
          ))}
          {Array.from({length: columns - row.length}).map((_, k) => (
            <View key={`spacer-${k}`} style={styles.cell} />
          ))}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {flexDirection: 'row'},
  cell: {flex: 1},
});
