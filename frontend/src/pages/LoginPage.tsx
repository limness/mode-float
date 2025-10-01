import { getKeycloakLoginUrl, redirectToKeycloakLogin } from '../config/auth'

export function LoginPage() {
  const isConfigured = Boolean(getKeycloakLoginUrl())

  const handleLogin = () => {
    if (!isConfigured) {
      return
    }
    redirectToKeycloakLogin()
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">
          Войти в <span className="auth-title__accent">Fly Potato</span>
        </h1>
        <p className="auth-card__subtitle">Авторизация проходит через корпоративный Keycloak.</p>

        <div className="auth-form auth-form--actions">
          <button className="auth-submit" type="button" onClick={handleLogin} disabled={!isConfigured}>
            Продолжить
          </button>
        </div>
        {!isConfigured && (
          <p className="auth-card__notice" role="alert">
            URL Keycloak не настроен. Обратитесь к администратору системы.
          </p>
        )}
        <p className="auth-card__footer">Используйте корпоративный аккаунт или провайдеры, подключённые в Keycloak (например, Google).</p>
      </div>
    </div>
  )
}
