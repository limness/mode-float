import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

interface ProtectedRouteProps {
  children: ReactNode
  groups?: Array<'admin' | 'operator' | string>
}

export function ProtectedRoute({ children, groups }: ProtectedRouteProps) {
  const location = useLocation()
  const { profile, isLoading, hasGroup } = useAuth()

  if (isLoading) {
    return null
  }

  if (profile === null) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />
  }

  if (groups && !hasGroup(groups)) {
    return <Navigate to="/no-access" state={{ from: location }} replace />
  }

  return <>{children}</>
}
