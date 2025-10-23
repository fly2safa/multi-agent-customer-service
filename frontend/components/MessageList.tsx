/**
 * MessageList Component - Displays conversation history
 */

import { useEffect, useRef } from 'react';
import { ChatMessage as ChatMessageType } from '@/lib/api';
import { Message } from './Message';

interface MessageListProps {
  messages: ChatMessageType[];
}

export function MessageList({ messages }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-8">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-2">Welcome to AI Customer Service</h2>
          <p className="text-muted-foreground mb-4">
            Ask me anything about pricing, technical support, or our policies.
          </p>
          <div className="text-sm text-muted-foreground space-y-1">
            <p>Try asking:</p>
            <ul className="list-none space-y-1">
              <li>• "What are your pricing plans?"</li>
              <li>• "How do I reset my password?"</li>
              <li>• "What's your privacy policy?"</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div ref={scrollRef} className="h-full overflow-y-auto scrollbar-visible">
      <div className="space-y-4 p-4">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
}

