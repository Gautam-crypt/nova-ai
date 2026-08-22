import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import ChatScreen from './screens/ChatScreen';
import SecurityScreen from './screens/SecurityScreen';

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName: any = 'help-circle';

            if (route.name === 'Chat') {
              iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
            } else if (route.name === 'Security') {
              iconName = focused ? 'shield-checkmark' : 'shield-checkmark-outline';
            }

            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarActiveTintColor: '#0A84FF',
          tabBarInactiveTintColor: 'gray',
          tabBarStyle: {
            backgroundColor: '#1E1E1E',
            borderTopColor: '#333',
          },
          headerStyle: {
            backgroundColor: '#1E1E1E',
            borderBottomColor: '#333',
          },
          headerTintColor: '#fff',
        })}
      >
        <Tab.Screen name="Chat" component={ChatScreen} options={{ title: 'NOVA Console' }} />
        <Tab.Screen name="Security" component={SecurityScreen} options={{ title: 'KAVACH Dashboard' }} />
      </Tab.Navigator>
    </NavigationContainer>
  );
}
