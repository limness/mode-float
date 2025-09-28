interface DashboardPageProps {
  title: string
  breadcrumb?: string[]
  embedUrl?: string
  embedTitle?: string
}

export function DashboardPage({
  title,
  breadcrumb = ['Главная', title],
  embedUrl,
  embedTitle,
}: DashboardPageProps) {
  const hasEmbed = Boolean(embedUrl)

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
            <iframe src={embedUrl} title={embedTitle ?? title} allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
          </div>
        ) : (
          <div className="panel__placeholder" role="presentation" />
        )}
      </section>
    </div>
  )
}
