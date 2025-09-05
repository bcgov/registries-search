import { createI18n } from 'vue-i18n'
import en from '../../../i18n/locales/en-CA'
import fr from '../../../i18n/locales/fr-CA'

export const i18nMock = createI18n({
  legacy: false,
  locale: 'en-CA',
  messages: {
    'en-CA': en,
    'fr-CA': fr
  }
})
