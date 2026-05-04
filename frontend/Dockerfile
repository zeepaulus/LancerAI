FROM node:18-alpine

WORKDIR /app

# Copy package.json để cài đặt thư viện
COPY package*.json ./

# Cài đặt thư viện
RUN npm install

# Copy toàn bộ source code
COPY . .

# Mở cổng 3000
EXPOSE 3000

# Lệnh khởi chạy của Vite
CMD ["npm", "run", "dev"]