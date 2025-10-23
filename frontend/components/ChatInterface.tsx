/**
 * ChatInterface Component - Main chat container
 */

'use client';

import { useChat } from '@/hooks/useChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Trash2, AlertCircle } from 'lucide-react';

export function ChatInterface() {
  const { messages, isLoading, error, sendMessage, clearChat, retry } = useChat({
    onError: (err) => {
      console.error('Chat error:', err);
    },
  });

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div>
            <h1 className="text-xl font-bold">Multi-Agent Customer Service</h1>
            <p className="text-sm text-muted-foreground">
              Powered by AI • {messages.length > 0 ? `${messages.length / 2} messages` : 'Start a conversation'}
            </p>
          </div>
          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearChat}
              disabled={isLoading}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Chat
            </Button>
          )}
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1">
        <MessageList messages={messages} />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-4 mb-2">
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

      {/* Input */}
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}

