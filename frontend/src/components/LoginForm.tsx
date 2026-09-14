import React, { useState } from 'react';
import { GraduationCap, ArrowRight, Loader2 } from 'lucide-react';

interface LoginFormProps {
  onLogin: (studentId: string) => Promise<any>;
  isLoading: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin, isLoading }) => {
  const [studentId, setStudentId] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentId.trim()) {
      setError('Vui lòng nhập MSSV');
      return;
    }
    try {
      await onLogin(studentId.trim());
    } catch (err: any) {
      setError(err.message || 'Đăng nhập thất bại. Vui lòng kiểm tra lại MSSV.');
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
      <div className="p-8">
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center">
            <GraduationCap className="w-8 h-8 text-indigo-600" />
          </div>
        </div>
        
        <h2 className="text-2xl font-bold text-center text-gray-900 mb-2">Đăng nhập</h2>
        <p className="text-center text-gray-500 mb-8">Nhập MSSV để bắt đầu</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="studentId" className="block text-sm font-medium text-gray-700 mb-1">
              Mã số sinh viên (MSSV)
            </label>
            <input
              id="studentId"
              type="text"
              value={studentId}
              onChange={(e) => {
                setStudentId(e.target.value);
                setError('');
              }}
              disabled={isLoading}
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
              placeholder="Ví dụ: 20210001"
            />
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Đăng nhập
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Thử: <span className="font-medium text-indigo-600">20210001</span>, <span className="font-medium text-indigo-600">20210045</span>, <span className="font-medium text-indigo-600">20200112</span>
          </p>
        </div>
      </div>
      <div className="bg-gray-50 p-4 border-t border-gray-100 text-center">
        <p className="text-xs text-gray-500">Hệ thống Trợ lý AI dành riêng cho Sinh viên</p>
      </div>
    </div>
  );
};
