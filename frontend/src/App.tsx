import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { TestCases } from './pages/TestCases';
import { CreateTest } from './pages/CreateTest';
import { TestHistory } from './pages/TestHistory';
import { TestRunDetail } from './pages/TestRunDetail';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/test-cases" replace />} />
          <Route path="/test-cases" element={<TestCases />} />
          <Route path="/test-cases/:id" element={<TestRunDetail />} />
          <Route path="/create-test" element={<CreateTest />} />
          <Route path="/reports" element={<TestHistory />} />
          <Route path="/test-runs/:runId" element={<TestRunDetail />} />
          <Route path="/ai-navigation" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-foreground">AI Navigation</h1><p className="text-muted-foreground">Coming soon...</p></div>} />
          <Route path="/settings" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-foreground">Settings</h1><p className="text-muted-foreground">Coming soon...</p></div>} />
          <Route path="/analytics" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-foreground">Analytics</h1><p className="text-muted-foreground">Coming soon...</p></div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App; 