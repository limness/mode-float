import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PiDownloadSimpleBold, PiFileArrowUpBold } from 'react-icons/pi'
import { Button } from '../components/common/Button'
import { classNames } from '../utils/classNames'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')
const UPLOAD_ENDPOINT =
  import.meta.env.VITE_UPLOAD_ENDPOINT ?? `${API_BASE_URL}/upload/xlsx`

export function UploadPage() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [isDragActive, setIsDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList?.length) {
      return
    }
    const file = fileList[0]
    setSelectedFile(file)
    setError(null)
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragActive(false)
    handleFiles(event.dataTransfer.files)
  }

  const handleBrowseClick = () => {
    inputRef.current?.click()
  }

  const handleUpload = async () => {
    if (!selectedFile || isUploading) {
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    setIsUploading(true)
    setError(null)

    try {
      const response = await fetch(UPLOAD_ENDPOINT, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const message = await response.text()
        throw new Error(message || 'Ошибка загрузки файла')
      }

      navigate('/')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Не удалось загрузить файл'
      setError(message)
    } finally {
      setIsUploading(false)
    }
  }

  const resetSelection = () => {
    setSelectedFile(null)
    setError(null)
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

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

        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.xls,.csv,.json,.txt"
          hidden
          onChange={(event) => handleFiles(event.target.files)}
        />

        <div
          className={classNames('upload-zone', isDragActive && 'upload-zone--active')}
          onDragOver={(event) => {
            event.preventDefault()
            setIsDragActive(true)
          }}
          onDragLeave={() => setIsDragActive(false)}
          onDrop={handleDrop}
          onClick={handleBrowseClick}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault()
              handleBrowseClick()
            }
          }}
        >
          <div className="upload-zone__icon">
            {selectedFile ? <PiFileArrowUpBold size={42} /> : <PiDownloadSimpleBold size={42} />}
          </div>
          <div className="upload-zone__title">
            {selectedFile ? 'Файл готов к загрузке' : 'Перетащите файлы для загрузки'}
          </div>
          <div className="upload-zone__subtitle">
            {selectedFile ? selectedFile.name : 'Загрузите отчёт в формате exel'}
          </div>
          <div className="upload-zone__hint">Нажмите, чтобы выбрать файл на компьютере</div>
        </div>

        {error && (
          <div className="upload-zone__error" role="alert">
            {error}
          </div>
        )}

        <div className="panel__footer">
          <Button variant="ghost" onClick={resetSelection} disabled={!selectedFile || isUploading}>
            Отменить
          </Button>
          <Button onClick={handleUpload} disabled={!selectedFile || isUploading}>
            {isUploading ? 'Загружаем…' : 'Подтвердить'}
          </Button>
        </div>
      </section>
    </div>
  )
}
