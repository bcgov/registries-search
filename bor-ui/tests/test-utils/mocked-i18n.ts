import { createI18n } from 'vue-i18n'
import en from '~/lang/en.json'

export const mockedI18n = createI18n({
  locale: 'en',
  messages: { en }
})
