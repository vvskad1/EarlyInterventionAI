/**
 * Chat Screen - Main interaction screen
 */

import React, { useState, useEffect, useRef } from 'react';
import {
    View,
    ScrollView,
    StyleSheet,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import {
    Appbar,
    TextInput,
    Button,
    Card,
    Text,
    Portal,
    Snackbar,
    ActivityIndicator,
} from 'react-native-paper';
import ChildProfileForm from '../components/ChildProfileForm';
import PlanDisplay from '../components/PlanDisplay';
import ChatMessages from '../components/ChatMessages';
import VoiceControls from '../components/VoiceControls';
import { generatePlan, sendChatMessage } from '../services/api';
import { saveChat } from '../services/storage';
import { updateChatTimestamp } from '../utils/helpers';
import { spacing } from '../config/theme';

const ChatScreen = ({ route, navigation }) => {
    const { chat: initialChat, isNew } = route.params;

    const [chat, setChat] = useState(initialChat);
    const [chatMessage, setChatMessage] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [snackbar, setSnackbar] = useState({ visible: false, message: '', type: 'info' });
    const [autoSpeak, setAutoSpeak] = useState(false);
    const scrollViewRef = useRef(null);

    useEffect(() => {
        // Save chat whenever it changes
        if (!isNew) {
            const updatedChat = updateChatTimestamp(chat);
            saveChat(updatedChat);
        }
    }, [chat]);

    const showSnackbar = (message, type = 'info') => {
        setSnackbar({ visible: true, message, type });
    };

    const updateChat = (updates) => {
        setChat(prev => ({ ...prev, ...updates }));
    };

    const handleGenerate = async () => {
        if (!chat.age_months || !chat.domains || chat.domains.length === 0) {
            showSnackbar('Please fill in age and select at least one domain', 'error');
            return;
        }

        setIsGenerating(true);
        try {
            const result = await generatePlan({
                ageMonths: chat.age_months,
                domains: chat.domains,
                notes: chat.notes,
            });

            updateChat({
                plan: result,
                title: `${chat.age_months}mo - ${chat.domains[0]}`,
            });

            // Save as new chat if it's a new one
            if (isNew) {
                await saveChat({
                    ...chat,
                    plan: result,
                    title: `${chat.age_months}mo - ${chat.domains[0]}`,
                });
            }

            showSnackbar('Plan generated successfully!', 'success');
        } catch (error) {
            showSnackbar(error.message, 'error');
        } finally {
            setIsGenerating(false);
        }
    };

    const handleSendMessage = async () => {
        if (!chatMessage.trim()) return;
        if (!chat.plan) {
            showSnackbar('Please generate a plan first', 'error');
            return;
        }

        const userMessage = { role: 'user', content: chatMessage };
        const updatedMessages = [...chat.messages, userMessage];

        updateChat({ messages: updatedMessages });
        setChatMessage('');
        setIsSending(true);

        try {
            const result = await sendChatMessage({
                ageMonths: chat.age_months,
                domains: chat.domains,
                notes: chat.notes,
                plan: chat.plan,
                messages: updatedMessages,
            });

            const assistantMessage = { role: 'assistant', content: result.response };
            updateChat({ messages: [...updatedMessages, assistantMessage] });

            // Scroll to bottom after message is added
            setTimeout(() => {
                scrollViewRef.current?.scrollToEnd({ animated: true });
            }, 100);
        } catch (error) {
            showSnackbar(error.message, 'error');
        } finally {
            setIsSending(false);
        }
    };

    const handleVoiceTranscript = (transcript) => {
        setChatMessage(transcript);
    };

    return (
        <View style={styles.container}>
            <Appbar.Header>
                <Appbar.BackAction onPress={() => navigation.goBack()} />
                <Appbar.Content title={chat.title} />
            </Appbar.Header>

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={styles.flex}
                keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
            >
                <ScrollView
                    ref={scrollViewRef}
                    style={styles.scrollView}
                    contentContainerStyle={styles.scrollContent}
                >
                    {/* Child Profile Form */}
                    <ChildProfileForm
                        ageMonths={chat.age_months}
                        domains={chat.domains}
                        notes={chat.notes}
                        onAgeChange={(age) => updateChat({ age_months: age })}
                        onDomainsChange={(domains) => updateChat({ domains })}
                        onNotesChange={(notes) => updateChat({ notes })}
                    />

                    {/* Generate Button */}
                    <Button
                        mode="contained"
                        onPress={handleGenerate}
                        loading={isGenerating}
                        disabled={!chat.age_months || !chat.domains || chat.domains.length === 0 || isGenerating}
                        style={styles.generateButton}
                        icon="auto-fix"
                    >
                        {isGenerating ? 'Generating Plan...' : 'Generate Intervention Plan'}
                    </Button>

                    {/* Plan Display */}
                    {chat.plan && <PlanDisplay plan={chat.plan} />}

                    {/* Chat Messages */}
                    {chat.messages && chat.messages.length > 0 && (
                        <ChatMessages messages={chat.messages} />
                    )}
                </ScrollView>

                {/* Chat Input (only show if plan exists) */}
                {chat.plan && (
                    <View style={styles.inputContainer}>
                        <VoiceControls
                            onTranscript={handleVoiceTranscript}
                            autoSpeak={autoSpeak}
                            onAutoSpeakChange={setAutoSpeak}
                            disabled={isSending}
                        />
                        <TextInput
                            style={styles.input}
                            mode="outlined"
                            placeholder="Ask a follow-up question..."
                            value={chatMessage}
                            onChangeText={setChatMessage}
                            disabled={isSending}
                            right={
                                <TextInput.Icon
                                    icon="send"
                                    onPress={handleSendMessage}
                                    disabled={isSending || !chatMessage.trim()}
                                />
                            }
                        />
                    </View>
                )}
            </KeyboardAvoidingView>

            <Portal>
                <Snackbar
                    visible={snackbar.visible}
                    onDismiss={() => setSnackbar({ ...snackbar, visible: false })}
                    duration={3000}
                >
                    {snackbar.message}
                </Snackbar>
            </Portal>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    flex: {
        flex: 1,
    },
    scrollView: {
        flex: 1,
    },
    scrollContent: {
        padding: spacing.md,
    },
    generateButton: {
        marginVertical: spacing.lg,
    },
    inputContainer: {
        padding: spacing.md,
        backgroundColor: '#ffffff',
        borderTopWidth: 1,
        borderTopColor: '#e0e0e0',
    },
    input: {
        marginTop: spacing.sm,
    },
});

export default ChatScreen;
