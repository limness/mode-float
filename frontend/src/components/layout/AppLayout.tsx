import { Outlet } from 'react-router-dom'
import { Sidebar } from '../navigation/Sidebar'
import { TopBar } from '../navigation/TopBar'

export function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-shell__main">
        <TopBar />
        <div className="app-shell__scroll">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
