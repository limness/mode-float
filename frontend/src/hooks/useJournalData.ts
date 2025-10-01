import { useEffect, useMemo, useState } from 'react'

type RawFlight = Record<string, unknown>

export interface JournalRow {
  id: string
  date: string
  time: string
  type: string
  duration: string
  takeoff: string
  landing: string
  validation?: string
}

interface UseJournalDataResult {
  rows: JournalRow[]
  isLoading: boolean
  error: string | null
  notice: string | null
  refresh: () => Promise<void>
}

const API_BASE_URL = (import.meta.env.VITE_API_UAV_URL ?? '/api/v1/uav').replace(/\/$/, '')
const JOURNAL_ENDPOINT = `${API_BASE_URL}/date-bounds/query`
const LIMITS_ENDPOINT = `${API_BASE_URL}/date-bounds`

function formatDateTime(value: unknown): { date: string; time: string } {
  if (typeof value === 'string' || value instanceof Date) {
    const date = value instanceof Date ? value : new Date(value)
    if (!Number.isNaN(date.getTime())) {
      return {
        date: date.toLocaleDateString('ru-RU'),
        time: date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
      }
    }
  }
  return { date: '—', time: '—' }
}

function formatCoordinates(lat?: unknown, lon?: unknown, fallback?: unknown): string {
  const latNum = typeof lat === 'number' ? lat : Number(lat)
  const lonNum = typeof lon === 'number' ? lon : Number(lon)
  if (!Number.isNaN(latNum) && !Number.isNaN(lonNum)) {
    return `${latNum.toFixed(5)} с.ш., ${lonNum.toFixed(5)} в.д.`
  }
  if (typeof fallback === 'string' && fallback.trim().length > 0) {
    return fallback
  }
  return '—'
}

function buildRows(data: RawFlight[], limit: number): JournalRow[] {
  return data.slice(0, limit).map((item, index) => {
    const id =
      (typeof item.flight_id === 'string' && item.flight_id) ||
      (typeof item.id === 'string' && item.id) ||
      `row-${index}`

    const takeoffDT = formatDateTime(item.takeoff_datetime ?? item.takeoff_time)

    const type = (typeof item.uav_type === 'string' && item.uav_type) || '—'

    let duration: string = '—'
    if (typeof item.duration_minutes === 'number') {
      duration = `${item.duration_minutes} мин`
    } else if (typeof item.duration_sec === 'number') {
      duration = `${Math.round(Number(item.duration_sec) / 60)} мин`
    }

    const takeoff = formatCoordinates(
      item.takeoff_lat,
      item.takeoff_lon,
      item.takeoff_point ?? (item.coordinates as any)?.takeoff
    )
    const landing = formatCoordinates(
      item.landing_lat,
      item.landing_lon,
      item.landing_point ?? (item.coordinates as any)?.landing
    )

    return {
      id,
      date: takeoffDT.date,
      time: takeoffDT.time,
      type,
      duration,
      takeoff,
      landing,
      validation: (typeof item.validation_status === 'string' && item.validation_status) || undefined,
    }
  })
}

export function useJournalData(limit = 30): UseJournalDataResult {
  const [raw, setRaw] = useState<RawFlight[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const fetchData = async () => {
    setIsLoading(true)
    try {
      setNotice(null)
      const limitsResponse = await fetch(LIMITS_ENDPOINT, { credentials: 'include' })
      if (!limitsResponse.ok) {
        throw new Error('Не удалось получить доступный период')
      }
      const limits = (await limitsResponse.json()) as { min_date: string | null; max_date: string | null }
      const max = limits.max_date ? new Date(limits.max_date) : new Date()
      const minBound = limits.min_date ? new Date(limits.min_date) : null
      if (Number.isNaN(max.getTime())) {
        throw new Error('Некорректная максимальная дата')
      }
      const windowMs = 7 * 24 * 60 * 60 * 1000
      const candidateFrom = new Date(max.getTime() - windowMs)
      const from = minBound && candidateFrom < minBound ? minBound : candidateFrom
      const body = {
        min_date: from.toISOString(),
        max_date: max.toISOString(),
        limit,
      }
      const response = await fetch(JOURNAL_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      })
      if (!response.ok) {
        throw new Error('Не удалось загрузить последние полёты')
      }
      if (response.redirected) {
        throw new Error('Сессия истекла. Обновите страницу и войдите снова.')
      }
      const contentType = response.headers.get('content-type') ?? ''
      let payload: RawFlight
      if (contentType.includes('application/json')) {
        payload = (await response.json()) as RawFlight
      } else {
        const text = await response.text()
        if (text.trim().startsWith('<')) {
          throw new Error('Сессия истекла. Обновите страницу и войдите снова.')
        }
        try {
          payload = JSON.parse(text) as RawFlight
        } catch (error) {
          throw new Error('Получен некорректный ответ сервера журнала')
        }
      }
      let items: RawFlight[] = []
      if (Array.isArray(payload)) {
        items = payload
      } else if (Array.isArray((payload as any)?.items)) {
        items = (payload as any).items
      } else {
        throw new Error('Некорректный ответ от сервера журнала')
      }
      setRaw(items)
      setError(null)
      setNotice(items.length ? null : "За выбранный период нет данных")
    } catch (err) {
      console.error('[journal] failed to fetch data', err)
      const message = err instanceof Error ? err.message : 'Не удалось загрузить журнал'
      if (message.includes('Сессия истекла')) {
        setNotice(message)
        setRaw([])
      } else {
        setNotice('Показаны демонстрационные данные: нет подключения к базе данных')
        setRaw([])
      }
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void fetchData()
  }, [limit])

  const rows = useMemo(() => buildRows(raw, limit), [raw, limit])

  return {
    rows,
    isLoading,
    error,
    notice,
    refresh: fetchData,
  }
}
