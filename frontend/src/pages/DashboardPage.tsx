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

  const finalUrl = embedUrl ?? signedUrl
  const hasEmbed = Boolean(finalUrl)

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
        {hasEmbed ? (
          <div className="panel__embed">
            {isEmbedLoading ? (
              <div className="export-hint">Готовим дашборд…</div>
            ) : embedError ? (
              <div className="export-error">{embedError}</div>
            ) : (
              <iframe
                src={finalUrl ?? undefined}
                title={embedTitle ?? title}
                allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            )}
          </div>
        ) : (
          <div className="panel__placeholder" role="presentation" />
        )}
      </section>
    </div>
  )
}
