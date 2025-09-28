import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { classNames } from '../../utils/classNames'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost'
  icon?: ReactNode
}

export function Button({ variant = 'primary', icon, className, children, ...rest }: ButtonProps) {
  return (
    <button className={classNames('button', `button--${variant}`, className)} {...rest}>
      {icon}
      <span>{children}</span>
    </button>
  )
}
