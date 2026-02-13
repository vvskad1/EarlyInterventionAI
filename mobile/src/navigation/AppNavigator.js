/**
 * App Navigator
 */

import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import ChatListScreen from '../screens/ChatListScreen';
import ChatScreen from '../screens/ChatScreen';

const Stack = createStackNavigator();

const AppNavigator = () => {
    return (
        <Stack.Navigator
            initialRouteName="ChatList"
            screenOptions={{
                headerShown: false,
            }}
        >
            <Stack.Screen name="ChatList" component={ChatListScreen} />
            <Stack.Screen name="Chat" component={ChatScreen} />
        </Stack.Navigator>
    );
};

export default AppNavigator;
