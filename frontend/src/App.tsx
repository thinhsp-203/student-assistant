import { useAuth } from './hooks/useAuth';
import { LoginPage } from './pages/LoginPage';
import { ChatPage } from './pages/ChatPage';
import { Loader2 } from 'lucide-react';

function App() {
  const { student, isLoggedIn, isLoading, login, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4 text-indigo-600">
          <Loader2 className="w-10 h-10 animate-spin" />
          <p className="font-medium">Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {isLoggedIn && student ? (
        <ChatPage student={student} onLogout={logout} />
      ) : (
        <LoginPage onLogin={login} isLoading={isLoading} />
      )}
    </>
  );
}

export default App;
