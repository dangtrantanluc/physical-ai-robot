/**
 * App root — provider stack + navigation.
 *
 * Order matters: GestureHandler → SafeArea → ReactQuery → Paper(theme) → Navigation.
 * The headless <TelemetryEngine/> lives inside the query provider and keeps the stores
 * live for the whole session (demo stream or backend polling).
 */
import React from 'react';
import {StatusBar, StyleSheet} from 'react-native';
import {GestureHandlerRootView} from 'react-native-gesture-handler';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {PaperProvider} from 'react-native-paper';
import {NavigationContainer} from '@react-navigation/native';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {navigationTheme, palette, paperTheme} from '@/theme';
import {BottomTabs} from '@/navigation';
import {useTelemetryEngine} from '@/hooks';

const queryClient = new QueryClient({
  defaultOptions: {queries: {refetchOnWindowFocus: false, retry: 1}},
});

function TelemetryEngine(): null {
  useTelemetryEngine();
  return null;
}

export default function App() {
  return (
    <GestureHandlerRootView style={styles.root}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <PaperProvider theme={paperTheme}>
            <NavigationContainer theme={navigationTheme}>
              <StatusBar barStyle="light-content" backgroundColor={palette.background} />
              <TelemetryEngine />
              <BottomTabs />
            </NavigationContainer>
          </PaperProvider>
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({root: {flex: 1}});
