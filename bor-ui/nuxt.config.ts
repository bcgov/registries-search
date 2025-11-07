import { createResolver } from 'nuxt/kit'

const { resolve } = createResolver(import.meta.url)

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-08-25',
  devtools: { enabled: true },

  extends: ['@sbc-connect/nuxt-business-base'],

  imports: {
    dirs: ['enums', 'types', 'interfaces', 'stores']
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
      registriesSearchApiVersion2: '',
      registriesSearchApiKey: '',
      searchRows: ''
    }
  }
})
