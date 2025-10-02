import { NavLink } from 'react-router-dom'
import { PiNotebookBold, PiSquaresFourBold, PiUploadSimpleBold } from 'react-icons/pi'
import { classNames } from '../../utils/classNames'
import { useAuth } from '../../context/AuthContext'

const MarkerIcon = () => (
  <img src="/regions-marker.svg" alt="" className="sidebar__icon" aria-hidden="true" />
)

const ArrowDownIcon = () => (
  <img src="/arrow-down.svg" alt="" className="sidebar__icon" aria-hidden="true" />
)

const navItems = [
  { label: 'Обзор', to: '/', icon: PiSquaresFourBold, groups: ['operator', 'admin'] },
  { label: 'Регионы', to: '/dashboard-2', icon: MarkerIcon, groups: ['operator', 'admin'] },
  { label: 'Время', to: '/dashboard-3', icon: ArrowDownIcon, groups: ['operator', 'admin'] },
  { label: 'Отчёт', to: '/upload', icon: PiUploadSimpleBold, groups: ['admin'] },
  { label: 'Журнал', to: '/journal', icon: PiNotebookBold, groups: ['admin'] },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { hasGroup, isLoading } = useAuth()

  if (isLoading) {
    return null
  }

  const allowedItems = navItems.filter((item) => hasGroup(item.groups))

  return (
    <aside className={classNames('sidebar', isOpen && 'sidebar--open')}>
      <nav className="sidebar__menu">
        {allowedItems.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={`${label}-${to}`}
            to={to}
            className={({ isActive }) =>
              classNames('sidebar__item', isActive && 'sidebar__item--active')
            }
            onClick={onClose}
          >
            <Icon />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
