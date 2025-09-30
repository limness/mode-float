<h1 align="center">Flight Potato</h1>
<div align="center">
	<img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/limness/mode-float">
	<img alt="GitHub code size" src="https://img.shields.io/github/languages/code-size/limness/mode-float">
	<img alt="GitHub commits stats" src="https://img.shields.io/github/commit-activity/y/limness/mode-float">
</div>
<p align="center">
<strong>Flight Potato</strong> – сервис для анализа количества и длительности полётов гражданских беспилотников в 
регионах Российской Федерации для определения полётной активности на основе данных Росавиации.
</p>

--- 

# Установка и развертывание
## 1. Клонирование репозитория

```bash
git clone https://github.com/limness/mode-float
cd mode-float
```
## 2. Настройка окружения
### Создание `.env` файла
Создайте или скопируйте файлы окружения

```bash
cp .env.example .env.prod
```

> [!NOTE]
> Makefile ищет файл `.env.<ENV>` через переменную `ENV_FILE ?= .env.$(ENV)`.

### Переменные окружения
| Переменная               | Значение по умолчанию | Описание                                |
|--------------------------|-----------------------|-----------------------------------------|
| `APP_TITLE`              | `Float App`           | Название приложения                     |
| `APP_VERSION`            | `0.1.0`               | Версия приложения                       |
| `APP_DEBUG`              | `False`               | Режим отладки (`True`/`False`)          |
| `APP_PROMETHEUS_HOST`    | `0.0.0.0`             | Хост, на котором запускается приложение |
| `APP_PROMETHEUS_PORT`    | `8000`                | Порт приложения                         |
| `POSTGRES_URI`           | –                     | URI подключения к базе данных           |
| `GRAFANA_CLOUD_USERNAME` | –                     | Имя пользователя Grafana Cloud          |
| `GRAFANA_CLOUD_TOKEN`    | –                     | Токен Grafana Cloud для метрик          |
| `DATA_SOURCE_NAME`       | –                     | Имя/ссылка источника метрик             |

## 3. Зависимости
| Библиотека            | Минимальная версия | Назначение                                                         |
|-----------------------|--------------------|--------------------------------------------------------------------|
| **python**            | ^3.12              | -                                                                  |
| **sqlalchemy**        | ^2.0.39            | ORM и конструктор SQL-запросов                                     |
| **alembic**           | ^1.15.1            | Инструмент миграций для SQLAlchemy                                 |
| **asyncpg**           | ^0.30.0            | Асинхронный драйвер PostgreSQL                                     |
| **pydantic-settings** | ^2.8.1             | Управление настройками через Pydantic                              |
| **greenlet**          | ^3.1.1             | Лёгкие сопрограммы (используются SQLAlchemy для «зелёных потоков») |
| **pydantic**          | ^2.11.7            | Валидация данных и создание моделей                                |
| **geopy**             | ^2.4.1             | Геокодирование и географические вычисления                         |
| **numpy**             | ^2.3.1             | Научные вычисления и работа с массивами                            |
| **colorlog**          | ^6.9.0             | Раскрашенный логгинг                                               |
| **httpx**             | ^0.28.1            | Асинхронный HTTP-клиент                                            |
| **prometheus-client** | ^0.22.1            | Метрики и мониторинг Prometheus                                    |
| **aiohttp**           | ^3.12.14           | Асинхронный HTTP-клиент/сервер                                     |
| **fastapi**           | ^0.117.1           | Веб-фреймворк для создания REST/GraphQL API                        |
| **uvicorn**           | ^0.37.0            | ASGI-сервер для запуска FastAPI и других ASGI-приложений           |
| **pandas**            | ^2.3.2             | Анализ и обработка табличных данных                                |
| **openpyxl**          | ^3.1.5             | Работа с Excel-файлами (XLSX)                                      |
| **geoalchemy2**       | ^0.18.0            | Геопространственные расширения для SQLAlchemy/PostGIS              |
| **pyjwt**             | ^2.10.1            | Работа с JSON Web Token (JWT)                                      |
| **python-multipart**  | ^0.0.20            | Парсинг multipart/form-data (загрузка файлов и форм в FastAPI)     |
## 4. Настройка Nginx

