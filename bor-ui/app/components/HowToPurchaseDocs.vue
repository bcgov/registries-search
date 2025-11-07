<script setup lang="ts">
const { tm, rt } = useI18n()
const parseHowToAccessDisclaimer = () => {
  const translations: unknown = tm('text.howToAccessBusinessDocumentsDisclaimer')
  if (translations instanceof Array) {
    return translations.map(translation => rt(translation))
  }
}
const howToAccessDisclaimerTexts = parseHowToAccessDisclaimer()

const bcOnlineURL = useRuntimeConfig().public.bconlineUrl
const docSearchURL = 'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business/permits-licences/businesses-incorporated-companies/searches-certificates'
</script>

<template>
  <div class="space-y-3">
    <h2>{{ $t('label.howToAccessBusinessDocuments') }}</h2>
    <div class="space-y-1">
      <p>{{ $t('text.howToAccessBusinessDocuments1') }}</p>
      <p>{{ $t('text.howToAccessBusinessDocuments2') }}</p>
      <p>{{ $t('text.howToAccessBusinessDocuments3') }}</p>
      <p>{{ $t('text.howToAccessBusinessDocuments4') }}</p>
    </div>
    <div class="flex space-x-2">
      <p>*</p>
      <p>
        {{ howToAccessDisclaimerTexts![0] }}
        <UButton
          class="text-base p-0 underline"
          :label="$t('label.bcOnline')"
          target="_blank"
          :to="bcOnlineURL"
          trailing-icon="i-mdi-open-in-new"
          variant="link"
        />
        {{ howToAccessDisclaimerTexts![1] }}
        <UButton
          class="p-0 underline text-base"
          :label="$t('text.submitADocumentSearchRequest')"
          target="_blank"
          :to="docSearchURL"
          trailing-icon="i-mdi-open-in-new"
          variant="link"
        />
        .
      </p>
    </div>
  </div>
</template>
