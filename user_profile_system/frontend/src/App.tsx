import React from 'react';
import ProfilePage from './components/ProfilePage';
import './App.css';

function App() {
  // For demo purposes, using a hardcoded user ID
  // In a real app, this would come from authentication context
  const currentUserId = 'demo-user-123';
  const isOwnProfile = true;

  return (
    <div className="App">
      <ProfilePage userId={currentUserId} isOwnProfile={isOwnProfile} />
    </div>
  );
}

export default App;