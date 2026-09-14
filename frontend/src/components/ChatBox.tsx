import React, { useRef, useEffect } from 'react';
import { Message, TopicMode } from '../types';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { SuggestedQuestions } from './SuggestedQuestions';
import { Bot } from 'lucide-react';

interface ChatBoxProps {
  messages: Message[];
  isGenerating: boolean;
  topicMode: TopicMode;
  onSendMessage: (content: string) => void;
  onStop: () => void;
}

export const ChatBox: React.FC<ChatBoxProps> = ({
  messages,
  isGenerating,
  topicMode,
  onSendMessage,
  onStop
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages arrive or content changes
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    // Simple scroll to bottom logic. For production, you'd want to check if user has manually scrolled up.
    container.scrollTop = container.scrollHeight;
  }, [messages]);

  const getTopicGreeting = () => {
    switch (topicMode) {
      case 'academic': return 'Chào bạn! Mình có thể giúp gì cho bạn về vấn đề học tập, đăng ký môn học hay điểm số?';
      case 'admin': return 'Chào bạn! Bạn cần hỗ trợ thông tin gì về thủ tục hành chính, giấy tờ hay học phí?';
      case 'career': return 'Chào bạn! Bạn có thắc mắc gì về định hướng nghề nghiệp, kỹ năng hay thực tập không?';
      default: return 'Chào bạn! Mình có thể giúp gì cho bạn hôm nay?';
    }
  };

  return (
    <div className="flex flex-col flex-1 h-full bg-white relative">
      {/* Messages Area */}
      <div 
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-4 sm:p-6 scroll-smooth"
      >
        <div className="max-w-4xl mx-auto w-full">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center min-h-[60vh]">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg mb-6">
                <Bot className="w-8 h-8" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-800 mb-2">Trợ lý Sinh viên</h2>
              <p className="text-gray-500 text-center max-w-md mb-8">
                {getTopicGreeting()}
              </p>
              
              <SuggestedQuestions 
                topicMode={topicMode} 
                onSelect={onSendMessage} 
              />
            </div>
          ) : (
            <div className="pb-4">
              {messages.map((msg, idx) => (
                <MessageBubble 
                  key={msg.id || idx} 
                  message={msg} 
                  isGenerating={isGenerating && idx === messages.length - 1} 
                />
              ))}
              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <ChatInput 
        onSendMessage={onSendMessage}
        onStop={onStop}
        isGenerating={isGenerating}
      />
    </div>
  );
};
