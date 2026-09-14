import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '../types';
import { Bot, User, ChevronDown, ChevronUp } from 'lucide-react';
import clsx from 'clsx';

interface MessageBubbleProps {
  message: Message;
  isGenerating?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isGenerating }) => {
  const isUser = message.role === 'user';
  const [showSources, setShowSources] = useState(false);

  const formattedTime = new Date(message.timestamp).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className={clsx("flex w-full mb-6 animate-fade-in", isUser ? "justify-end" : "justify-start")}>
      <div className={clsx("flex max-w-[85%] md:max-w-[75%]", isUser ? "flex-row-reverse" : "flex-row")}>
        
        {/* Avatar */}
        <div className={clsx(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1",
          isUser ? "ml-3 bg-indigo-100 text-indigo-600" : "mr-3 bg-gradient-to-br from-indigo-500 to-blue-600 text-white shadow-sm"
        )}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
        </div>

        {/* Message Content */}
        <div className="flex flex-col min-w-0">
          <div className={clsx(
            "px-5 py-3.5 rounded-2xl",
            isUser 
              ? "bg-indigo-600 text-white rounded-tr-sm" 
              : "bg-white border border-gray-100 shadow-sm rounded-tl-sm text-gray-800"
          )}>
            {message.content ? (
              <div className={clsx("prose prose-sm max-w-none break-words", isUser ? "prose-invert" : "")}>
                {isUser ? (
                  <p className="whitespace-pre-wrap m-0 text-[15px] leading-relaxed">{message.content}</p>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
            ) : (
              isGenerating && !isUser && (
                <div className="flex items-center space-x-1 h-5 px-1">
                  <svg className="w-4 h-4 text-gray-400 typing-dot" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" /></svg>
                  <svg className="w-4 h-4 text-gray-400 typing-dot" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" /></svg>
                  <svg className="w-4 h-4 text-gray-400 typing-dot" viewBox="0 0 24 24"><circle cx="12" cy="12" r="6" /></svg>
                </div>
              )
            )}
          </div>

          {/* Sources Toggle */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-2 ml-1">
              <button 
                onClick={() => setShowSources(!showSources)}
                className="flex items-center text-xs text-gray-500 hover:text-indigo-600 transition-colors"
              >
                {showSources ? <ChevronUp className="w-3 h-3 mr-1" /> : <ChevronDown className="w-3 h-3 mr-1" />}
                {showSources ? 'Ẩn nguồn tham khảo' : `${message.sources.length} nguồn tham khảo`}
              </button>
              
              {showSources && (
                <div className="mt-2 space-y-2">
                  {message.sources.map((source, idx) => (
                    <div key={idx} className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-600">
                      <p className="font-semibold text-gray-700 mb-1">{source.metadata?.title || `Nguồn ${idx + 1}`}</p>
                      <p className="line-clamp-3">{source.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Timestamp */}
          <div className={clsx(
            "text-[10px] text-gray-400 mt-1.5 px-1",
            isUser ? "text-right" : "text-left"
          )}>
            {formattedTime}
          </div>
        </div>
      </div>
    </div>
  );
};
