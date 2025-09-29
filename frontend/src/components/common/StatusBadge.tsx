interface StatusBadgeProps {
  status: 'running' | 'completed' | 'failed' | 'pending'
}

const statusLabels: Record<StatusBadgeProps['status'], string> = {
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
  pending: 'Pending',
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return <span className={`status-badge status-badge--${status}`}>{statusLabels[status]}</span>
}
