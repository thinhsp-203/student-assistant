import React, { useState, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';
import clsx from 'clsx';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onStop: () => void;
  isGenerating: boolean;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  onStop, 
  isGenerating, 
  disabled 
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (input.trim() && !isGenerating && !disabled) {
      onSendMessage(input.trim());
      setInput('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-white border-t border-gray-200 p-4 w-full">
      <div className="max-w-4xl mx-auto relative flex items-end gap-2 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500 transition-all p-2 pr-3 shadow-sm">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Nhập câu hỏi của bạn... (Enter để gửi, Shift+Enter để xuống dòng)"
          className="flex-1 max-h-[120px] bg-transparent border-none focus:ring-0 resize-none py-2 px-3 text-gray-700 placeholder-gray-400 text-[15px] outline-none"
          rows={1}
        />
        
        <div className="flex-shrink-0 mb-1">
          {isGenerating ? (
            <button
              onClick={onStop}
              className="p-2 bg-red-100 hover:bg-red-200 text-red-600 rounded-xl transition-colors flex items-center justify-center w-10 h-10"
              title="Dừng tạo câu trả lời"
            >
              <Square className="w-5 h-5 fill-current" />
            </button>
          ) : (
            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || disabled}
              className={clsx(
                "p-2 rounded-xl transition-all flex items-center justify-center w-10 h-10",
                input.trim() && !disabled
                  ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              )}
              title="Gửi tin nhắn"
            >
              <Send className="w-5 h-5 ml-0.5" />
            </button>
          )}
        </div>
      </div>
      <div className="max-w-4xl mx-auto mt-2 text-center">
         <p className="text-[11px] text-gray-400">Trợ lý AI có thể mắc lỗi. Vui lòng kiểm tra lại các thông tin quan trọng.</p>
      </div>
    </div>
  );
};
