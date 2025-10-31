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
        'flex gap-3 p-4 rounded-lg transition-all duration-200',
        isUser 
          ? 'bg-blue-50 border border-blue-200 shadow-sm hover:shadow-md dark:bg-blue-950/20 dark:border-blue-800' 
          : 'bg-muted/50'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm',
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-secondary text-secondary-foreground'
        )}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      {/* Message content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className={cn(
            "font-semibold text-sm",
            isUser ? "text-blue-700 dark:text-blue-400" : ""
          )}>
            {isUser ? 'You' : (message.agent || 'AI Assistant')}
          </span>
          {message.timestamp && (
            <span className={cn(
              "text-xs",
              isUser ? "text-blue-600 dark:text-blue-500" : "text-muted-foreground"
            )}>
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className={cn(
          "text-sm whitespace-pre-wrap break-words",
          isUser ? "text-blue-800 font-medium dark:text-blue-300" : ""
        )}>
          {message.content || <span className={cn(
            "italic",
            isUser ? "text-blue-600 dark:text-blue-400" : "text-muted-foreground"
          )}>Thinking...</span>}
        </div>
      </div>
    </div>
  );
}

