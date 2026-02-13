/**
 * Early Intervention AI - Mobile App Entry Point
 */

import React from 'react';
import { StatusBar } from 'react-native';
import { Provider as PaperProvider } from 'react-native-paper';
import { NavigationContainer } from '@react-navigation/native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AppNavigator from './src/navigation/AppNavigator';
import { theme } from './src/config/theme';

function App() {
    return (
        <SafeAreaProvider>
            <PaperProvider theme={theme}>
                <NavigationContainer>
                    <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
                    <AppNavigator />
                </NavigationContainer>
            </PaperProvider>
        </SafeAreaProvider>
    );
}

export default App;
