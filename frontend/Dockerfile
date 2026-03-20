FROM node:20-alpine

WORKDIR /app

# Копирование package файлов
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование исходного кода
COPY . .

# Порт Vite dev server
EXPOSE 5173

# Команда запуска (development режим с hot reload)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
