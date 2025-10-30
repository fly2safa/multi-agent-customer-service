/**
 * Audio Manager - Handles typing sound effects for AI agent responses
 * Supports different sounds for each agent with volume and mute controls
 */

export type AgentType = 'billing' | 'technical' | 'policy';

interface AudioManagerConfig {
  volume: number; // 0-100
  muted: boolean;
  minPlayInterval: number; // Minimum ms between sounds to prevent audio spam
}

class AudioManager {
  private audioContext: AudioContext | null = null;
  private soundBuffers: Map<AgentType, AudioBuffer | null> = new Map();
  private config: AudioManagerConfig = {
    volume: 50, // Default 50%
    muted: false,
    minPlayInterval: 50, // 50ms minimum between sounds
  };
  private lastPlayTime = 0;
  private isInitialized = false;
  private currentSource: AudioBufferSourceNode | null = null; // Track current playing sound

  /**
   * Initialize the audio manager (must be called after user interaction)
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Create AudioContext (requires user interaction in most browsers)
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // Load all agent sounds
      await this.loadSounds();
      
      this.isInitialized = true;
      console.log('Audio Manager initialized successfully');
    } catch (error) {
      console.warn('Audio Manager initialization failed:', error);
      // Graceful degradation - app continues without audio
    }
  }

  /**
   * Load sound files for all agents
   */
  private async loadSounds(): Promise<void> {
    const agents: AgentType[] = ['billing', 'technical', 'policy'];
    
    const loadPromises = agents.map(async (agent) => {
      try {
        const response = await fetch(`/sounds/${agent}-typing.mp3`);
        if (!response.ok) {
          console.warn(`Sound file not found: ${agent}-typing.mp3`);
          this.soundBuffers.set(agent, null);
          return;
        }
        
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await this.audioContext!.decodeAudioData(arrayBuffer);
        this.soundBuffers.set(agent, audioBuffer);
        console.log(`Loaded sound for ${agent} agent`);
      } catch (error) {
        console.warn(`Failed to load sound for ${agent} agent:`, error);
        this.soundBuffers.set(agent, null);
      }
    });

    await Promise.all(loadPromises);
  }

  /**
   * Play typing sound for a specific agent
   */
  playSound(agent: AgentType): void {
    if (!this.isInitialized || this.config.muted || !this.audioContext) {
      return;
    }

    // Rate limiting: prevent audio spam
    const now = Date.now();
    if (now - this.lastPlayTime < this.config.minPlayInterval) {
      return;
    }
    this.lastPlayTime = now;

    const buffer = this.soundBuffers.get(agent);
    if (!buffer) {
      return; // Sound not loaded or not available
    }

    try {
      // Stop previous sound if still playing
      this.stopCurrentSound();

      // Create source and gain nodes
      const source = this.audioContext.createBufferSource();
      const gainNode = this.audioContext.createGain();
      
      source.buffer = buffer;
      
      // Set volume (convert 0-100 to 0-1)
      gainNode.gain.value = this.config.volume / 100;
      
      // Connect: source -> gain -> destination
      source.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      // Track this source
      this.currentSource = source;
      
      // Clear reference when sound finishes naturally
      source.onended = () => {
        if (this.currentSource === source) {
          this.currentSource = null;
        }
      };
      
      // Play the sound
      source.start(0);
    } catch (error) {
      console.warn('Failed to play sound:', error);
    }
  }

  /**
   * Stop currently playing sound
   */
  private stopCurrentSound(): void {
    if (this.currentSource) {
      try {
        this.currentSource.stop();
      } catch (error) {
        // Sound already stopped, ignore error
      }
      this.currentSource = null;
    }
  }

  /**
   * Stop all sounds (public method for external use)
   */
  stopAllSounds(): void {
    this.stopCurrentSound();
  }

  /**
   * Set volume (0-100)
   */
  setVolume(volume: number): void {
    this.config.volume = Math.max(0, Math.min(100, volume));
  }

  /**
   * Get current volume (0-100)
   */
  getVolume(): number {
    return this.config.volume;
  }

  /**
   * Toggle mute on/off
   */
  toggleMute(): boolean {
    this.config.muted = !this.config.muted;
    return this.config.muted;
  }

  /**
   * Set mute state
   */
  setMuted(muted: boolean): void {
    this.config.muted = muted;
  }

  /**
   * Check if muted
   */
  isMuted(): boolean {
    return this.config.muted;
  }

  /**
   * Check if audio manager is ready
   */
  isReady(): boolean {
    return this.isInitialized;
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    this.stopCurrentSound();
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    this.soundBuffers.clear();
    this.isInitialized = false;
  }
}

// Singleton instance
const audioManager = new AudioManager();

export default audioManager;

