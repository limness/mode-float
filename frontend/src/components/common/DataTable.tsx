import type { ReactNode } from 'react'

export interface Column<T> {
  id: string
  header: string
  align?: 'left' | 'center' | 'right'
  render?: (row: T) => ReactNode
}

interface DataTableProps<T> {
  columns: Array<Column<T>>
  rows: T[]
  rowKey: (row: T) => string
  emptyMessage?: string
}

export function DataTable<T>({ columns, rows, rowKey, emptyMessage = 'No data available' }: DataTableProps<T>) {
  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.id} className={`align-${column.align ?? 'left'}`}>
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td className="data-table__empty" colSpan={columns.length}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={rowKey(row)}>
                {columns.map((column) => (
                  <td key={column.id} className={`align-${column.align ?? 'left'}`}>
                    {column.render ? column.render(row) : (row as unknown as Record<string, ReactNode>)[column.id]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
