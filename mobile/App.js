import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from './src/screens/HomeScreen';
import TutorScreen from './src/screens/TutorScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: '#007AFF',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
            fontSize: 18,
          },
          headerTitleAlign: 'center',
          contentStyle: {
            backgroundColor: '#fff',
          },
          animation: 'slide_from_right',
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ 
            title: 'AI Math Tutor',
          }}
        />
        <Stack.Screen 
          name="Tutor" 
          component={TutorScreen}
          options={{ 
            title: 'Problem Solving',
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
