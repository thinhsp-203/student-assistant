import { Student, CompletedCourse, StudentProgress } from '../types';
import { apiGet } from './api';

export const studentService = {
  login: async (studentId: string): Promise<Student> => {
    // In a real app, this would be a proper authentication endpoint
    // For this prototype, we might just fetch the student profile
    // Assuming there's a login or profile endpoint:
    const response = await apiGet<{ student: Student }>(`/students/${studentId}`);
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
  }
};
