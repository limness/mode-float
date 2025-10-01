import { useNavigate, useLocation } from 'react-router-dom'
import { Button } from '../components/common/Button'
import { useAuth } from '../context/AuthContext'

export function NoAccessPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { profile } = useAuth()
  const fromState = (location.state as { from?: { pathname: string } } | null)?.from?.pathname

  return (
    <div className="page-shell">
      <div className="breadcrumb">
        <span>Главная</span>
        <span> / </span>
        <span>Нет доступа</span>
      </div>

      <section className="panel">
        <header className="panel__header">
          <h1 className="panel__title">Доступ ограничен</h1>
        </header>
        <div className="access-denied">
          <p>
            {profile?.fullName ?? 'Пользователь'}, у вашей учётной записи нет прав для работы в системе.
            Обратитесь к администратору, чтобы получить необходимую роль.
          </p>
          {fromState && (
            <p className="export-hint">
              Запрошенный ресурс: <code>{fromState}</code>
            </p>
          )}
          <div className="access-denied__actions">
            <Button onClick={() => navigate(-1)}>Назад</Button>
          </div>
        </div>
      </section>
    </div>
  )
}
