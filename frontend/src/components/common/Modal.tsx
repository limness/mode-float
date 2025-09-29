import type { ReactNode } from 'react'
import { Button } from './Button'

interface ModalProps {
  open: boolean
  title: string
  description?: string
  primaryAction?: {
    label: string
    onClick: () => void
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  children?: ReactNode
  onClose?: () => void
}

export function Modal({
  open,
  title,
  description,
  primaryAction,
  secondaryAction,
  children,
  onClose,
}: ModalProps) {
  if (!open) return null

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal">
        <header className="modal__header">
          <div>
            <h2>{title}</h2>
            {description && <p>{description}</p>}
          </div>
          {onClose && (
            <button className="modal__close" onClick={onClose} aria-label="Close">
              ×
            </button>
          )}
        </header>
        {children && <div className="modal__body">{children}</div>}
        {(primaryAction || secondaryAction) && (
          <footer className="modal__footer">
            {secondaryAction && (
              <Button variant="ghost" onClick={secondaryAction.onClick}>
                {secondaryAction.label}
              </Button>
            )}
            {primaryAction && (
              <Button onClick={primaryAction.onClick}>{primaryAction.label}</Button>
            )}
          </footer>
        )}
      </div>
    </div>
  )
}
