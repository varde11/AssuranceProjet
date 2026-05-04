import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import NewAnalysis from './pages/NewAnalysis';
import History from './pages/History';
import PredictionDetail from './pages/PredictionDetail';


export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected — inside sidebar layout */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="/nouvelle-analyse" element={<NewAnalysis />} />
            <Route path="/historique"       element={<History />} />
            <Route path="/analyse/:id"      element={<PredictionDetail />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/nouvelle-analyse" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
