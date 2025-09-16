import fs from 'fs'
import { createResolver } from 'nuxt/kit'

const { resolve } = createResolver(import.meta.url)

export const getUserSettingsMock = () => {
  const userSettingsJson = fs.readFileSync(resolve('./json/settings.json'), 'utf8')
  return JSON.parse(userSettingsJson)
}
