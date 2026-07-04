import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AICommandCenter from './pages/AICommandCenter';
import CityMap from './pages/CityMap';
import Analytics from './pages/Analytics';
import Reports from './pages/Reports';
import KnowledgeBase from './pages/KnowledgeBase';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1400px] mx-auto px-8 py-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/ai-command" element={<AICommandCenter />} />
              <Route path="/map" element={<CityMap />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/knowledge-base" element={<KnowledgeBase />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
