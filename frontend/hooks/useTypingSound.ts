/**
 * useTypingSound Hook - React hook for managing typing sound effects
 * Provides easy integration with the AudioManager
 */

import { useEffect, useState, useCallback } from 'react';
import audioManager, { AgentType } from '@/lib/audioManager';

export interface TypingSoundControls {
  playSound: (agent: AgentType) => void;
  stopSounds: () => void;
  volume: number;
  setVolume: (volume: number) => void;
  muted: boolean;
  toggleMute: () => void;
  isReady: boolean;
}

/**
 * Hook for managing typing sound effects
 * Automatically initializes the audio manager on mount
 */
export function useTypingSound(): TypingSoundControls {
  const [volume, setVolumeState] = useState(audioManager.getVolume());
  const [muted, setMutedState] = useState(audioManager.isMuted());
  const [isReady, setIsReady] = useState(audioManager.isReady());

  // Initialize audio manager on mount
  useEffect(() => {
    const initAudio = async () => {
      await audioManager.initialize();
      setIsReady(audioManager.isReady());
    };

    // Initialize on user interaction (required by browsers)
    // Try immediate initialization, but also set up for user interaction
    initAudio();

    // Cleanup on unmount
    return () => {
      // Don't cleanup audioManager as it's a singleton used across the app
      // It will be cleaned up when the window closes
    };
  }, []);

  /**
   * Play typing sound for a specific agent
   */
  const playSound = useCallback((agent: AgentType) => {
    audioManager.playSound(agent);
  }, []);

  /**
   * Stop all currently playing sounds
   */
  const stopSounds = useCallback(() => {
    audioManager.stopAllSounds();
  }, []);

  /**
   * Set volume (0-100)
   */
  const setVolume = useCallback((newVolume: number) => {
    audioManager.setVolume(newVolume);
    setVolumeState(newVolume);
    
    // Persist to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('typingSound_volume', newVolume.toString());
    }
  }, []);

  /**
   * Toggle mute on/off
   */
  const toggleMute = useCallback(() => {
    const newMuted = audioManager.toggleMute();
    setMutedState(newMuted);
    
    // Persist to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('typingSound_muted', newMuted.toString());
    }
  }, []);

  // Load preferences from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedVolume = localStorage.getItem('typingSound_volume');
      if (savedVolume) {
        const vol = parseInt(savedVolume, 10);
        audioManager.setVolume(vol);
        setVolumeState(vol);
      }

      const savedMuted = localStorage.getItem('typingSound_muted');
      if (savedMuted) {
        const mute = savedMuted === 'true';
        audioManager.setMuted(mute);
        setMutedState(mute);
      }
    }
  }, []);

  return {
    playSound,
    stopSounds,
    volume,
    setVolume,
    muted,
    toggleMute,
    isReady,
  };
}

