import React from 'react';
import { GraduationCap, LogOut, Menu } from 'lucide-react';
import { Student } from '../types';

interface HeaderProps {
  student: Student;
  onLogout: () => void;
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ student, onLogout, onToggleSidebar }) => {
  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 sm:px-6 shadow-sm">
      <div className="flex items-center gap-3">
        {onToggleSidebar && (
          <button 
            onClick={onToggleSidebar}
            className="md:hidden p-2 text-gray-500 hover:text-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-indigo-600 text-white">
          <GraduationCap className="w-6 h-6" />
        </div>
        <h1 className="font-semibold text-lg text-gray-800 hidden sm:block">
          Trợ lý Sinh viên Thông minh
        </h1>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex flex-col items-end">
          <span className="text-sm font-medium text-gray-900">{student.name}</span>
          <span className="text-xs text-gray-500">MSSV: {student.student_id}</span>
        </div>
        <button
          onClick={onLogout}
          className="flex items-center gap-2 p-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          title="Đăng xuất"
        >
          <LogOut className="w-5 h-5" />
          <span className="hidden sm:inline">Đăng xuất</span>
        </button>
      </div>
    </header>
  );
};
