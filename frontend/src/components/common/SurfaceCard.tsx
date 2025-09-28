import type { ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

interface SurfaceCardProps {
  title?: string
  subtitle?: string
  actions?: ReactNode
  children: ReactNode
  padding?: 'sm' | 'md' | 'lg'
  className?: string
}

export function SurfaceCard({
  title,
  subtitle,
  actions,
  padding = 'md',
  className,
  children,
}: SurfaceCardProps) {
  return (
    <section className={classNames('surface-card', `surface-card--${padding}`, className)}>
      {(title || subtitle || actions) && (
        <header className="surface-card__header">
          <div>
            {title && <h2 className="surface-card__title">{title}</h2>}
            {subtitle && <p className="surface-card__subtitle">{subtitle}</p>}
          </div>
          {actions && <div className="surface-card__actions">{actions}</div>}
        </header>
      )}
      <div className="surface-card__body">{children}</div>
    </section>
  )
}
