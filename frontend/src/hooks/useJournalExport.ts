import { useCallback, useEffect, useMemo, useState } from 'react'

interface LimitsResponse {
  min_date: string
  max_date: string
}

const API_BASE_URL = (import.meta.env.VITE_API_UAV_URL ?? '/api/v1/uav').replace(/\/$/, '')

export function useJournalExport(apiBase: string = API_BASE_URL) {
  const [minDate, setMinDate] = useState<Date | null>(null)
  const [maxDate, setMaxDate] = useState<Date | null>(null)
  const [fromDate, setFromDate] = useState<string>('')
  const [toDate, setToDate] = useState<string>('')
  const [isLoadingLimits, setIsLoadingLimits] = useState(true)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const formatDateInput = (date: Date) => date.toISOString().slice(0, 10)

  useEffect(() => {
    let cancelled = false

    const loadLimits = async () => {
      setIsLoadingLimits(true)
      try {
        const response = await fetch(`${apiBase}/date-bounds`, {
          credentials: 'include',
        })
        if (!response.ok) {
          throw new Error('Не удалось получить доступный период')
        }
        const data = (await response.json()) as LimitsResponse
        if (cancelled) return

        const min = new Date(data.min_date)
        const max = new Date(data.max_date)

        setMinDate(min)
        setMaxDate(max)

        const defaultTo = max
        const defaultFrom = new Date(Math.max(min.getTime(), defaultTo.getTime() - 7 * 24 * 60 * 60 * 1000))

        setFromDate(formatDateInput(defaultFrom))
        setToDate(formatDateInput(defaultTo))
      } catch (err) {
        if (err instanceof Error) {
          setError(err.message)
        } else {
          setError('Неизвестная ошибка загрузки периода')
        }
      } finally {
        if (!cancelled) {
          setIsLoadingLimits(false)
        }
      }
    }

    void loadLimits()

    return () => {
      cancelled = true
    }
  }, [apiBase])

  const isRangeValid = useMemo(() => {
    if (!fromDate || !toDate) return false
    const from = new Date(fromDate)
    const to = new Date(toDate)
    if (Number.isNaN(from.getTime()) || Number.isNaN(to.getTime())) return false
    if (from > to) return false
    if (minDate && from < minDate) return false
    if (maxDate && to > maxDate) return false
    return true
  }, [fromDate, toDate, minDate, maxDate])

  const exportJournal = useCallback(async () => {
    if (!isRangeValid) {
      setError('Период задан некорректно')
      return
    }

    try {
      setIsExporting(true)
      setError(null)

      const payload = {
        min_date: new Date(fromDate).toISOString(),
        max_date: new Date(toDate).toISOString(),
      }

      const response = await fetch(`${apiBase}/date-bounds/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status >= 500) {
          throw new Error('Сервер временно недоступен, попробуйте позже')
        }
        if (response.status === 404) {
          throw new Error('За выбранный период данные отсутствуют')
        }
        const message = await response.text()
        throw new Error(message || 'Не удалось экспортировать журнал')
      }

      if (response.redirected) {
        throw new Error('Сессия истекла. Войдите снова, чтобы экспортировать журнал.')
      }

      const contentType = response.headers.get('content-type') ?? ''
      let jsonPayload: unknown
      if (contentType.includes('application/json')) {
        jsonPayload = await response.json()
      } else {
        const text = await response.text()
        if (text.trim().startsWith('<')) {
          throw new Error('Сессия истекла. Войдите снова, чтобы экспортировать журнал.')
        }
        try {
          jsonPayload = JSON.parse(text)
        } catch (error) {
          throw new Error(text || 'Получен некорректный ответ сервера')
        }
      }

      const blob = new Blob([JSON.stringify(jsonPayload, null, 2)], {
        type: 'application/json',
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      const suffix = `${fromDate.replace(/-/g, '')}-${toDate.replace(/-/g, '')}`
      link.href = url
      link.download = `journal-${suffix}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Неизвестная ошибка при экспортировании')
      }
    } finally {
      setIsExporting(false)
    }
  }, [apiBase, fromDate, toDate, isRangeValid])

  return {
    minDate,
    maxDate,
    fromDate,
    toDate,
    setFromDate,
    setToDate,
    isLoadingLimits,
    isExporting,
    isRangeValid,
    error,
    exportJournal,
  }
}
