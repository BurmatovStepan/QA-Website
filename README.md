# QA-Website
> Семестровый проект ТехноПарк (осень 2025)

# Установка
Перед установкой необходимо иметь **[Node.js](https://nodejs.org/en) (v20+)** и **[npm](https://www.npmjs.com/)**.

Откройте проект и выполните команды.
```
git clone https://github.com/BurmatovStepan/QA-Website.git
cd qa-website
npm install
```

# Сборка
В `package.json`  предусмотрено 2 скрипта для сборки:
- `npm run build:dev` - собирает проект в `dist/QA-Website` без оптимизаций
- `npm run build` - собирает проект в `/dist`

# Отладка
`npm start` - открывает сервер с HMR на http://localhost:1234.

# Развертывание
Проект использует **GitHub Actions** для автоматического развертывания приложения на **GitHub Pages**.
### Процесс
1. Отправьте код (Push/Merge) в ветку `main`
2. Автоматически запускается `deploy.yaml`
3. Выполняется команда `npm run build`
4. Содержимое папки `./dist` загружается и публикуется на ваших GitHub Pages

Примечание: запустить развертывание можно вручную через вкладку "Actions" в GitHub.
