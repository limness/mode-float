import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

const USERS_API_BASE = (import.meta.env.VITE_API_USERS_URL ?? '/api/v1/users').replace(/\/$/, '')
const PROFILE_ENDPOINT =
  import.meta.env.VITE_PROFILE_ENDPOINT ?? `${USERS_API_BASE}/me`

type NormalizedGroup = 'admin' | 'operator' | string

interface RawProfileResponse {
  uid?: string | null
  username?: string | null
  email?: string | null
  first_name?: string | null
  last_name?: string | null
  groups?: string[] | null
}

interface Profile {
  fullName: string
  initials: string
  displayGroup: string
  groups: NormalizedGroup[]
  email?: string | null
}

interface AuthContextValue {
  profile: Profile | null
  isLoading: boolean
  hasGroup: (groups?: NormalizedGroup[]) => boolean
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function normalizeGroup(value: string): { normalized: NormalizedGroup; display: string } {
  const trimmed = value.trim()
  const lastSegment = trimmed.split('/').filter(Boolean).pop() ?? trimmed
  const base = lastSegment.toLowerCase()

  if (base === 'administrators' || base === 'admin') {
    return { normalized: 'admin', display: 'Администратор' }
  }
  if (base === 'operators' || base === 'operator') {
    return { normalized: 'operator', display: 'Оператор' }
  }

  const pretty = lastSegment
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())

  return { normalized: base, display: pretty }
}

function deriveInitials(fullName: string): string {
  const parts = fullName
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0]?.toUpperCase())
    .filter(Boolean)

  if (parts.length === 0) {
    return '—'
  }

  return parts.slice(0, 2).join('')
}

function buildProfile(payload: RawProfileResponse): Profile {
  const firstName = payload.first_name ?? ''
  const lastName = payload.last_name ?? ''
  const fullNameCandidates = [lastName, firstName].filter(Boolean)
  const fullName = fullNameCandidates.length
    ? fullNameCandidates.join(' ')
    : payload.username ?? payload.email ?? 'Пользователь'

  const rawGroups = payload.groups?.filter(Boolean) ?? []
  const normalizedGroups: NormalizedGroup[] = []
  let displayGroup = rawGroups.length === 0 ? 'Нет доступа' : '—'

  for (const raw of rawGroups) {
    const { normalized, display } = normalizeGroup(raw)
    if (!normalizedGroups.includes(normalized)) {
      normalizedGroups.push(normalized)
    }
    if (displayGroup === '—') {
      displayGroup = display
    }
  }

  return {
    fullName,
    initials: deriveInitials(fullName),
    displayGroup,
    groups: normalizedGroups,
    email: payload.email,
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const loadProfile = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(PROFILE_ENDPOINT, { credentials: 'include' })
      if (!response.ok) {
        setProfile(null)
        return
      }

      const data = (await response.json()) as RawProfileResponse
      setProfile(buildProfile(data))
    } catch (error) {
      console.error('[auth] Failed to load profile:', error)
      setProfile(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadProfile()
  }, [])

  const value = useMemo<AuthContextValue>(() => {
    const hasGroup = (groups?: NormalizedGroup[]) => {
      if (!groups || groups.length === 0) return true
      if (!profile) return false
      const normalizedSet = new Set(profile.groups.map((item) => item.toLowerCase()))
      return groups.some((group) => normalizedSet.has(group.toLowerCase()))
    }

    return {
      profile,
      isLoading,
      hasGroup,
      refresh: loadProfile,
    }
  }, [profile, isLoading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
