import fs from 'fs'
import { createResolver } from 'nuxt/kit'

const { resolve } = createResolver(import.meta.url)

export const getSearchResultsMock = (type: 'Business' | 'Extended' | 'Limited' | 'Public') => {
  const resultJson = fs.readFileSync(resolve(`./json/searchResults${type}.json`), 'utf8')
  return JSON.parse(resultJson)
}
