# QA-Website
> Семестровый проект ТехноПарк (осень 2025)

# Установка
Перед установкой необходимо иметь **[Python](https://www.python.org/downloads/) (v3.10+)**, **[Node.js](https://nodejs.org/en) (v20+)** и **[npm](https://www.npmjs.com/)**.

Откройте проект и выполните команды.
1. Создайте проект
```bash
git clone https://github.com/BurmatovStepan/QA-Website.git
cd qa-website
```

2. Установите зависимости
```bash
npm install
pip install -r requirements.txt
```

3. Создатей файл `.env` в корневой директории. Данные переменные используются в `settings.py` django-приложения
```ini
SECRET_KEY=<YOUR_SECRET_KEY>

DEBUG=True
ALLOWED_HOSTS=127.0.0.1|localhost

ENGINE=<BACKEND_OF_YOUR_DATABASE>     (default="django.db.backends.postgresql")
NAME=<NAME_OF_YOUR_DATABASE>          (default="qa_database")
USER=<NAME_OF_USER>                   (default="qa_user")
PASSWORD=<PASSWORD_OF_THE_USER>       (default="")
HOST=<HOST_TO_ACCESS_DATABASE>        (default="localhost")
PORT=<PORT_TO_ACCESS_DATABASE>        (default="5432")
```

# Сборка статических файлов
В `package.json`  предусмотрено 2 скрипта для сборки:
- `npm run build:dev` - копирует `assets/` и собирает `scss/style.scss` и `ts/main.ts` в `static/` без оптимизаций.
- `npm run build` - собирает проект в `static/` со сжатием `style.css`.

# Запуск/Отладка
`npm start` - выполняет команду `build:dev`, запускает сервер Django на http://127.0.0.1:8000/ и создает файловые наблюдатели для `assets/`, `scss/` и `ts/`, обеспечивая **HMR** при изменении файлов.

> [!WARNING]
> Команды `npm start`, `npm run build:dev` и `npm run build` удаляют директорию `static/` перед выполнением.
