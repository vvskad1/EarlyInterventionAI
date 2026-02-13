/**
 * Voice Controls Component
 */

import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import { IconButton, useTheme } from 'react-native-paper';
import VoiceService from '../services/voice';
import { spacing } from '../config/theme';

const VoiceControls = ({
    onTranscript,
    autoSpeak,
    onAutoSpeakChange,
    disabled = false,
}) => {
    const theme = useTheme();
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);

    const handleMicPress = async () => {
        if (disabled) return;

        if (isListening) {
            // Stop listening
            const transcript = await VoiceService.stopListening();
            setIsListening(false);
            if (transcript && onTranscript) {
                onTranscript(transcript);
            }
        } else {
            // Start listening
            const available = await VoiceService.isAvailable();
            if (!available) {
                Alert.alert(
                    'Voice Recognition Unavailable',
                    'Voice recognition is not available on this device.'
                );
                return;
            }

            const success = await VoiceService.startListening((transcript) => {
                if (onTranscript) {
                    onTranscript(transcript);
                }
            });

            if (success) {
                setIsListening(true);
            } else {
                Alert.alert(
                    'Permission Required',
                    'Please enable microphone permission in settings.'
                );
            }
        }
    };

    const handleSpeakerPress = () => {
        if (onAutoSpeakChange) {
            onAutoSpeakChange(!autoSpeak);
        }
    };

    const handleStopSpeech = async () => {
        await VoiceService.stopSpeaking();
        setIsSpeaking(false);
    };

    return (
        <View style={styles.container}>
            {/* Microphone Button */}
            <IconButton
                icon={isListening ? 'microphone' : 'microphone-off'}
                size={24}
                iconColor={isListening ? theme.colors.error : theme.colors.onSurface}
                onPress={handleMicPress}
                disabled={disabled}
                style={[
                    styles.button,
                    isListening && styles.activeButton,
                ]}
            />

            {/* Speaker Button */}
            <IconButton
                icon={autoSpeak ? 'volume-high' : 'volume-off'}
                size={24}
                iconColor={autoSpeak ? theme.colors.primary : theme.colors.onSurface}
                onPress={handleSpeakerPress}
                disabled={disabled}
                style={styles.button}
            />

            {/* Stop Speech Button (only visible when speaking) */}
            {isSpeaking && (
                <IconButton
                    icon="stop"
                    size={24}
                    iconColor={theme.colors.error}
                    onPress={handleStopSpeech}
                    style={styles.button}
                />
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    button: {
        margin: 0,
    },
    activeButton: {
        backgroundColor: '#ffebee',
    },
});

export default VoiceControls;
