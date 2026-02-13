/**
 * Voice Service - Speech-to-Text and Text-to-Speech
 */

import Voice from '@react-native-voice/voice';
import Tts from 'react-native-tts';

class VoiceService {
    constructor() {
        this.isListening = false;
        this.transcript = '';

        // Initialize Voice Recognition
        Voice.onSpeechStart = this.onSpeechStart;
        Voice.onSpeechEnd = this.onSpeechEnd;
        Voice.onSpeechResults = this.onSpeechResults;
        Voice.onSpeechError = this.onSpeechError;

        // Initialize TTS
        Tts.setDefaultLanguage('en-US');
        Tts.setDefaultRate(0.5);
        Tts.setDefaultPitch(1.0);
    }

    // Voice Recognition Handlers
    onSpeechStart = (e) => {
        console.log('Speech started');
    };

    onSpeechEnd = (e) => {
        console.log('Speech ended');
    };

    onSpeechResults = (e) => {
        if (e.value && e.value.length > 0) {
            this.transcript = e.value[0];
        }
    };

    onSpeechError = (e) => {
        console.error('Speech error:', e.error);
    };

    // Start listening
    async startListening(callback) {
        try {
            this.transcript = '';
            this.resultCallback = callback;
            await Voice.start('en-US');
            this.isListening = true;
            return true;
        } catch (error) {
            console.error('Start listening error:', error);
            return false;
        }
    }

    // Stop listening
    async stopListening() {
        try {
            await Voice.stop();
            this.isListening = false;

            if (this.resultCallback && this.transcript) {
                this.resultCallback(this.transcript);
            }

            return this.transcript;
        } catch (error) {
            console.error('Stop listening error:', error);
            return '';
        }
    }

    // Cancel listening
    async cancelListening() {
        try {
            await Voice.cancel();
            this.isListening = false;
            this.transcript = '';
            return true;
        } catch (error) {
            console.error('Cancel listening error:', error);
            return false;
        }
    }

    // Check if available
    async isAvailable() {
        try {
            const available = await Voice.isAvailable();
            return available;
        } catch (error) {
            return false;
        }
    }

    // Text-to-Speech
    async speak(text, onStart, onDone) {
        try {
            if (onStart) {
                Tts.addEventListener('tts-start', onStart);
            }

            if (onDone) {
                Tts.addEventListener('tts-finish', onDone);
            }

            await Tts.speak(text);
            return true;
        } catch (error) {
            console.error('TTS error:', error);
            return false;
        }
    }

    // Stop speaking
    async stopSpeaking() {
        try {
            await Tts.stop();
            return true;
        } catch (error) {
            console.error('Stop TTS error:', error);
            return false;
        }
    }

    // Cleanup
    destroy() {
        Voice.destroy().then(Voice.removeAllListeners);
        Tts.removeAllListeners('tts-start');
        Tts.removeAllListeners('tts-finish');
    }
}

export default new VoiceService();
