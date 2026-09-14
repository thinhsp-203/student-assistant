import React from 'react';
import { Student } from '../types';
import clsx from 'clsx';
import { AlertTriangle } from 'lucide-react';

interface StudentProfileProps {
  student: Student;
}

export const StudentProfile: React.FC<StudentProfileProps> = ({ student }) => {
  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  };

  const getGpaColor = (gpa: number) => {
    if (gpa >= 3.2) return 'bg-green-100 text-green-800 border-green-200';
    if (gpa >= 2.5) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const progressPercentage = Math.round((student.total_credits_completed / student.total_credits_required) * 100) || 0;

  return (
    <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
      <div className="flex items-center gap-4 mb-4">
        <div className="w-12 h-12 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold text-lg">
          {getInitials(student.name)}
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 line-clamp-1" title={student.name}>{student.name}</h3>
          <p className="text-xs text-gray-500">{student.student_id}</p>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-xs text-gray-500 mb-1">Ngành học</p>
          <p className="text-sm font-medium text-gray-800">{student.major}</p>
        </div>

        <div className="flex justify-between items-center">
          <div>
            <p className="text-xs text-gray-500 mb-1">Học kỳ</p>
            <p className="text-sm font-medium text-gray-800">HK{student.current_semester}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500 mb-1">GPA</p>
            <span className={clsx("text-xs font-bold px-2 py-1 rounded-md border", getGpaColor(student.gpa))}>
              {student.gpa.toFixed(2)}
            </span>
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-500">Tiến độ tín chỉ</span>
            <span className="font-medium text-gray-700">{student.total_credits_completed}/{student.total_credits_required}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-500" 
              style={{ width: `${Math.min(progressPercentage, 100)}%` }}
            ></div>
          </div>
        </div>

        {student.warnings && student.warnings.length > 0 && (
          <div className="mt-3">
            {student.warnings.map((warning, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-red-700 bg-red-50 p-2 rounded-lg border border-red-100">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{warning}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
