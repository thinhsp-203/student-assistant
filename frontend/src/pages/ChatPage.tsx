import React, { useState } from 'react';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';
import { ChatBox } from '../components/ChatBox';
import { Student, TopicMode } from '../types';
import { useChat } from '../hooks/useChat';

interface ChatPageProps {
  student: Student;
  onLogout: () => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ student, onLogout }) => {
  const [topicMode, setTopicMode] = useState<TopicMode>('academic');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const { 
    messages, 
    isGenerating, 
    sendMessage, 
    stopGeneration, 
    clearHistory 
  } = useChat(student.student_id, topicMode);

  const handleTopicChange = (newTopic: TopicMode) => {
    setTopicMode(newTopic);
    if (window.innerWidth < 768) {
      setIsSidebarOpen(false); // Close sidebar on mobile after selection
    }
  };

  const handleToggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      <Header 
        student={student} 
        onLogout={onLogout} 
        onToggleSidebar={handleToggleSidebar} 
      />
      
      <div className="flex flex-1 overflow-hidden relative">
        {/* Overlay for mobile sidebar */}
        {isSidebarOpen && (
          <div 
            className="fixed inset-0 bg-black/20 z-10 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
        
        <Sidebar 
          student={student}
          topicMode={topicMode}
          onTopicChange={handleTopicChange}
          onClearHistory={clearHistory}
          isOpen={isSidebarOpen}
        />
        
        <main className="flex-1 flex flex-col min-w-0 h-full">
          <ChatBox 
            messages={messages}
            isGenerating={isGenerating}
            topicMode={topicMode}
            onSendMessage={sendMessage}
            onStop={stopGeneration}
          />
        </main>
      </div>
    </div>
  );
};
