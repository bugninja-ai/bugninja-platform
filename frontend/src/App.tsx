import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import TestCases from './pages/TestCases';
import CreateTest from './pages/CreateTest';
import TestRuns from './pages/TestRuns';
import { TestRunDetail } from './pages/TestRunDetail';
import TestCaseDetail from './pages/TestCaseDetail';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<TestCases />} />
          <Route path="/create" element={<CreateTest />} />
          <Route path="/runs" element={<TestRuns />} />
          <Route path="/runs/:runId" element={<TestRunDetail />} />
          <Route path="/test-details/:id" element={<TestCaseDetail />} />
          <Route path="/dashboard" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-gray-900">Dashboard</h1><p className="text-gray-600">Coming soon...</p></div>} />
          <Route path="/analytics" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-gray-900">Analytics</h1><p className="text-gray-600">Coming soon...</p></div>} />
          <Route path="/settings" element={<div className="p-8 text-center"><h1 className="text-2xl font-bold text-gray-900">Settings</h1><p className="text-gray-600">Coming soon...</p></div>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App; 