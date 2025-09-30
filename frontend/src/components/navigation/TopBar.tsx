import { useEffect, useState } from 'react'
import { PiSignOutBold } from 'react-icons/pi'
import { useNavigate } from 'react-router-dom'

const USERS_API_BASE = (import.meta.env.VITE_API_USERS_URL ?? '/api/v1/users').replace(/\/$/, '')
const PROFILE_ENDPOINT =
  import.meta.env.VITE_PROFILE_ENDPOINT ?? `${USERS_API_BASE}/me`

interface ProfileState {
  fullName: string
  group: string
  initials: string
}

interface ProfileResponse {
  uid?: string | null
  username?: string | null
  email?: string | null
  first_name?: string | null
  last_name?: string | null
  groups?: string[] | null
}

const FALLBACK_PROFILE: ProfileState = {
  fullName: 'Пользователь',
  group: '—',
  initials: 'П',
}

export function TopBar() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<ProfileState>(FALLBACK_PROFILE)

  useEffect(() => {
    const controller = new AbortController()

    const fetchProfile = async () => {
      try {
        const response = await fetch(PROFILE_ENDPOINT, {
          signal: controller.signal,
          credentials: 'include',
        })

        if (!response.ok) {
          return
        }

        const payload: ProfileResponse = await response.json()
        setProfile((prev) => {
          const fullName = deriveFullName(payload) ?? prev.fullName
          const group = deriveGroup(payload) ?? prev.group
          const initials = deriveInitials(fullName)
          return { fullName, group, initials }
        })
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }
      }
    }

    fetchProfile()

    return () => {
      controller.abort()
    }
  }, [])

  return (
    <header className="top-bar">
      <div className="top-bar__actions">
        <button className="top-bar__icon-button" aria-label="Выйти" onClick={() => navigate('/auth/login')}>
          <PiSignOutBold size={20} />
        </button>
        <div className="user-chip">
          <div className="user-chip__avatar">{profile.initials}</div>
          <div>
            <div className="user-chip__name">{profile.fullName}</div>
            <div className="user-chip__meta">{profile.group}</div>
          </div>
        </div>
      </div>
    </header>
  )
}

function deriveFullName(payload: ProfileResponse): string | undefined {
  const names = [payload.last_name, payload.first_name].filter(Boolean)

  if (names.length) {
    return names.join(' ')
  }

  return payload.username ?? payload.email ?? undefined
}

function deriveGroup(payload: ProfileResponse): string | undefined {
  const groups = payload.groups?.filter(Boolean)
  if (!groups || groups.length === 0) {
    return undefined
  }

  const raw = groups[0] ?? ''
  const normalized = raw
    .split('/')
    .filter(Boolean)
    .pop() ?? raw

  if (!normalized) {
    return undefined
  }

  return normalized
    .replace(/[-_]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
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
