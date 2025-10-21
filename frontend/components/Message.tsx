/**
 * Message Component - Displays individual chat messages
 */

import { ChatMessage } from '@/lib/api';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MessageProps {
  message: ChatMessage;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'human';

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-lg',
        isUser ? 'bg-primary/5' : 'bg-muted/50'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'
        )}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Message content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-sm">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          {message.timestamp && (
            <span className="text-xs text-muted-foreground">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="text-sm whitespace-pre-wrap break-words">
          {message.content || <span className="text-muted-foreground italic">Thinking...</span>}
        </div>
      </div>
    </div>
  );
}

