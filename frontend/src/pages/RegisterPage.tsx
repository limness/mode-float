import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/common/Button'

export function RegisterPage() {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">
          Регистрация в системе <span className="auth-title__accent">FlyEye</span>
        </h1>
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="lastName">
              Фамилия<span className="required">*</span>
            </label>
            <input id="lastName" name="lastName" type="text" placeholder="Введите фамилию" required />
          </div>
          <div className="form-field">
            <label htmlFor="firstName">
              Имя<span className="required">*</span>
            </label>
            <input id="firstName" name="firstName" type="text" placeholder="Введите имя" required />
          </div>
          <div className="form-field">
            <label htmlFor="middleName">Отчество</label>
            <input id="middleName" name="middleName" type="text" placeholder="Введите отчество" />
          </div>
          <div className="form-field">
            <label htmlFor="email">
              Email<span className="required">*</span>
            </label>
            <input id="email" name="email" type="email" placeholder="Введите почтовый адрес" required />
          </div>
          <div className="form-field">
            <label htmlFor="registerPassword">
              Пароль<span className="required">*</span>
            </label>
            <input
              id="registerPassword"
              name="password"
              type="password"
              placeholder="Введите пароль"
              required
            />
          </div>
          <div className="auth-actions">
            <Button type="submit">Зарегистрироваться</Button>
          </div>
        </form>
        <div className="auth-extra">
          Уже есть аккаунт? <Link to="/auth/login">Войти</Link>
        </div>
      </div>
    </div>
  )
}
