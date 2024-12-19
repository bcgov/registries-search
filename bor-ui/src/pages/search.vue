<template>
  <div class="mt-8 mb-16" data-cy="search-page">
    <h1>{{ searchTitleText }}</h1>
    <div v-if="currentAccount?.id" class="flex mt-1 pt-2">
      <div class="pl-[2px] pr-5 border-r-[1px] border-bcGovGray-400" data-cy="account-name">
        <span v-if="currentAccount.accountType === AccountTypeE.STAFF">BC Registries Staff</span>
        <span v-else>{{ currentAccountName }}</span>
      </div>
      <div class="pl-5" data-cy="user-name">
        {{ userFullName }}
      </div>
    </div>
    <UButton
      class="mt-3 text-base"
      icon="i-mdi-help-circle-outline"
      :label="showDocHelp ? 'Hide Help' : 'Help with ' + searchTitleText"
      variant="link"
      data-cy="search-help-btn"
      @click="showDocHelp = !showDocHelp"
    />
    <div v-if="showDocHelp" class="doc-help-info mb-10 mt-5 pt-6">
      <div class="doc-help-info__content mx-auto">
        <h3 style="text-align: center;">
          Help with {{ searchTitleText }}
        </h3>
        <h3 class="mt-6">
          Search
        </h3>
        <p class="mt-6">
          The Person Search returns results for people
          associated with all businesses in British Columbia.
        </p>
        <p v-if="hasExtendedAccess" class="mt-6">
          You can find people by searching for any part of the person's name, preferred name, address,
          email, or SIN. Note that all searches prioritize name matches, so
          searches for an address will list name matches first. For example,
          searches for Parker Ave. will list matches for peoples' names containing Parker
          above addresses containing Parker.
        </p>
        <p v-else-if="hasLimitedAccess" class="mt-6">
          You can find people by searching for any part of the person's name or address, or
          their business email address. Note that all searches prioritize name matches, so
          searches for an address will list name matches first. For example,
          searches for Parker Ave. will list matches for peoples' names containing Parker
          above addresses containing Parker.
        </p>
        <p v-else class="mt-6">
          You can find people by searching for any part of the person's name.
        </p>
        <h3 class="mt-6">
          Business Information
        </h3>
        <p class="mt-6">
          You can directly view information for the business types listed below in {{ searchTitleText }}.
          Information for other business types can be obtained through
          <UButton
            class="text-base"
            :to="bcOnlineURL"
            label="BC OnLine"
            icon="i-mdi-open-in-new"
            target="_blank"
            trailing
            variant="link"
          />
          .
        </p>
        <ul class="ml-4 mt-6">
          <li>Benefit Companies</li>
          <li>Cooperative Associations (active only)</li>
          <li>Sole Proprietorships</li>
          <li>General Partnerships</li>
        </ul>
        <p class="mt-6">
          Where available, documents for these business types include:
        </p>
        <ul class="ml-4 mt-6">
          <li>Business Summary</li>
          <li>Filing History Documents (ledger filings)</li>
          <li>Certificate of Status</li>
          <li>Certificate of Good Standing</li>
          <li>Letter Under Seal</li>
        </ul>
        <div class="mt-6">
          <UButton
            class="text-base"
            :to="searchGuideURL"
            :label="`Learn how to use ${searchTitleText} - User Guide`"
            icon="i-mdi-open-in-new"
            target="_blank"
            trailing
            variant="link"
          />
        </div>
      </div>
      <div class="flex justify-end">
        <UButton
          class="my-6"
          label="Hide Help"
          variant="link"
          @click="showDocHelp = !showDocHelp"
        />
      </div>
    </div>

    <UTabs
      v-if="!hasExtendedAccess"
      class="mt-5"
      :items="tabs"
      :ui="{ list: { background: 'bg-bcGovColor-darkBlue', width: 'w-full max-w-[600px]' } }"
      data-cy="search-tabs"
    >
      <template #search>
        <Search />
      </template>
      <template #documents>
        <DocAccessHistory />
      </template>
    </UTabs>
    <Search v-else />
  </div>
</template>
<script setup lang="ts">
const account = useBcrosAccount()
const { currentAccount, currentAccountName, userFullName } = storeToRefs(account)
const { hasExtendedAccess, hasLimitedAccess } = storeToRefs(useBcrosSearchAccess())
const { searchType } = storeToRefs(useBcrosSearch())
const { t } = useNuxtApp().$i18n

const tabs = [
  { slot: 'search', label: t('label.tabs.findBusinessPerson'), icon: 'i-mdi-magnify' },
  { slot: 'documents', label: t('label.tabs.viewPurchasedDocuments'), icon: 'i-mdi-file-document-outline' }
]

const searchTitleText = t('appHeader')

const bcOnlineURL = useRuntimeConfig().public.bcolURL
const searchGuideURL = computed(() => {
  // TODO: extended/public/business search link tbd
  if (searchType.value === SearchTypeE.DIRECTOR) {
    // eslint-disable-next-line
    return 'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/permits-licences-and-registration/registries-other-assets/director_search_quick_guide.pdf'
  }
  return ''
})
const showDocHelp = ref(false)
</script>
<style lang="scss" scoped>
.doc-help-info {
  border-bottom: 1px dashed theme('colors.bcGovGray.700');
  border-top: 1px dashed theme('colors.bcGovGray.700');

  &__content {
    max-width: 60%;

    &__link {
      color: theme('colors.blue.500');
      white-space: nowrap;
      text-decoration: none;
    }
  }
}

.learn-more {
  color: theme('colors.blue.500');
  text-decoration: none;

  &__icon,
  &__icon::before {
    font-size: 18px;
    margin-top: -1px;
  }
}

.tab-item-inactive {
  color: white;
  background-color: theme('colors.bcGovColor.darkBlue');
  box-shadow: inset 0 0 5px 1px theme('colors.bcGovGray.900');
  margin-top: 5px;
  transition: none !important;
}
.tab-item-inactive:hover {
  background-color: theme('colors.blue.500');
  box-shadow: none;
}

.tab-item-active {
  color: theme('colors.bcGovGray.800');
  background-color: white;
  transition: none !important;
}

.tab-item-default {
  border-radius: 5px 5px 0 0 !important;
  font-size: 1.125rem;
  height: 67px;
  min-width: 50%;
  width: 50%;
}
</style>
