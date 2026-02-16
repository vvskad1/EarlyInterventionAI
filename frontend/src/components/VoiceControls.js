import React, { useState, useEffect, useRef } from 'react';
import { IconButton, Tooltip, Box } from '@mui/material';
import { Mic, MicOff, VolumeUp, VolumeOff, Stop } from '@mui/icons-material';

/**
 * VoiceControls Component
 * Provides speech-to-text and text-to-speech controls using Web Speech API
 * 
 * Features:
 * - Speech Recognition: Click mic to speak, text fills input
 * - Speech Synthesis: Toggle to auto-read responses aloud
 */
function VoiceControls({ 
  onTranscript,
  autoSpeak = false,
  onAutoSpeakChange,
  disabled = false,
  onSendMessage, // Callback to send message when mic is released
  isSpeaking = false, // Indicates if TTS is currently speaking
  onStopSpeech, // Callback when user stops TTS
}) {
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const [shouldListen, setShouldListen] = useState(false); // Track if user wants to keep listening
  const recognitionRef = useRef(null);
  const sessionTranscriptRef = useRef(''); // Transcript for current recognition session
  const accumulatedTranscriptRef = useRef(''); // All accumulated transcript across sessions

  // Initialize Speech Recognition
  useEffect(() => {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const SpeechSynthesis = window.speechSynthesis;
    
    if (!SpeechRecognition || !SpeechSynthesis) {
      setSpeechSupported(false);
      console.warn('Web Speech API not supported in this browser');
      return;
    }

    // Initialize Speech Recognition
    const recognition = new SpeechRecognition();
    recognition.continuous = true; // Keep listening until manually stopped
    recognition.interimResults = true; // Show results as user speaks
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let sessionFinal = '';
      let interimTranscript = '';
      
      // Process all results from this session
      for (let i = 0; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          sessionFinal += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }
      
      // Update session transcript with final results
      sessionTranscriptRef.current = sessionFinal;
      
      // Send complete transcript: accumulated from previous sessions + current session
      const completeTranscript = accumulatedTranscriptRef.current + sessionFinal + interimTranscript;
      if (onTranscript && completeTranscript.trim()) {
        onTranscript(completeTranscript.trim());
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      if (event.error === 'not-allowed') {
        alert('Microphone permission denied. Please allow microphone access to use speech input.');
        setIsListening(false);
      } else if (event.error === 'no-speech') {
        // User didn't speak - this is fine, just log it
        console.log('No speech detected');
      } else if (event.error === 'aborted') {
        // Recognition was aborted
        console.log('Recognition aborted');
      }
    };

    recognition.onend = () => {
      // Save session transcript to accumulated before restarting
      if (sessionTranscriptRef.current) {
        accumulatedTranscriptRef.current += sessionTranscriptRef.current;
        sessionTranscriptRef.current = '';
      }
      
      // If user still wants to listen (didn't manually stop) and AI is not speaking, restart immediately
      if (shouldListen && !isSpeaking) {
        console.log('Recognition ended, restarting...');
        // Keep isListening true for visual continuity
        setTimeout(() => {
          try {
            recognitionRef.current?.start();
          } catch (error) {
            console.error('Failed to restart recognition:', error);
            setIsListening(false);
          }
        }, 100); // Small delay before restart
      } else {
        // Only set to false if we're actually stopping
        setIsListening(false);
      }
    };

    recognitionRef.current = recognition;

    // Cleanup
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          // Ignore cleanup errors
        }
      }
    };
  }, [onTranscript, shouldListen, isSpeaking]); // Add dependencies

  // Pause recognition when AI starts speaking, resume when done
  useEffect(() => {
    if (!recognitionRef.current) return;

    if (isSpeaking && isListening) {
      // AI started speaking, pause recognition
      console.log('Pausing recognition while AI speaks');
      try {
        recognitionRef.current.stop();
      } catch (error) {
        console.error('Failed to pause recognition:', error);
      }
    } else if (!isSpeaking && shouldListen && !isListening) {
      // AI finished speaking, resume if user wants to listen
      console.log('Resuming recognition after AI finished speaking');
      setTimeout(() => {
        try {
          recognitionRef.current?.start();
        } catch (error) {
          console.error('Failed to resume recognition:', error);
        }
      }, 300); // Delay to ensure TTS fully stopped
    }
  }, [isSpeaking, isListening, shouldListen]);

  // Handle microphone button click (toggle start/stop)
  const handleMicClick = () => {
    if (!speechSupported || disabled) return;

    if (isListening || shouldListen) {
      // Stop listening (transcript remains in message box for review)
      setShouldListen(false);
      
      try {
        recognitionRef.current?.stop();
      } catch (error) {
        console.error('Failed to stop speech recognition:', error);
      }
      
      setIsListening(false);
      
      // Clear both transcript refs for next recording
      sessionTranscriptRef.current = '';
      accumulatedTranscriptRef.current = '';
    } else {
      // Start listening
      setShouldListen(true);
      
      // Reset transcripts for new recording
      sessionTranscriptRef.current = '';
      accumulatedTranscriptRef.current = '';
      
      try {
        recognitionRef.current?.start();
      } catch (error) {
        // Ignore if already started
        if (error.name !== 'InvalidStateError') {
          console.error('Failed to start speech recognition:', error);
        }
      }
    }
  };

  // Handle speaker toggle
  const handleSpeakerToggle = () => {
    if (onAutoSpeakChange) {
      onAutoSpeakChange(!autoSpeak);
    }
  };

  // Handle stopping ongoing speech
  const handleStopSpeech = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    // Immediately notify parent to reset isSpeaking state
    if (onStopSpeech) {
      onStopSpeech();
    }
  };

  // Stop any ongoing speech when component unmounts
  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!speechSupported) {
    return null; // Don't render if not supported
  }

  return (
    <Box sx={{ display: 'flex', gap: 0.5 }}>
      {/* Speech-to-Text (Microphone) - Click to start, click again to stop */}
      <Tooltip title={(isListening || shouldListen) ? "Click to stop recording" : "Click to speak"}>
        <span>
          <IconButton
            onClick={handleMicClick}
            disabled={disabled}
            size="small"
            sx={{
              color: (isListening || shouldListen) ? 'error.main' : 'text.secondary',
              animation: (isListening || shouldListen) ? 'pulse 1.5s ease-in-out infinite' : 'none',
              '@keyframes pulse': {
                '0%': { opacity: 1 },
                '50%': { opacity: 0.5 },
                '100%': { opacity: 1 },
              },
              '&:hover': {
                bgcolor: (isListening || shouldListen) ? 'error.light' : 'action.hover',
              },
            }}
          >
            {(isListening || shouldListen) ? <Mic /> : <MicOff />}
          </IconButton>
        </span>
      </Tooltip>

      {/* Text-to-Speech (Speaker) */}
      <Tooltip title={autoSpeak ? "Auto-read responses: ON" : "Auto-read responses: OFF"}>
        <span>
          <IconButton
            onClick={handleSpeakerToggle}
            disabled={disabled}
            size="small"
            sx={{
              color: autoSpeak ? 'primary.main' : 'text.secondary',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
          >
            {autoSpeak ? <VolumeUp /> : <VolumeOff />}
          </IconButton>
        </span>
      </Tooltip>

      {/* Stop Speech Button - shows when AI is speaking */}
      {isSpeaking && (
        <Tooltip title="Stop voice playback">
          <span>
            <IconButton
              onClick={handleStopSpeech}
              size="small"
              sx={{
                color: 'error.main',
                animation: 'pulse 1.5s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.6 },
                  '100%': { opacity: 1 },
                },
                '&:hover': {
                  bgcolor: 'error.light',
                },
              }}
            >
              <Stop />
            </IconButton>
          </span>
        </Tooltip>
      )}
    </Box>
  );
}

// Hook for text-to-speech functionality
export function useSpeechSynthesis() {
  const isSpeakingRef = useRef(false);

  const speak = (text, onStart, onEnd) => {
    if (!window.speechSynthesis || !text) return;

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 1.0; // Normal speed
    utterance.pitch = 1.0; // Normal pitch
    utterance.volume = 1.0; // Max volume

    utterance.onstart = () => {
      isSpeakingRef.current = true;
      if (onStart) onStart();
    };

    utterance.onend = () => {
      isSpeakingRef.current = false;
      if (onEnd) onEnd();
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      isSpeakingRef.current = false;
      if (onEnd) onEnd();
    };

    window.speechSynthesis.speak(utterance);
  };

  const cancel = (onEnd) => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      isSpeakingRef.current = false;
      if (onEnd) onEnd();
    }
  };

  const isSpeaking = () => isSpeakingRef.current;

  return { speak, cancel, isSpeaking };
}

export default VoiceControls;
