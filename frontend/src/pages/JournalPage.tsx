import { Button } from '../components/common/Button'
import { useJournalExport } from '../hooks/useJournalExport'

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
  const formatDisplayDate = (date: Date | null) => (date ? date.toLocaleDateString('ru-RU') : '—')

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
        {exportError && (
          <p className="export-error">{exportError}</p>
        )}
      </section>
    </div>
  )
}
