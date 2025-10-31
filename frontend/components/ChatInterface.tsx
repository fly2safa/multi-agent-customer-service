/**
 * ChatInterface Component - Main chat container
 */

'use client';

import { useChat } from '@/hooks/useChat';
import { useTypingSound } from '@/hooks/useTypingSound';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { VolumeControl } from './VolumeControl';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Trash2, AlertCircle } from 'lucide-react';

export function ChatInterface() {
  const { messages, isLoading, error, sendMessage, clearChat, retry } = useChat({
    onError: (err) => {
      console.error('Chat error:', err);
    },
  });

  const { volume, setVolume, muted, toggleMute, isReady } = useTypingSound();

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header - Fixed at top */}
      <header className="flex-shrink-0 border-b bg-gradient-to-r from-blue-600 to-indigo-600 z-10 shadow-md">
        <div className="container flex h-16 items-center justify-between px-4">
          <div>
            <h1 className="text-xl font-bold text-white">Multi-Agent Customer Service</h1>
            <p className="text-sm text-blue-100">
              Powered by AI • {messages.length > 0 ? `${messages.length / 2} messages` : 'Start a conversation'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Volume Control */}
            {isReady && (
              <VolumeControl
                volume={volume}
                muted={muted}
                onVolumeChange={setVolume}
                onToggleMute={toggleMute}
              />
            )}
            {/* Clear Chat Button */}
            {messages.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={clearChat}
                disabled={isLoading}
                className="bg-white/10 hover:bg-white/20 text-white border-white/30 hover:border-white/50"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear Chat
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Messages - Scrollable area */}
      <div className="flex-1 overflow-y-auto scrollbar-visible">
        <MessageList messages={messages} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="flex-shrink-0 mx-4 mb-2">
          <Card className="bg-destructive/10 border-destructive/20 p-3">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error.message}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={retry}
                className="ml-auto"
              >
                Retry
              </Button>
            </div>
          </Card>
        </div>
      )}

      {/* Input - Fixed at bottom */}
      <div className="flex-shrink-0">
        <MessageInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

