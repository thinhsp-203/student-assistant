import { Student, CompletedCourse, StudentProgress, AdvisingResponse } from '../types';
import { apiGet, apiPost } from './api';

export const studentService = {
  login: async (studentId: string, password?: string): Promise<Student> => {
    const response = await apiPost<{ access_token: string; student: Student }>(
      '/students/login',
      { student_id: studentId, ...(password ? { password } : {}) }
    );
    localStorage.setItem('accessToken', response.access_token);
    const student = response.student;
    
    // Parse warnings if they come as a string from the backend SQLite DB
    if (typeof student.warnings === 'string') {
      try {
        student.warnings = JSON.parse(student.warnings);
      } catch (e) {
        student.warnings = [];
      }
    } else if (!student.warnings) {
      student.warnings = [];
    }
    
    return student;
  },

  getTranscript: async (studentId: string): Promise<CompletedCourse[]> => {
    return apiGet<CompletedCourse[]>(`/students/${studentId}/transcript`);
  },

  getProgress: async (studentId: string): Promise<StudentProgress> => {
    return apiGet<StudentProgress>(`/students/${studentId}/progress`);
  },

  getRecommendations: async (studentId: string): Promise<AdvisingResponse> => {
    return apiGet<AdvisingResponse>(`/advising/${studentId}/recommendations`);
  }
};
