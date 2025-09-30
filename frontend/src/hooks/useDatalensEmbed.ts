import { useEffect, useMemo, useState } from 'react'

interface UseDatalensEmbedOptions {
  ttlSeconds?: number
  params?: Record<string, string | string[]>
}

const API_DASHBOARD_BASE = ('/api/v1/dashboard').replace(/\/$/, '')
const EMBED_ENDPOINT = `${API_DASHBOARD_BASE}/embed/datalens`

interface EmbedState {
  url: string | null
  isLoading: boolean
  error: string | null
}

export function useDatalensEmbed(embedId?: string, options?: UseDatalensEmbedOptions): EmbedState {
  const [state, setState] = useState<EmbedState>({ url: null, isLoading: Boolean(embedId), error: null })
  const serializedParams = useMemo(() => JSON.stringify(options?.params ?? {}), [options?.params])

  useEffect(() => {
    if (!embedId) {
      setState({ url: null, isLoading: false, error: null })
      return
    }

    const controller = new AbortController()

    const fetchEmbed = async () => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }))
      try {
        const response = await fetch(EMBED_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            embed_id: embedId,
            ttl_seconds: options?.ttlSeconds,
            params: options?.params,
          }),
          signal: controller.signal,
        })

        if (!response.ok) {
          const message = await response.text()
          throw new Error(message || 'Не удалось получить ссылку для встраивания')
        }

        const payload = (await response.json()) as { url: string }
        setState({ url: payload.url, isLoading: false, error: null })
      } catch (error) {
        if (controller.signal.aborted) {
          return
        }
        setState({
          url: null,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Неизвестная ошибка при получении ссылки',
        })
      }
    }

    void fetchEmbed()

    return () => {
      controller.abort()
    }
  }, [embedId, serializedParams, options?.ttlSeconds])

  return state
}
