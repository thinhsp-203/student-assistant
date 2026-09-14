import React from 'react';
import { TopicMode } from '../types';
import { BookOpen, FileText, Briefcase, HelpCircle } from 'lucide-react';

interface SuggestedQuestionsProps {
  topicMode: TopicMode;
  onSelect: (question: string) => void;
}

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({ topicMode, onSelect }) => {
  const suggestions: Record<TopicMode, {text: string, icon: React.ReactNode}[]> = {
    academic: [
      { text: "HK tới em nên đăng ký môn nào?", icon: <BookOpen className="w-4 h-4" /> },
      { text: "Môn tiên quyết của Trí tuệ nhân tạo là gì?", icon: <BookOpen className="w-4 h-4" /> },
      { text: "Điều kiện tốt nghiệp của ngành em?", icon: <HelpCircle className="w-4 h-4" /> },
      { text: "Em đang bị cảnh báo học vụ, phải làm sao?", icon: <HelpCircle className="w-4 h-4" /> },
    ],
    admin: [
      { text: "Xin giấy xác nhận sinh viên ở đâu?", icon: <FileText className="w-4 h-4" /> },
      { text: "Hạn đóng học phí học kỳ này khi nào?", icon: <FileText className="w-4 h-4" /> },
      { text: "Thủ tục bảo lưu kết quả học tập?", icon: <FileText className="w-4 h-4" /> },
      { text: "Làm sao để đăng ký ký túc xá?", icon: <FileText className="w-4 h-4" /> },
    ],
    career: [
      { text: "Ngành của em ra trường làm gì?", icon: <Briefcase className="w-4 h-4" /> },
      { text: "Em nên học thêm kỹ năng gì để dễ xin việc?", icon: <Briefcase className="w-4 h-4" /> },
      { text: "Mức lương trung bình ngành em là bao nhiêu?", icon: <Briefcase className="w-4 h-4" /> },
      { text: "Nên tìm chỗ thực tập ở đâu?", icon: <Briefcase className="w-4 h-4" /> },
    ]
  };

  const currentSuggestions = suggestions[topicMode];

  return (
    <div className="w-full max-w-3xl mx-auto mt-8 px-4 animate-fade-in">
      <h3 className="text-center text-sm font-medium text-gray-500 mb-4">Gợi ý câu hỏi</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {currentSuggestions.map((item, index) => (
          <button
            key={index}
            onClick={() => onSelect(item.text)}
            className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-indigo-300 hover:shadow-md transition-all text-left text-sm text-gray-700 hover:text-indigo-700"
          >
            <div className="text-indigo-500 shrink-0">
              {item.icon}
            </div>
            <span>{item.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
