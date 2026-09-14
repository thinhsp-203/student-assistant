import React, { useEffect, useState } from 'react';
import { CheckCircle2, Loader2, LockKeyhole } from 'lucide-react';
import { AdvisingResponse } from '../types';
import { studentService } from '../services/studentService';

interface RecommendationPanelProps {
  studentId: string;
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ studentId }) => {
  const [data, setData] = useState<AdvisingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    studentService.getRecommendations(studentId)
      .then(result => { if (active) setData(result); })
      .catch(() => { if (active) setError('Chưa tải được đề xuất môn học.'); });
    return () => { active = false; };
  }, [studentId]);

  return (
    <section className="mt-6" aria-labelledby="recommendations-title">
      <h3 id="recommendations-title" className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">
        Gợi ý học kỳ tiếp theo
      </h3>
      {!data && !error && <Loader2 className="w-4 h-4 animate-spin text-indigo-500 mx-2" />}
      {error && <p className="text-xs text-red-600 px-2">{error}</p>}
      {data && (
        <div className="space-y-2">
          {data.eligible_courses.slice(0, 4).map(course => (
            <div key={course.course_id} className="rounded-lg border border-green-100 bg-green-50 p-2 text-xs">
              <div className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0" />
                <div><strong>{course.course_id}</strong> · {course.name}<br /><span className="text-gray-600">{course.credits} tín chỉ · {course.category}</span></div>
              </div>
            </div>
          ))}
          {data.blocked_courses.slice(0, 2).map(item => (
            <div key={item.course.course_id} className="rounded-lg border border-amber-100 bg-amber-50 p-2 text-xs text-amber-900">
              <div className="flex items-start gap-2">
                <LockKeyhole className="w-4 h-4 shrink-0" />
                <div><strong>{item.course.course_id}</strong> · thiếu {item.missing_prerequisites.join(', ')}</div>
              </div>
            </div>
          ))}
          {data.eligible_courses.length === 0 && data.blocked_courses.length === 0 &&
            <p className="text-xs text-gray-500 px-2">Chưa có môn phù hợp trong học kỳ này.</p>}
        </div>
      )}
    </section>
  );
};
