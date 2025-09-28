import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/common/Button'

export function LoginPage() {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">
          Вход в систему <span className="auth-title__accent">FlyEye</span>
        </h1>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="login">
              Логин<span className="required">*</span>
            </label>
            <input id="login" name="login" type="text" placeholder="Введите логин" required />
          </div>
          <div className="form-field">
            <label htmlFor="password">
              Пароль<span className="required">*</span>
            </label>
            <input id="password" name="password" type="password" placeholder="Введите пароль" required />
          </div>
          <div className="auth-actions">
            <Button type="submit">Войти</Button>
          </div>
        </form>
        <div className="auth-extra">
          Нет аккаунта? <Link to="/auth/register">Зарегистрироваться</Link>
        </div>
      </div>
    </div>
  )
}
