<!-- TODO Update for DZ_3 -->

# QA-Website
> Семестровый проект ТехноПарк (осень 2025)

# Установка
Перед установкой необходимо иметь **[Python](https://www.python.org/downloads/) (v3.10+)**, **[Node.js](https://nodejs.org/en) (v20+)** и **[npm](https://www.npmjs.com/)**.

Откройте проект и выполните команды.
1. Создайте проект
```
git clone https://github.com/BurmatovStepan/QA-Website.git
cd qa-website
```

2. Установите зависимости
```
npm install
pip install -r requirements.txt
```

3. Создатей файл `.env` в корневой директории. Данные переменные используются в `settings.py` django-приложения
```
SECRET_KEY=<YOUR_SECRET_KEY>
DEBUG=True
ALLOWED_HOSTS=127.0.0.1|localhost
```

# Сборка статических файлов
В `package.json`  предусмотрено 2 скрипта для сборки:
- `npm run build:dev` - копирует `assets/` и собирает `scss/style.scss` и `ts/main.ts` в `static/` без оптимизаций.
- `npm run build` - собирает проект в `static/` со сжатием `style.css`.

# Запуск/Отладка
`npm start` - выполняет команду `build:dev`, запускает сервер Django на http://127.0.0.1:8000/ и создает файловые наблюдатели для `assets/`, `scss/` и `ts/`, обеспечивая **HMR** при изменении файлов.

> [!WARNING]
> Команды `npm start`, `npm run build:dev` и `npm run build` удаляют директорию `static/` перед выполнением.

> [!TIP]
> Для тестирования mock-данных доступны следующие теги (?tag=value в строке поиска)
> 1. `user=<user_id>` - авторизация под пользователем с `id=user_id`
> 2. `page-size=<int>` - задание размера пагинации
