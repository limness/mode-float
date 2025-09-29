import { NavLink } from 'react-router-dom'
import { PiNotebookBold, PiSquaresFourBold, PiUploadSimpleBold } from 'react-icons/pi'
import { classNames } from '../../utils/classNames'

const navItems = [
  { label: 'Дашборд', to: '/', icon: PiSquaresFourBold },
  { label: 'Дашборд', to: '/dashboard-2', icon: PiSquaresFourBold },
  { label: 'Дашборд', to: '/dashboard-3', icon: PiSquaresFourBold },
  { label: 'Дашборд', to: '/dashboard-4', icon: PiSquaresFourBold },
  { label: 'Отчёт', to: '/upload', icon: PiUploadSimpleBold },
  { label: 'Журнал', to: '/journal', icon: PiNotebookBold },
]

export function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="sidebar__menu">
        {navItems.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={`${label}-${to}`}
            to={to}
            className={({ isActive }) =>
              classNames('sidebar__item', isActive && 'sidebar__item--active')
            }
          >
            <Icon />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
