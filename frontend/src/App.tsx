import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { UploadPage } from './pages/UploadPage'
import { JournalPage } from './pages/JournalPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { ProtectedRoute } from './components/auth/ProtectedRoute'

const normalizeEmbedId = (value: string | undefined) => {
  const trimmed = value?.trim()
  return trimmed ? trimmed : undefined
}

const DATALENS_IDS: Record<string, string | undefined> = {
  overview: normalizeEmbedId(import.meta.env.VITE_DATALENS_OVERVIEW_ID) ?? 'qu4h5tflyj82b',
  regions: normalizeEmbedId(import.meta.env.VITE_DATALENS_REGIONS_ID) ?? 'w2ih53uscykah',
  time: normalizeEmbedId(import.meta.env.VITE_DATALENS_TIME_ID) ?? '6csrckp9k2tir',
}

const DEFAULT_EMBED_TTL = 600
const DEFAULT_EMBED_PARAMS: Record<string, string | string[]> | undefined = undefined

const dashboardPages: Array<{
  path: string
  title: string
  embedId?: string
  embedUrl?: string
  embedTtlSeconds?: number
  embedParams?: Record<string, string | string[]>
  groups: string[]
}> = [
  {
    path: '/',
    title: 'Обзор',
    embedId: DATALENS_IDS.overview,
    embedTtlSeconds: DEFAULT_EMBED_TTL,
    embedParams: DEFAULT_EMBED_PARAMS,
    groups: ['operator', 'admin'],
  },
  {
    path: '/dashboard-2',
    title: 'Регионы',
    embedId: DATALENS_IDS.regions,
    embedTtlSeconds: DEFAULT_EMBED_TTL,
    embedParams: DEFAULT_EMBED_PARAMS,
    groups: ['operator', 'admin'],
  },
  {
    path: '/dashboard-3',
    title: 'Время',
    embedId: DATALENS_IDS.time,
    embedTtlSeconds: DEFAULT_EMBED_TTL,
    embedParams: DEFAULT_EMBED_PARAMS,
    groups: ['operator', 'admin'],
  },
]

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {dashboardPages.map(({ path, title, embedUrl, embedId, embedTtlSeconds, embedParams, groups }) => (
          <Route
            key={path}
            path={path}
            element={
              <ProtectedRoute groups={groups}>
                <DashboardPage title={title} embedUrl={embedUrl} embedId={embedId} embedTtlSeconds={embedTtlSeconds} embedParams={embedParams} />
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
