import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
  plugins: [
    vue(),
    Icons({ compiler: 'vue3' }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.spec.js'],
    restoreMocks: true,
    coverage: {
      // Istanbul mede o que realmente executou; com v8, telas só importadas apareciam como 100% cobertas.
      provider: 'istanbul',
      // Mede todo o código-fonte, inclusive arquivos sem teste, para a porcentagem não ficar inflada.
      include: ['src/**/*.{js,vue}'],
      exclude: ['src/**/*.spec.js', 'src/main.js'],
      reporter: ['text', 'html'],
      // Meta da disciplina para o frontend: abaixo disso, o comando falha.
      thresholds: { lines: 25, statements: 25 },
    },
  },
})
