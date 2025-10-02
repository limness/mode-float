import { useMemo } from 'react'
import { useDatalensEmbed } from '../hooks/useDatalensEmbed'

interface DashboardPageProps {
  title: string
  breadcrumb?: string[]
  embedUrl?: string
  embedId?: string
  embedTitle?: string
  embedTtlSeconds?: number
  embedParams?: Record<string, string | string[]>
}

export function DashboardPage({
  title,
  breadcrumb = ['Главная', title],
  embedUrl,
  embedId,
  embedTitle,
  embedTtlSeconds,
  embedParams,
}: DashboardPageProps) {
  const { url: signedUrl, isLoading: isEmbedLoading, error: embedError } = useDatalensEmbed(embedId, {
    ttlSeconds: embedTtlSeconds,
    params: embedParams,
  })

  const finalUrl = useMemo(() => {
    const baseUrl = signedUrl ?? embedUrl
    if (!baseUrl) {
      return null
    }

    const url = new URL(baseUrl)
    // Принудительно включаем тёмную тему DataLens
    url.hash = url.hash ? `${url.hash}&theme=dark` : '#theme=dark'
    return url.toString()
  }, [signedUrl, embedUrl])

  const hasResolvedEmbed = Boolean(finalUrl)
  const shouldRenderEmbedContainer = Boolean(embedId || embedUrl || signedUrl)

  return (
    <div className="page-shell">
      <div className="breadcrumb">
        {breadcrumb.map((item, index) => (
          <span key={`${item}-${index}`}>
            {index > 0 && ' / '}
            {item}
          </span>
        ))}
      </div>

      <section className="panel">
        <header className="panel__header">
          <h1 className="panel__title">{title}</h1>
        </header>
        {shouldRenderEmbedContainer ? (
          <div className="panel__embed">
            {isEmbedLoading ? (
              <div className="export-hint">Готовим дашборд…</div>
            ) : embedError ? (
              <div className="export-error">{embedError}</div>
            ) : hasResolvedEmbed ? (
              <iframe
                key={finalUrl}
                src={finalUrl!}
                title={embedTitle ?? title}
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : (
              <div className="export-hint">Ссылка на дашборд пока недоступна</div>
            )}
          </div>
        ) : (
          <div className="panel__placeholder" role="presentation" />
        )}
      </section>
    </div>
  )
}
