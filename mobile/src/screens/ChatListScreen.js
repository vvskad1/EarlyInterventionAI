/**
 * Chat List Screen - Shows all saved chats
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    View,
    FlatList,
    StyleSheet,
    TouchableOpacity,
    Alert,
} from 'react-native';
import {
    Appbar,
    Card,
    Text,
    FAB,
    Portal,
    Dialog,
    Button,
    Paragraph,
    useTheme,
    IconButton,
} from 'react-native-paper';
import { useFocusEffect } from '@react-navigation/native';
import { getChats, deleteChat, clearAllChats } from '../services/storage';
import { createNewChat, formatDate } from '../utils/helpers';
import { spacing } from '../config/theme';

const ChatListScreen = ({ navigation }) => {
    const theme = useTheme();
    const [chats, setChats] = useState([]);
    const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
    const [chatToDelete, setChatToDelete] = useState(null);

    // Load chats when screen is focused
    useFocusEffect(
        useCallback(() => {
            loadChats();
        }, [])
    );

    const loadChats = async () => {
        const loadedChats = await getChats();
        setChats(loadedChats);
    };

    const handleNewChat = () => {
        const newChat = createNewChat();
        navigation.navigate('Chat', { chat: newChat, isNew: true });
    };

    const handleChatPress = (chat) => {
        navigation.navigate('Chat', { chat, isNew: false });
    };

    const handleDeletePress = (chat) => {
        setChatToDelete(chat);
        setDeleteDialogVisible(true);
    };

    const confirmDelete = async () => {
        if (chatToDelete) {
            await deleteChat(chatToDelete.id);
            setDeleteDialogVisible(false);
            setChatToDelete(null);
            loadChats();
        }
    };

    const handleClearAll = () => {
        Alert.alert(
            'Clear All Chats',
            'Are you sure you want to delete all chats? This cannot be undone.',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete All',
                    style: 'destructive',
                    onPress: async () => {
                        await clearAllChats();
                        loadChats();
                    },
                },
            ]
        );
    };

    const renderChatItem = ({ item }) => (
        <TouchableOpacity onPress={() => handleChatPress(item)}>
            <Card style={styles.chatCard}>
                <Card.Content style={styles.chatCardContent}>
                    <View style={styles.chatHeader}>
                        <Text variant="titleMedium" style={styles.chatTitle}>
                            {item.title}
                        </Text>
                        <IconButton
                            icon="delete"
                            size={20}
                            onPress={() => handleDeletePress(item)}
                        />
                    </View>
                    {item.age_months !== null && (
                        <Text variant="bodySmall" style={styles.chatMeta}>
                            Age: {item.age_months} months
                        </Text>
                    )}
                    {item.domains && item.domains.length > 0 && (
                        <Text variant="bodySmall" style={styles.chatMeta}>
                            {item.domains.length} domain(s)
                        </Text>
                    )}
                    <Text variant="bodySmall" style={styles.chatDate}>
                        {formatDate(item.updatedAt)}
                    </Text>
                </Card.Content>
            </Card>
        </TouchableOpacity>
    );

    return (
        <View style={styles.container}>
            <Appbar.Header>
                <Appbar.Content title="Early Intervention AI" />
                {chats.length > 0 && (
                    <Appbar.Action icon="delete-sweep" onPress={handleClearAll} />
                )}
            </Appbar.Header>

            {chats.length === 0 ? (
                <View style={styles.emptyContainer}>
                    <Text variant="titleLarge" style={styles.emptyTitle}>
                        No Chats Yet
                    </Text>
                    <Text variant="bodyMedium" style={styles.emptyText}>
                        Create a new chat to generate an early intervention plan
                    </Text>
                </View>
            ) : (
                <FlatList
                    data={chats}
                    renderItem={renderChatItem}
                    keyExtractor={(item) => item.id}
                    contentContainerStyle={styles.listContent}
                />
            )}

            <FAB
                style={styles.fab}
                icon="plus"
                label="New Chat"
                onPress={handleNewChat}
            />

            <Portal>
                <Dialog visible={deleteDialogVisible} onDismiss={() => setDeleteDialogVisible(false)}>
                    <Dialog.Title>Delete Chat</Dialog.Title>
                    <Dialog.Content>
                        <Paragraph>Are you sure you want to delete this chat?</Paragraph>
                    </Dialog.Content>
                    <Dialog.Actions>
                        <Button onPress={() => setDeleteDialogVisible(false)}>Cancel</Button>
                        <Button onPress={confirmDelete}>Delete</Button>
                    </Dialog.Actions>
                </Dialog>
            </Portal>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    listContent: {
        padding: spacing.md,
    },
    chatCard: {
        marginBottom: spacing.md,
        elevation: 2,
    },
    chatCardContent: {
        paddingVertical: spacing.sm,
    },
    chatHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    chatTitle: {
        flex: 1,
        fontWeight: '600',
    },
    chatMeta: {
        color: '#666',
        marginTop: spacing.xs,
    },
    chatDate: {
        color: '#999',
        marginTop: spacing.sm,
        fontSize: 11,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: spacing.xl,
    },
    emptyTitle: {
        marginBottom: spacing.md,
        fontWeight: '600',
    },
    emptyText: {
        textAlign: 'center',
        color: '#666',
    },
    fab: {
        position: 'absolute',
        right: spacing.md,
        bottom: spacing.md,
    },
});

export default ChatListScreen;
