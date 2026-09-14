import React from 'react';
import { LoginForm } from '../components/LoginForm';
import { GraduationCap } from 'lucide-react';
import { Student } from '../types';

interface LoginPageProps {
  onLogin: (studentId: string) => Promise<Student>;
  isLoading: boolean;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin, isLoading }) => {
  return (
    <div className="min-h-screen chat-gradient flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-white/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-blue-400/20 rounded-full blur-3xl pointer-events-none"></div>
      
      <div className="w-full max-w-md z-10 flex flex-col items-center">
        <div className="flex items-center gap-3 mb-8 text-white animate-fade-in">
          <GraduationCap className="w-10 h-10" />
          <h1 className="text-3xl font-bold tracking-tight">Student Assistant</h1>
        </div>
        
        <div className="w-full animate-fade-in" style={{ animationDelay: '0.1s' }}>
          <LoginForm onLogin={onLogin} isLoading={isLoading} />
        </div>
      </div>
      
      <div className="absolute bottom-6 text-white/60 text-sm z-10">
        &copy; {new Date().getFullYear()} - Dự án AI Hỗ trợ Sinh viên
      </div>
    </div>
  );
};
