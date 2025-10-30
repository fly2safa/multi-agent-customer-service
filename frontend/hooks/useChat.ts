/**
 * useChat Hook - Manages chat state and API interactions
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { streamMessage, ChatMessage } from '@/lib/api';
import audioManager, { AgentType } from '@/lib/audioManager';

export interface UseChatOptions {
  sessionId?: string;
  onError?: (error: Error) => void;
}

/**
 * Map agent name from backend to AgentType for audio
 */
function mapAgentNameToType(agentName: string): AgentType | null {
  const normalized = agentName.toLowerCase();
  
  if (normalized.includes('billing')) {
    return 'billing';
  } else if (normalized.includes('technical')) {
    return 'technical';
  } else if (normalized.includes('policy')) {
    return 'policy';
  }
  
  return null;
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [sessionId, setSessionId] = useState<string | undefined>(options.sessionId);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load messages from sessionStorage on mount
  useEffect(() => {
    const storedMessages = sessionStorage.getItem('chat_messages');
    const storedSessionId = sessionStorage.getItem('chat_session_id');
    
    if (storedMessages) {
      try {
        setMessages(JSON.parse(storedMessages));
      } catch (e) {
        console.error('Error loading messages from storage:', e);
      }
    }
    
    if (storedSessionId && !sessionId) {
      setSessionId(storedSessionId);
    }
  }, [sessionId]);

  // Save messages to sessionStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      sessionStorage.setItem('chat_messages', JSON.stringify(messages));
    }
  }, [messages]);

  // Save sessionId to sessionStorage
  useEffect(() => {
    if (sessionId) {
      sessionStorage.setItem('chat_session_id', sessionId);
    }
  }, [sessionId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // Add user message immediately
      const userMessage: ChatMessage = {
        role: 'human',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      // Create placeholder for AI response
      const aiMessage: ChatMessage = {
        role: 'ai',
        content: '',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);

      try {
        // Stream the response
        let fullResponse = '';
        let currentAgent = '';

        for await (const chunk of streamMessage(content, sessionId)) {
          if (chunk.type === 'session' && chunk.session_id) {
            setSessionId(chunk.session_id);
          } else if (chunk.type === 'agent' && chunk.agent) {
            // Capture the agent name
            currentAgent = chunk.agent;
            
            // Update the AI message with the agent name
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                agent: currentAgent,
              };
              return updated;
            });
          } else if (chunk.type === 'chunk' && chunk.content) {
            fullResponse += chunk.content;
            
            // Play typing sound for the current agent
            if (currentAgent) {
              const agentType = mapAgentNameToType(currentAgent);
              if (agentType) {
                audioManager.playSound(agentType);
              }
            }
            
            // Update the last message (AI response)
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                ...updated[updated.length - 1],
                content: fullResponse,
                agent: currentAgent,
              };
              return updated;
            });
          } else if (chunk.type === 'error') {
            throw new Error(chunk.error || 'Unknown error');
          }
        }
      } catch (err) {
        const error = err as Error;
        setError(error);
        options.onError?.(error);

        // Remove the placeholder AI message on error
        setMessages((prev) => prev.slice(0, -1));
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, isLoading, options]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(undefined);
    sessionStorage.removeItem('chat_messages');
    sessionStorage.removeItem('chat_session_id');
  }, []);

  const retry = useCallback(() => {
    if (messages.length > 0) {
      const lastUserMessage = messages
        .slice()
        .reverse()
        .find((msg) => msg.role === 'human');

      if (lastUserMessage) {
        // Remove last AI response if it exists
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage.role === 'ai') {
            return prev.slice(0, -1);
          }
          return prev;
        });

        sendMessage(lastUserMessage.content);
      }
    }
  }, [messages, sendMessage]);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearChat,
    retry,
  };
}

