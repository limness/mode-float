import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { UploadPage } from './pages/UploadPage'
import { JournalPage } from './pages/JournalPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { ProtectedRoute } from './components/auth/ProtectedRoute'

const dashboardPages = [
  { path: '/', title: 'Обзор', embedUrl: 'https://ru.wikipedia.org/wiki/Dashboard', groups: ['operator', 'admin'] },
  { path: '/dashboard-2', title: 'Регионы', groups: ['operator', 'admin'] },
  { path: '/dashboard-3', title: 'Время', groups: ['operator', 'admin'] },
]

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {dashboardPages.map(({ path, title, embedUrl, groups }) => (
          <Route
            key={path}
            path={path}
            element={
              <ProtectedRoute groups={groups}>
                <DashboardPage title={title} embedUrl={embedUrl} />
              </ProtectedRoute>
            }
          />
        ))}
        <Route
          path="/upload"
          element={
            <ProtectedRoute groups={['admin']}>
              <UploadPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/journal"
          element={
            <ProtectedRoute groups={['admin']}>
              <JournalPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
