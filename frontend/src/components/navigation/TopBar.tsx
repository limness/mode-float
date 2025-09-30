import { PiSignOutBold } from 'react-icons/pi'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export function TopBar() {
  const navigate = useNavigate()
  const { profile } = useAuth()

  const initials = profile?.initials ?? '—'
  const fullName = profile?.fullName ?? 'Пользователь'
  const group = profile?.displayGroup ?? '—'

  return (
    <header className="top-bar">
      <div className="top-bar__actions">
        <button className="top-bar__icon-button" aria-label="Выйти" onClick={() => navigate('/auth/login')}>
          <PiSignOutBold size={20} />
        </button>
        <div className="user-chip">
          <div className="user-chip__avatar">{initials}</div>
          <div>
            <div className="user-chip__name">{fullName}</div>
            <div className="user-chip__meta">{group}</div>
          </div>
        </div>
      </div>
    </header>
  )
}