> [!IMPORTANT]
> Замените значения в конфиге:

* `server_name` → на ваш домен (например, d1ffic00lt.com www.d1ffic00l.com)

* `ssl_certificate` и `ssl_certificate_key` → на реальные пути к вашим сертификатам

> [!NOTE]
> например, для Let’s Encrypt:
`/etc/letsencrypt/live/<ВАШ_ДОМЕН>/fullchain.pem` и
`/etc/letsencrypt/live/<ВАШ_ДОМЕН>/privkey.pem`

## 5. Настройка KeyCloak

1. Войти в Keycloak → создать **Realm**.
2. Clients → Create client:
   * **Client type**: `OpenID Connect`
   * **Client ID**: `oauth2-proxy` (или своё)
   * **Name**: по желанию
3. Next:
   * **Root URL**: `<ВАШ_ДОМЕН>`
   * **Valid redirect URIs**: `<ВАШ_ДОМЕН>/oauth2/callback`
   * **Web origins**: `<ВАШ_ДОМЕН>`
   * **Home URL** (опц.): `<ВАШ_ДОМЕН>`
4. Next:
   * **Client authentication**: `ON` (тип клиента: `confidential`)
   * **Standard Flow**: `ON`
   * Сохранить.
5. На вкладке **Credentials** скопировать **Client secret** — он нужен `oauth2-proxy`.

**Protocol Mappers** (клиент → Mappers):

Добавьте мапперы, чтобы нужные поля попадали в токены:

  * `email`:

    * **Mapper type**: `User Property`
    * **Property**: `email`
    * **Token Claim Name**: `email`
    * **Add to ID token**: `ON`, **Add to access token**: `ON`
  * `preferred_username`:

    * **Mapper type**: `User Property`
    * **Property**: `username`
    * **Token Claim Name**: `preferred_username`
    * **Add to ID token**: `ON`, **Add to access token**: `ON`
  * (опц.) `groups`:

    * **Mapper type**: `Group Membership`
    * **Token Claim Name**: `groups`
    * (по желанию) Full group path

## 4. Запуск 

```bash
make all-prod
```

## 5. Настройка дашборда

> [!IMPORTANT]
> Для корректной работы Дашборда вам требуется учетная запись [yandex.cloud](https://yandex.cloud) (в том числе и
 [datalens.ru](https://datalens.ru))   


### 0. Создание Каталога 

Перед начало работы вы должны дождаться создания Облака на [yandex.cloud](https://yandex.cloud). Это может занять 
некоторое время. Проверить статус 
создания каталога Вы можете посмотреть на [этой](https://console.yandex.cloud/cloud) странице. 

### 1. Создание Воркбука
* Скачайте [файл](https://github.com/limness/flight-potato-dashboard.json) дашборда
* Зайдите на [страницу](https://datalens.ru/collections) с Воркбуками
* В правом верхнем углу нажмите кнопку `Создать`
* Импортируйте ранее скаченный файл
* Заполните полня названия и описания

### 2. Настройка подключения к базе данных
* Зайдите в ранее созданный Воркбук
* Перейдите во вкладку `Подключения`
* Нажмите на подключение `flight-database-connection`
* Заполните данные 
  * Выберите Ваш текущий каталог (если каталог отсутствует – создайте его)
  * Укажите `Хост` (ip вашего сервера)
  * Укажите `Порт` базы данных
  * Укажите имя пользователя для доступа к базе данных
  * Укажите пароль для дуступа к базе данных

### 3. Настройка интеграции на сайт

> [!WARNING]
> Для интеграции дашбордов DataLens в работу сайта требуется подписка DataLens for business 

TODO: инфа про rsa jwt и id
![https://s11.pikabu.ru/images/big_size_comm/2020-06_4/1592486654118117958.jpg](https://s11.pikabu.ru/images/big_size_comm/2020-06_4/1592486654118117958.jpg)
