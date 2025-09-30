import { NavLink } from 'react-router-dom'
import { PiNotebookBold, PiSquaresFourBold, PiUploadSimpleBold } from 'react-icons/pi'
import { classNames } from '../../utils/classNames'
import { useAuth } from '../../context/AuthContext'

const navItems = [
  { label: 'Обзор', to: '/', icon: PiSquaresFourBold, groups: ['operator', 'admin'] },
  { label: 'Регионы', to: '/dashboard-2', icon: PiSquaresFourBold, groups: ['operator', 'admin'] },
  { label: 'Время', to: '/dashboard-3', icon: PiSquaresFourBold, groups: ['operator', 'admin'] },
  { label: 'Отчёт', to: '/upload', icon: PiUploadSimpleBold, groups: ['admin'] },
  { label: 'Журнал', to: '/journal', icon: PiNotebookBold, groups: ['admin'] },
]

export function Sidebar() {
  const { hasGroup, isLoading } = useAuth()

  if (isLoading) {
    return null
  }

  const allowedItems = navItems.filter((item) => hasGroup(item.groups))

  return (
    <aside className="sidebar">
      <nav className="sidebar__menu">
        {allowedItems.map(({ label, to, icon: Icon }) => (
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
