<script setup lang="ts">
const { accessLevel } = storeToRefs(useSearchAccessStore())

const showDocHelp = ref(false)

const bcOnlineURL = useRuntimeConfig().public.bconlineUrl as string
</script>

<template>
  <div>
    <UButton
      class="p-0"
      icon="i-mdi-help-circle-outline"
      :label="showDocHelp ? $t('label.hideHelp') : $t('label.helpWithBPS')"
      variant="link"
      data-testid="search-help-btn"
      @click="showDocHelp = !showDocHelp"
    />
    <div v-if="showDocHelp" class="border-y border-dashed mb-10 mt-5 pt-6">
      <div class="max-w-[60%] mx-auto space-y-6">
        <h3 style="text-align: center;">
          {{ $t('label.helpWithBPS') }}
        </h3>
        <h3>
          {{ $t('label.search') }}
        </h3>
        <p>
          {{ $t(`search.person.${accessLevel}.help1`) }}
        </p>
        <p>
          {{ $t(`search.person.${accessLevel}.help2`) }}
        </p>
        <h3>
          {{ $t('label.businessInformation') }}
        </h3>
        <p>
          {{ $t('text.viewBusinessInformationHelp') }}
          <UButton
            class="text-base p-0"
            :to="bcOnlineURL"
            label="BC OnLine"
            icon="i-mdi-open-in-new"
            target="_blank"
            trailing
            variant="link"
          />
          .
        </p>
        <ul class="ml-4">
          <li>{{ $t('label.benefitCompanies') }}</li>
          <li>{{ $t('label.cooperativeAssociationsActive') }}</li>
          <li>{{ $t('label.soleProprietorships') }}</li>
          <li>{{ $t('label.generalPartnerships') }}</li>
        </ul>
        <p>
          {{ $t('text.whereAvailDocsInclude') }}
        </p>
        <ul class="ml-4">
          <li>{{ $t('label.businessSummary') }}</li>
          <li>{{ $t('label.filingHistoryDocsLedger') }}</li>
          <li>{{ $t('label.certStatus') }}</li>
          <li>{{ $t('label.certGoodStanding') }}</li>
          <li>{{ $t('label.letterUnderSeal') }}</li>
        </ul>
      </div>
      <div class="flex justify-end">
        <UButton
          class="my-6 p-0"
          :label="$t('label.hideHelp')"
          variant="link"
          @click="showDocHelp = !showDocHelp"
        />
      </div>
    </div>
  </div>
</template>
