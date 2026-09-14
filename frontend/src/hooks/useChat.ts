import { useState, useRef, useCallback } from 'react';
import { Message, Source } from '../types';
import { chatService } from '../services/chatService';

export function useChat(studentId: string | undefined, topicMode: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!studentId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };

    const assistantMessageId = (Date.now() + 1).toString();
    const initialAssistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage, initialAssistantMessage]);
    setIsGenerating(true);

    abortControllerRef.current = new AbortController();

    try {
      await chatService.streamChatResponse(
        content,
        messages, // Send history (doesn't include the newly added ones yet to match the API expectation of previous context)
        studentId,
        topicMode,
        abortControllerRef.current.signal,
        (chunk: string) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        },
        (sources: Source[]) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, sources }
                : msg
            )
          );
        },
        () => {
          setIsGenerating(false);
          abortControllerRef.current = null;
        },
        (error: Error) => {
          console.error("Chat error:", error);
          setMessages(prev => 
            prev.map(msg => 
              msg.id === assistantMessageId 
                ? { ...msg, content: msg.content + "\n\n**Lỗi:** " + error.message }
                : msg
            )
          );
          setIsGenerating(false);
          abortControllerRef.current = null;
        }
      );
    } catch (e) {
      setIsGenerating(false);
    }
  }, [messages, studentId, topicMode]);

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsGenerating(false);
    }
  }, []);

  const clearHistory = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isGenerating,
    sendMessage,
    stopGeneration,
    clearHistory
  };
}
