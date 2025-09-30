import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { UploadPage } from './pages/UploadPage'
import { JournalPage } from './pages/JournalPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'

const dashboardPages = [
  { path: '/', title: 'Обзор', embedUrl: 'https://datalens.ru/txyv26ng090ge?_no_controls=1&tab=7g' },
  { path: '/dashboard-2', title: 'Регионы' },
  { path: '/dashboard-3', title: 'Время' },
]

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {dashboardPages.map(({ path, title, embedUrl }) => (
          <Route key={path} path={path} element={<DashboardPage title={title} embedUrl={embedUrl} />} />
        ))}
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/journal" element={<JournalPage />} />
      </Route>
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/register" element={<RegisterPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
