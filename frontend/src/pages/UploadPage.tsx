import { useState } from 'react'
import { PiDownloadSimpleBold } from 'react-icons/pi'
import { Button } from '../components/common/Button'
import { classNames } from '../utils/classNames'

export function UploadPage() {
  const [isDragActive, setIsDragActive] = useState(false)

  return (
    <div className="page-shell">
      <div className="breadcrumb">
        <span>Главная</span>
        <span> / </span>
        <span>Отчёт</span>
      </div>

      <section className="panel">
        <header className="panel__header">
          <h1 className="panel__title">Загрузить новый отчёт</h1>
        </header>

        <div
          className={classNames('upload-zone', isDragActive && 'upload-zone--active')}
          onDragOver={(event) => {
            event.preventDefault()
            setIsDragActive(true)
          }}
          onDragLeave={() => setIsDragActive(false)}
          onDrop={(event) => {
            event.preventDefault()
            setIsDragActive(false)
          }}
        >
          <div className="upload-zone__icon">
            <PiDownloadSimpleBold size={42} />
          </div>
          <div className="upload-zone__title">Перетащите файлы для загрузки</div>
          <div className="upload-zone__subtitle">Загрузите отчёт в формате exel</div>
        </div>

        <div className="panel__footer">
          <Button variant="ghost">Отменить</Button>
          <Button>Подтвердить</Button>
        </div>
      </section>
    </div>
  )
}
