import { createResolver } from 'nuxt/kit'
import { defineConfig, devices } from '@playwright/test'
import type { ConfigOptions } from '@nuxt/test-utils/playwright'

const { resolve } = createResolver(import.meta.url)

const deviceNames = [
  'Desktop Chrome',
  ...(process.env.CI
    ? [
      'Desktop Firefox',
      'Desktop Edge',
      'Desktop Safari'
    ]
    : [])
]

export default defineConfig<ConfigOptions>({
  globalSetup: './tests/e2e/setup',
  testDir: './tests/e2e',
  testMatch: '*.spec.ts',
  workers: process.env.CI ? 2 : undefined,
  reporter: [['list'], [process.env.CI ? 'blob' : 'html']],
  use: {
    nuxt: {
      rootDir: resolve('./'),
      runner: 'vitest',
      host: process.env.NUXT_PUBLIC_BASE_URL
    },
    actionTimeout: 10000,
    baseURL: process.env.NUXT_PUBLIC_BASE_URL,
    trace: 'on',
    screenshot: 'on-first-failure',
    // do not open browser
    headless: true
  },
  projects: deviceNames.map(name => ({ name, use: devices[name] })),
  webServer: {
    command: 'pnpm build:test',
    port: 3000,
    reuseExistingServer: !process.env.CI,
    timeout: 60000,
    env: {
      playwright: 'true'
    }
  }
})
