import { createResolver } from 'nuxt/kit'

const { resolve } = createResolver(import.meta.url)

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  extends: ['@sbc-connect/nuxt-pay', '@sbc-connect/nuxt-forms'],

  imports: {
    dirs: ['enums', 'interfaces', 'stores']
  },

  app: {
    head: {
      title: 'Business and Person Search'
    }
  },

  alias: {
    BeneficialOwnerIcon: resolve('./public/icons/shares-votes/beneficial-owner.svg'),
    IndirectControlIcon: resolve('./public/icons/shares-votes/indirect-control.svg'),
    RegisteredOwnerIcon: resolve('./public/icons/shares-votes/registered-owner.svg'),
    DirectorsDirectControlIcon: resolve('./public/icons/directors/direct-control.svg'),
    DirectorsIndirectControlIcon: resolve('./public/icons/directors/indirect-control.svg'),
    DirectorsSignificanInfluenceIcon: resolve('./public/icons/directors/significant-influence.svg'),
    OtherIcon: resolve('./public/icons/other.svg')
  },

  i18n: {
    locales: [
      {
        name: 'English',
        code: 'en-CA',
        language: 'en-CA',
        dir: 'ltr',
        file: 'en-CA.ts'
      },
      {
        name: 'Français',
        code: 'fr-CA',
        language: 'fr-CA',
        dir: 'ltr',
        file: 'fr-CA.ts'
      }
    ]
  },

  runtimeConfig: {
    public: {
      bconlineUrl: '',
      borApiUrl: '',
      borApiVersion: '',
      borApiKey: '',
      businessDashUrl: '',
      registriesSearchApiUrl: '',
      registriesSearchApiVersion: '',
      registriesSearchApiVersion2: '',
      registriesSearchApiKey: '',
      registriesSearchUrl: '',
      searchRows: ''
    }
  }
})
