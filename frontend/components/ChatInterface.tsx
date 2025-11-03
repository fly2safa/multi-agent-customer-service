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

      {/* Quick Access Agent Buttons */}
      <div className="flex-shrink-0 bg-gray-50 dark:bg-gray-900 border-b px-4 py-3">
        <div className="container mx-auto">
          <p className="text-xs text-muted-foreground mb-2 font-semibold">Quick Access - Try These Sample Queries:</p>
          <div className="flex gap-4 flex-wrap">
            {/* Billing Agent Button */}
            <div className="flex flex-col gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => sendMessage("What are your pricing plans?")}
                disabled={isLoading}
                className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border-emerald-300 hover:border-emerald-400 dark:bg-emerald-950/30 dark:text-emerald-400 dark:border-emerald-800 dark:hover:bg-emerald-950/50 font-semibold"
              >
                💰 Billing Support
              </Button>
              <div className="text-xs text-emerald-700 dark:text-emerald-400 px-1">
                <div className="font-medium italic">"What are your pricing plans?"</div>
                <div className="text-[10px] text-muted-foreground mt-0.5">Strategy: Hybrid RAG/CAG</div>
              </div>
            </div>

            {/* Technical Agent Button */}
            <div className="flex flex-col gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => sendMessage("How do I reset my password?")}
                disabled={isLoading}
                className="bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-300 hover:border-orange-400 dark:bg-orange-950/30 dark:text-orange-400 dark:border-orange-800 dark:hover:bg-orange-950/50 font-semibold"
              >
                🔧 Technical Support
              </Button>
              <div className="text-xs text-orange-700 dark:text-orange-400 px-1">
                <div className="font-medium italic">"How do I reset my password?"</div>
                <div className="text-[10px] text-muted-foreground mt-0.5">Strategy: Pure RAG</div>
              </div>
            </div>

            {/* Policy Agent Button */}
            <div className="flex flex-col gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => sendMessage("What's your privacy policy?")}
                disabled={isLoading}
                className="bg-purple-50 hover:bg-purple-100 text-purple-700 border-purple-300 hover:border-purple-400 dark:bg-purple-950/30 dark:text-purple-400 dark:border-purple-800 dark:hover:bg-purple-950/50 font-semibold"
              >
                📋 Policy & Compliance
              </Button>
              <div className="text-xs text-purple-700 dark:text-purple-400 px-1">
                <div className="font-medium italic">"What's your privacy policy?"</div>
                <div className="text-[10px] text-muted-foreground mt-0.5">Strategy: Pure CAG</div>
              </div>
            </div>
          </div>
        </div>
      </div>

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
        <MessageInput onSend={sendMessage} disabled={isLoading} messages={messages} />
      </div>
    </div>
  );
}

