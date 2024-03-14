<template>
  <div class="container mt-8 mb-16">
    <v-row no-gutters>
      <v-col>
        <h1>{{ searchTitleText }}</h1>
      </v-col>
    </v-row>
    <v-row class="mt-1 pt-2" justify="start" no-gutters>
      <v-col class="account-label pr-5" cols="auto">
        <span v-if="currentAccount.accountType === AccountTypeE.STAFF">BC Registries Staff</span>
        <span v-else>{{ currentAccountName }}</span>
      </v-col>
      <v-col class="account-name pl-5" cols="auto">
        {{ userFullName }}
      </v-col>
    </v-row>
    <v-btn
      id="doc-help-btn"
      class="copy-normal mt-3 primary px-0 text"
      flat
      :ripple="false"
      @click="showDocHelp = !showDocHelp"
    >
      <v-icon>mdi-help-circle-outline</v-icon>
      <span v-if="!showDocHelp">Help with {{ searchTitleText }}</span>
      <span v-else>Hide Help</span>
    </v-btn>
    <v-slide-y-transition>
      <div v-if="showDocHelp" class="doc-help-info mb-10 mt-5 pb-16 pt-6">
        <div class="doc-help-info__content mx-auto">
          <h3 style="text-align: center;">
            Help with {{ searchTitleText }}
          </h3>
          <h3 class="mt-6">
            Search
          </h3>
          <p v-if="!isExtended" class="mt-6">
            The Beta version of Director Search returns results for people
            associated with all businesses in British Columbia.
          </p>
          <p class="mt-6">
            You can find people by searching for any part of the person's name or address, or
            their business email address. Note that all searches prioritize name matches, so
            searches for an address will list name matches first. For example,
            searches for Parker Ave. will list matches for peoples' names containing Parker
            above addresses containing Parker.
          </p>
          <h3 class="mt-6">
            Business Information
          </h3>
          <p class="mt-6">
            You can directly view information for the business types listed below in {{ searchTitleText }}.
            Information for other business types can be obtained through
            <a class="doc-help-info__content__link" :href="bcOnlineURL" target="_blank">
              <span style="text-decoration: underline;">BC OnLine</span>
              <v-icon class="doc-help-info__content__link__icon ml-1">mdi-open-in-new</v-icon>
            </a>.
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
            <a class="learn-more" :href="searchGuideURL" target="_blank">
              Learn how to use {{ searchTitleText }} - User Guide
              <v-icon class="learn-more__icon">mdi-open-in-new</v-icon>
            </a>
          </div>
        </div>
        <span class="doc-help-info__close-btn my-6" @click="showDocHelp = false">Hide help</span>
      </div>
    </v-slide-y-transition>

    <v-window v-model="tab" class="mt-5">
      <v-window-item class="ma-0">
        <v-card class="window-item-card" flat>
          <p class="mb-7 mt-12 info-text" data-cy="search-input-info-text">
            {{ searchInfoText }}
          </p>
          <search-input class="pb-5" />
          <search-results-table v-if="results!=null" class="mt-30px" />
        </v-card>
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup lang="ts">
const account = useBcrosAccount()
const { currentAccount, currentAccountName, userFullName } = storeToRefs(account)
const { isExtended, results } = storeToRefs(useBcrosSearch())

const searchTitleText = computed(() => isExtended.value ? 'Business and Person Search' : 'Director Search')
const searchInfoText = computed(() => {
  if (isExtended.value) {
    // eslint-disable-next-line
    return 'Search for the names, addresses, SIN/TTN/ITN, and business email addresses of people associated with businesses in B.C.'
  }
  return 'Search for the names, addresses, and business email addresses of people associated with businesses in B.C.'
})

const bcOnlineURL = useRuntimeConfig().public.bcolURL
const searchGuideURL = computed(() => {
  if (isExtended.value) { return '' }
  // eslint-disable-next-line
  return 'https://www2.gov.bc.ca/assets/gov/employment-business-and-economic-development/business-management/permits-licences-and-registration/registries-other-assets/director_search_quick_guide.pdf'
})
const showDocHelp = ref(false)
const tab = ref('0')
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#search-tab {
  border-right: 2.5px solid $gray1;
}

.account-label {
  padding-left: 2px !important;
}
.account-label + .account-name {
  border-left: 1px solid $gray4;
}

.doc-help-info {
  border-bottom: 1px dashed $gray7;
  border-top: 1px dashed $gray7;

  &__content {
    max-width: 60%;

    &__link {
      color: $app-blue;
      white-space: nowrap;
      text-decoration: none;

      &__icon {
        font-size: 1rem;
        color: $app-blue;
      }
    }
  }

  &__close-btn {
    color: $app-blue;
    cursor: pointer;
    float: right;
    font-size: .875rem;
    text-decoration: underline;
    white-space: nowrap;
  }
}

.info-text {
  font-size: 1rem;
  color: $gray7
}

.learn-more {
  color: $app-blue;
  text-decoration: none;

  &__icon,
  &__icon::before {
    font-size: 18px;
    margin-top: -1px;
  }
}

.tab-item-inactive {
  color: white;
  background-color: $BCgovBlue5;
  box-shadow: inset 0 0 5px 1px $gray9;
  margin-top: 5px;
  transition: none !important;
}
.tab-item-inactive:hover {
  background-color: $app-blue;
  box-shadow: none;
}

.tab-item-active {
  color: $gray8;
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

.tooltip-search-tab {
  position: relative;

  &__arrow {
    right: 119px;
    top: -10px;
  }

  &__text {
    // border-bottom: 1px dotted $gray7;
    text-decoration: underline dotted 1px;
    margin-right: 2px;
  }
}

.warning-icon {
  color: $BCgovGold7;
}

.window-item-card {
  padding: 0 30px 30px 30px;
}
</style>
