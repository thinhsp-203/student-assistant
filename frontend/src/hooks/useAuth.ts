import { useState, useEffect } from 'react';
import { Student } from '../types';
import { studentService } from '../services/studentService';

export function useAuth() {
  const [student, setStudent] = useState<Student | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const savedStudent = localStorage.getItem('studentData');
    if (savedStudent) {
      try {
        const parsed = JSON.parse(savedStudent);
        if (!parsed.name) {
          throw new Error("Invalid student data format");
        }
        if (typeof parsed.warnings === 'string') {
          try {
            parsed.warnings = JSON.parse(parsed.warnings);
          } catch {
            parsed.warnings = [];
          }
        } else if (!parsed.warnings) {
          parsed.warnings = [];
        }
        setStudent(parsed);
      } catch (e) {
        localStorage.removeItem('studentData');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (studentId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await studentService.login(studentId);
      setStudent(data);
      localStorage.setItem('studentData', JSON.stringify(data));
      return data;
    } catch (err: any) {
      setError(err.message || 'Failed to login');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setStudent(null);
    localStorage.removeItem('studentData');
  };

  return {
    student,
    isLoggedIn: !!student,
    isLoading,
    error,
    login,
    logout
  };
}
