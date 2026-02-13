/**
 * Chat Messages Component
 */

import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text } from 'react-native-paper';
import { spacing } from '../config/theme';

const ChatMessages = ({ messages }) => {
    if (!messages || messages.length === 0) return null;

    return (
        <Card style={styles.card}>
            <Card.Content>
                <Text variant="titleMedium" style={styles.title}>
                    💬 Conversation
                </Text>

                {messages.map((message, index) => (
                    <View
                        key={index}
                        style={[
                            styles.messageContainer,
                            message.role === 'user' ? styles.userMessage : styles.assistantMessage,
                        ]}
                    >
                        <Text
                            variant="labelSmall"
                            style={[
                                styles.roleLabel,
                                message.role === 'user' ? styles.userLabel : styles.assistantLabel,
                            ]}
                        >
                            {message.role === 'user' ? 'You' : 'AI Assistant'}
                        </Text>
                        <Text variant="bodyMedium" style={styles.messageText}>
                            {message.content}
                        </Text>
                    </View>
                ))}
            </Card.Content>
        </Card>
    );
};

const styles = StyleSheet.create({
    card: {
        marginBottom: spacing.md,
    },
    title: {
        fontWeight: '700',
        marginBottom: spacing.md,
    },
    messageContainer: {
        padding: spacing.md,
        borderRadius: 8,
        marginBottom: spacing.sm,
    },
    userMessage: {
        backgroundColor: '#e3f2fd',
        alignSelf: 'flex-end',
    },
    assistantMessage: {
        backgroundColor: '#f5f5f5',
        alignSelf: 'flex-start',
    },
    roleLabel: {
        fontWeight: '600',
        marginBottom: spacing.xs,
    },
    userLabel: {
        color: '#1976d2',
    },
    assistantLabel: {
        color: '#666',
    },
    messageText: {
        lineHeight: 20,
    },
});

export default ChatMessages;
