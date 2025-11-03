/**
 * MessageInput Component - User input for chat messages
 * Supports command history navigation with Up/Down arrow keys
 */

import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Send, Loader2 } from 'lucide-react';
import { ChatMessage } from '@/lib/api';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  messages?: ChatMessage[];
}

export function MessageInput({ onSend, disabled, messages = [] }: MessageInputProps) {
  const [input, setInput] = useState('');
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [draftMessage, setDraftMessage] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Extract user message history (only 'human' role messages)
  const userHistory = messages
    .filter((msg) => msg.role === 'human')
    .map((msg) => msg.content);

  // Auto-focus input when component mounts
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Auto-focus input when it becomes enabled (after response completes)
  useEffect(() => {
    if (!disabled) {
      inputRef.current?.focus();
    }
  }, [disabled]);

  // Reset history navigation when new message is sent
  useEffect(() => {
    setHistoryIndex(-1);
    setDraftMessage('');
  }, [messages.length]);

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
      setHistoryIndex(-1);
      setDraftMessage('');
      // Focus will happen automatically via useEffect when disabled changes
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    // Handle Enter key
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
      return;
    }

    // Handle Up Arrow - Navigate to previous messages
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      
      if (userHistory.length === 0) return;

      // Save current draft on first up arrow press
      if (historyIndex === -1) {
        setDraftMessage(input);
      }

      const newIndex = Math.min(historyIndex + 1, userHistory.length - 1);
      setHistoryIndex(newIndex);
      
      // Get message from end of array (most recent first)
      const message = userHistory[userHistory.length - 1 - newIndex];
      setInput(message);
      return;
    }

    // Handle Down Arrow - Navigate to newer messages
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      
      if (historyIndex === -1) return;

      const newIndex = historyIndex - 1;
      
      if (newIndex === -1) {
        // Restore draft message
        setInput(draftMessage);
        setHistoryIndex(-1);
        setDraftMessage('');
      } else {
        setHistoryIndex(newIndex);
        const message = userHistory[userHistory.length - 1 - newIndex];
        setInput(message);
      }
      return;
    }
  };

  return (
    <div className="border-t bg-background p-4">
      <div className="flex gap-2 max-w-4xl mx-auto">
        <Input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message here... (↑/↓ for history)"
          disabled={disabled}
          className="flex-1 border-2 border-gray-300 focus:border-blue-600 focus:ring-2 focus:ring-blue-500/30 focus:shadow-lg focus:shadow-blue-500/20 transition-all duration-200 text-blue-900 font-semibold placeholder:text-gray-400 dark:border-gray-600 dark:focus:border-blue-500 dark:text-blue-300"
        />
        <Button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          size="icon"
          className="bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg transition-all duration-200"
        >
          {disabled ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  );
}

