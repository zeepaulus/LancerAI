import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Bắt buộc phải có để chạy trong Docker
    port: 3000,
    watch: {
      usePolling: true, // Ép Vite phải quét file liên tục để nhận diện thay đổi
      interval: 100,    // Quét mỗi 100ms
    }
  },
});