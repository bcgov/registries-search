// vitest.config.ts
import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    dir: './tests/unit',
    include: ['**/*.test.ts'],
    environmentOptions: {
      nuxt: {
        domEnvironment: 'happy-dom', // 'happy-dom' (default) or 'jsdom'
        overrides: {
          // other Nuxt config you want to pass
        }
      }
    }
  }
})
