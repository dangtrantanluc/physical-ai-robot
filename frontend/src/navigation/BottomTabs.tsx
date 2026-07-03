/** Bottom tab navigator: Dashboard · Camera · Logs · Settings. */
import React from 'react';
import {StyleSheet} from 'react-native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {palette, spacing, typography} from '@/theme';
import {DashboardScreen} from '@/screens/dashboard/DashboardScreen';
import {CameraScreen} from '@/screens/camera/CameraScreen';
import {LogsScreen} from '@/screens/logs/LogsScreen';
import {SettingsScreen} from '@/screens/settings/SettingsScreen';
import type {RootTabParamList} from './types';

const Tab = createBottomTabNavigator<RootTabParamList>();

const ICONS: Record<keyof RootTabParamList, string> = {
  Dashboard: 'view-dashboard-outline',
  Camera: 'camera-outline',
  Logs: 'format-list-bulleted',
  Settings: 'cog-outline',
};

export function BottomTabs() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        headerShown: false,
        tabBarActiveTintColor: palette.primary,
        tabBarInactiveTintColor: palette.textMuted,
        tabBarStyle: {
          backgroundColor: palette.surface,
          borderTopColor: palette.border,
          borderTopWidth: StyleSheet.hairlineWidth,
          height: 62,
          paddingBottom: spacing.sm,
          paddingTop: spacing.sm,
        },
        tabBarLabelStyle: {...typography.caption, fontWeight: '600'},
        tabBarIcon: ({color, size}) => (
          <MaterialCommunityIcons name={ICONS[route.name]} color={color} size={size} />
        ),
      })}>
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Camera" component={CameraScreen} />
      <Tab.Screen name="Logs" component={LogsScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}
