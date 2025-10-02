import { Button } from '../components/common/Button'
import { useJournalExport } from '../hooks/useJournalExport'
import { useJournalData } from '../hooks/useJournalData'
import { classNames } from '../utils/classNames'

const RECENT_LIMIT = 20

export function JournalPage() {
  const {
    minDate,
    maxDate,
    fromDate,
    toDate,
    setFromDate,
    setToDate,
    isLoadingLimits,
    isExporting,
    isRangeValid,
    error: exportError,
    exportJournal,
  } = useJournalExport()
  const { rows: latestRows, isLoading: isLoadingRows, error: rowsError, notice: rowsNotice } = useJournalData(RECENT_LIMIT)

  const formatDisplayDate = (date: Date | null) => (date ? date.toLocaleDateString('ru-RU') : '—')
  const tableRows = latestRows.slice(0, RECENT_LIMIT)
  const hasRows = tableRows.length > 0

  const renderValidationBadge = (state?: string) => {
    if (!state) {
      return <span className="table__cell-sub">—</span>
    }
    const normalized = state.toLowerCase()
    const variant = normalized === 'valid' ? 'success' : normalized === 'duplicate' ? 'warning' : 'info'
    const label = normalized === 'valid' ? 'Проверено' : normalized === 'duplicate' ? 'Дубликат' : state
    return <span className={classNames('badge', `badge--${variant}`)}>{label}</span>
  }

  return (
    <div className="page-shell">
      <div className="breadcrumb">
        <span>Главная</span>
        <span> / </span>
        <span>Журнал</span>
      </div>

      <section className="panel">
        <header className="panel__header">
          <div>
            <h1 className="panel__title">Журнал</h1>
            <p className="panel__subtitle">Доступный период: {formatDisplayDate(minDate)} — {formatDisplayDate(maxDate)}</p>
          </div>
          <Button onClick={exportJournal} disabled={!isRangeValid || isLoadingLimits || isExporting}>
            {isExporting ? 'Готовим...' : 'Скачать JSON'}
          </Button>
        </header>

        <div className="export-controls">
          <label>
            <span>С</span>
            <input
              type="date"
              value={fromDate}
              min={minDate ? minDate.toISOString().slice(0, 10) : undefined}
              max={toDate || undefined}
              onChange={(event) => setFromDate(event.target.value)}
              disabled={isLoadingLimits}
            />
          </label>
          <label>
            <span>По</span>
            <input
              type="date"
              value={toDate}
              min={fromDate || undefined}
              max={maxDate ? maxDate.toISOString().slice(0, 10) : undefined}
              onChange={(event) => setToDate(event.target.value)}
              disabled={isLoadingLimits}
            />
          </label>
        </div>
        {(exportError || rowsError) && (
          <p className="export-error">{exportError ?? rowsError}</p>
        )}
        {rowsNotice && <p className="export-hint">{rowsNotice}</p>}

        <div className="table-card">
          <div className="table-card__header">
            <h2 className="table-card__title">Последние полёты</h2>
            <span className="table-card__meta">{`Показываем ${tableRows.length} из ${RECENT_LIMIT}`}</span>
          </div>
          <div className="table-card__body">
            {isLoadingRows ? (
              <p className="export-hint">Загружаем последние полёты...</p>
            ) : hasRows ? (
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Дата</th>
                    <th>Тип БПЛА</th>
                    <th>Длительность</th>
                    <th>Координаты взлета</th>
                    <th>Координаты посадки</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {tableRows.map((flight, index) => (
                    <tr key={`${flight.id}-${index}`}>
                      <td>
                        <span className="table__cell-primary">{flight.id}</span>
                      </td>
                      <td>
                        <span className="table__cell-primary">{flight.date}</span>
                        {flight.time && <span className="table__cell-sub">{flight.time}</span>}
                      </td>
                      <td>
                        <span className="table__cell-primary">{flight.type}</span>
                      </td>
                      <td>
                        <span className="table__cell-primary">{flight.duration}</span>
                      </td>
                      <td>
                        <span className="table__cell-coordinate">{flight.takeoff}</span>
                      </td>
                      <td>
                        <span className="table__cell-coordinate">{flight.landing}</span>
                      </td>
                      <td>{renderValidationBadge(flight.validation)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="export-hint">За выбранный период нет полётов.</p>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}
