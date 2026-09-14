import React from 'react';
import { BookOpen, FileText, Briefcase, Trash2 } from 'lucide-react';
import { Student, TopicMode } from '../types';
import { StudentProfile } from './StudentProfile';
import clsx from 'clsx';

interface SidebarProps {
  student: Student;
  topicMode: TopicMode;
  onTopicChange: (topic: TopicMode) => void;
  onClearHistory: () => void;
  isOpen: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  student, 
  topicMode, 
  onTopicChange,
  onClearHistory,
  isOpen 
}) => {
  const topics: { id: TopicMode; label: string; icon: React.ReactNode }[] = [
    { id: 'academic', label: 'Học tập', icon: <BookOpen className="w-5 h-5" /> },
    { id: 'admin', label: 'Hành chính', icon: <FileText className="w-5 h-5" /> },
    { id: 'career', label: 'Nghề nghiệp', icon: <Briefcase className="w-5 h-5" /> },
  ];

  return (
    <aside className={clsx(
      "fixed inset-y-0 left-0 z-20 w-72 bg-white border-r border-gray-200 flex flex-col h-[calc(100vh-4rem)] top-16 transition-transform duration-300 md:relative md:top-0 md:h-full md:translate-x-0",
      isOpen ? "translate-x-0" : "-translate-x-full"
    )}>
      <div className="p-4 flex-1 overflow-y-auto">
        <StudentProfile student={student} />
        
        <div className="mt-8">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">
            Chủ đề tư vấn
          </h3>
          <div className="space-y-1">
            {topics.map((topic) => (
              <button
                key={topic.id}
                onClick={() => onTopicChange(topic.id)}
                className={clsx(
                  "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors text-sm font-medium",
                  topicMode === topic.id
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                )}
              >
                {topic.icon}
                {topic.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onClearHistory}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Xóa lịch sử chat
        </button>
      </div>
    </aside>
  );
};
