import { redirectToKeycloakLogin } from '../config/auth'

export function LoginPage() {
  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">
          Войти в <span className="auth-title__accent">Fly Potato</span>
        </h1>
        <p className="auth-card__subtitle">Авторизация проходит через корпоративный Keycloak.</p>

        <div className="auth-form auth-form--actions">
          <button className="auth-submit" type="button" onClick={redirectToKeycloakLogin}>
            Продолжить
          </button>
        </div>
        <p className="auth-card__footer">Используйте корпоративный аккаунт или провайдеры, подключённые в Keycloak (например, Google).</p>
      </div>
    </div>
  )
}
