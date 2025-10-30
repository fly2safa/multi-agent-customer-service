/**
 * VolumeControl Component - Volume slider with mute toggle
 */

'use client';

import { useState } from 'react';
import { Button } from './ui/button';
import { Volume2, VolumeX, Volume1 } from 'lucide-react';

interface VolumeControlProps {
  volume: number;
  muted: boolean;
  onVolumeChange: (volume: number) => void;
  onToggleMute: () => void;
}

export function VolumeControl({
  volume,
  muted,
  onVolumeChange,
  onToggleMute,
}: VolumeControlProps) {
  const [showSlider, setShowSlider] = useState(false);

  const getVolumeIcon = () => {
    if (muted || volume === 0) {
      return <VolumeX className="h-4 w-4" />;
    } else if (volume < 50) {
      return <Volume1 className="h-4 w-4" />;
    } else {
      return <Volume2 className="h-4 w-4" />;
    }
  };

  return (
    <div 
      className="relative"
      onMouseEnter={() => setShowSlider(true)}
      onMouseLeave={() => setShowSlider(false)}
    >
      {/* Volume Button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggleMute}
        title={muted ? 'Unmute typing sounds' : 'Mute typing sounds'}
      >
        {getVolumeIcon()}
      </Button>

      {/* Volume Slider - Appears on Hover */}
      {showSlider && (
        <div className="absolute right-0 top-full mt-1 bg-background border rounded-lg shadow-lg p-3 min-w-[200px] z-50">
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground whitespace-nowrap">
              Volume
            </span>
            <input
              type="range"
              min="0"
              max="100"
              value={muted ? 0 : volume}
              onChange={(e) => {
                const newVolume = parseInt(e.target.value, 10);
                onVolumeChange(newVolume);
                // Auto-unmute if user adjusts volume while muted
                if (muted && newVolume > 0) {
                  onToggleMute();
                }
              }}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500 dark:bg-gray-700"
              style={{
                background: `linear-gradient(to right, rgb(59, 130, 246) 0%, rgb(59, 130, 246) ${muted ? 0 : volume}%, rgb(229, 231, 235) ${muted ? 0 : volume}%, rgb(229, 231, 235) 100%)`,
              }}
            />
            <span className="text-xs text-muted-foreground font-mono min-w-[2.5rem] text-right">
              {muted ? '0' : volume}%
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Typing sound effect volume
          </p>
        </div>
      )}
    </div>
  );
}

