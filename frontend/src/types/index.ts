export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

export interface Source {
  content: string;
  metadata: Record<string, string>;
}

export interface Student {
  student_id: string;
  name: string;
  email: string;
  major: string;
  intake_year: number;
  current_semester: number;
  gpa: number;
  total_credits_completed: number;
  total_credits_required: number;
  status: string;
  warnings: string[];
}

export interface CompletedCourse {
  course_id: string;
  course_name: string;
  credits: number;
  grade: string;
  grade_point: number;
  semester: number;
}

export interface StudentProgress {
  completion_percentage: number;
  completed_courses: CompletedCourse[];
  remaining_courses: Array<{course_id: string; course_name: string; credits: number}>;
  eligible_courses: Array<{course_id: string; course_name: string; credits: number}>;
}

export interface CourseRecommendation {
  course_id: string;
  name: string;
  credits: number;
  category: string;
  suggested_semester: number;
  prerequisites: string[];
  description?: string;
}

export interface AdvisingResponse {
  target_semester: number;
  eligible_courses: CourseRecommendation[];
  blocked_courses: Array<{
    course: CourseRecommendation;
    missing_prerequisites: string[];
    reason: string;
  }>;
}

export type TopicMode = 'academic' | 'admin' | 'career';
