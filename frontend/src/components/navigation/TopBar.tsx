import { PiSignOutBold } from 'react-icons/pi'
import { useNavigate } from 'react-router-dom'

export function TopBar() {
  const navigate = useNavigate()

  return (
    <header className="top-bar">
      <div className="top-bar__actions">
        <button className="top-bar__icon-button" aria-label="Выйти" onClick={() => navigate('/auth/login')}>
          <PiSignOutBold size={20} />
        </button>
        <div className="user-chip">
          <div className="user-chip__avatar">П</div>
          <div>
            <div className="user-chip__name">Плойкин Е.В.</div>
            <div className="user-chip__meta">Администратор</div>
          </div>
        </div>
      </div>
    </header>
  )
}
