import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './app/layout/Layout';
import TestCasesPage from './features/test-cases/TestCasesPage';
import CreateTestPage from './features/test-cases/CreateTestPage';
import TestRunsPage from './features/test-runs/TestRunsPage';
import TestRunDetailPage from './features/test-run-detail/TestRunDetailPage';
import TestCaseDetailPage from './features/test-cases/TestCaseDetailPage';
import SettingsPage from './features/settings/SettingsPage';


function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<TestCasesPage />} />
          <Route path="/create" element={<CreateTestPage />} />
          <Route path="/runs" element={<TestRunsPage />} />
          <Route path="/runs/:runId" element={<TestRunDetailPage />} />
          <Route path="/test-details/:id" element={<TestCaseDetailPage />} />
          <Route path="/dashboard" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-gray-900">Dashboard</h1><p className="text-gray-600">Coming soon...</p></div>} />
          <Route path="/analytics" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-gray-900">Analytics</h1><p className="text-gray-600">Coming soon...</p></div>} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App; 