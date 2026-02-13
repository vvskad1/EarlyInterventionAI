/**
 * App Theme Configuration
 */

import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const theme = {
    ...DefaultTheme,
    colors: {
        ...DefaultTheme.colors,
        primary: '#1976d2',
        secondary: '#64b5f6',
        tertiary: '#90caf9',
        background: '#f5f5f5',
        surface: '#ffffff',
        surfaceVariant: '#e3f2fd',
        error: '#d32f2f',
        errorContainer: '#ffebee',
        onPrimary: '#ffffff',
        onSecondary: '#ffffff',
        onBackground: '#212121',
        onSurface: '#212121',
        onError: '#ffffff',
        outline: '#C9C4BC',
    },
    roundness: 8,
};

export const spacing = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
};

export const typography = {
    title: {
        fontSize: 24,
        fontWeight: '700',
        letterSpacing: 0.5,
    },
    subtitle: {
        fontSize: 16,
        fontWeight: '600',
    },
    body: {
        fontSize: 14,
        lineHeight: 20,
    },
    caption: {
        fontSize: 12,
        color: '#666',
    },
};
