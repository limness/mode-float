import { Button } from '../components/common/Button'

interface FlightRow {
  id: string
  date: string
  time: string
  type: 'Гражданский' | 'Военный'
  duration: string
  takeoff: string
  landing: string
}

const flights: FlightRow[] = [
  {
    id: '749792889798',
    date: '03.06.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '749792889799',
    date: '02.06.2024',
    time: '18:53:21',
    type: 'Военный',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '749792889735',
    date: '02.06.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '791891739869',
    date: '31.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '749792889666',
    date: '30.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '0000000000',
    date: '29.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '0000000000',
    date: '29.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '0000000000',
    date: '29.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '0000000000',
    date: '29.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
  {
    id: '0000000000',
    date: '29.05.2024',
    time: '18:53:21',
    type: 'Гражданский',
    duration: '3 ч 20 мин',
    takeoff: '55.73906 с.ш. 37.60421 в.д.',
    landing: '55.73906 с.ш. 37.60421 в.д.',
  },
]

export function JournalPage() {
  return (
    <div className="page-shell">
      <div className="breadcrumb">
        <span>Главная</span>
        <span> / </span>
        <span>Журнал</span>
      </div>

      <section className="panel">
        <header className="panel__header">
          <h1 className="panel__title">Журнал</h1>
          <Button>Скачать журнал</Button>
        </header>

        <div className="table-card">
          <div className="table-card__header">
            <h2 className="table-card__title">Последние полеты</h2>
          </div>
          <div className="table-card__body">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Дата</th>
                  <th>Тип БПЛА</th>
                  <th>Длительность</th>
                  <th>Координаты взлета</th>
                  <th>Координаты посадки</th>
                </tr>
              </thead>
              <tbody>
                {flights.map((flight, index) => (
                  <tr key={`${flight.id}-${index}`}>
                    <td className="table__cell-main">{flight.id}</td>
                    <td>
                      <span className="table__cell-main">{flight.date}</span>
                      <span className="table__cell-sub">{flight.time}</span>
                    </td>
                    <td className="table__cell-main">{flight.type}</td>
                    <td className="table__cell-main">{flight.duration}</td>
                    <td className="table__cell-main">{flight.takeoff}</td>
                    <td className="table__cell-main">{flight.landing}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
  )
}
