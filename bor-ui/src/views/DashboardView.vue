<template>
  <v-container v-if="appReady" id="dashboard" class="container" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>Business and Person Search</h1>
      </v-col>
      <v-col class="pt-3" cols="auto">
        <a class="learn-more" :href="learnMoreURL" target="_blank">
          Learn More
          <v-icon class="learn-more__icon">mdi-open-in-new</v-icon>
        </a>
      </v-col>
    </v-row>
    <v-row class="mt-1 pt-2" justify="start" no-gutters>
      <v-col class="account-label pr-5" cols="auto">
        <span v-if="auth.currentAccount.accountType === AccountType.STAFF">BC Registries Staff</span>
        <span v-else>{{ auth.currentAccount.label }}</span>
      </v-col>
      <v-col class="account-name pl-5" cols="auto">
        {{ auth.currentAccount.name }}
      </v-col>
    </v-row>
    <v-btn class="doc-help-btn copy-normal primary px-0 text" flat :ripple="false" @click="showDocHelp = !showDocHelp">
      <v-icon>mdi-help-circle-outline</v-icon>
      <span v-if="!showDocHelp">Help with Business and Person Search</span>
      <span v-else>Hide Help</span>
    </v-btn>
    <v-slide-y-transition>
      <div v-if="showDocHelp" class="doc-help-info mb-10 mt-5 pb-16 pt-6">
        <div class="doc-help-info__content mx-auto">
          <h3 style="text-align: center;">Help with Business and Person Search</h3>
          <p class="mt-5">
            This text has not been updated for Business and Person Search
          </p>
          <ul class="ml-4 mt-6">
            <li>Benefit Companies</li>
            <li>Cooperative Associations (active only)</li>
            <li>Sole Proprietorships</li>
            <li>General Partnerships</li>
          </ul>
          <p class="mt-6">
            Documents that may be available through Business Search include:
          </p>
          <ul class="ml-4 mt-6">
            <li>Business Summary</li>
            <li>Filing History Documents (ledger filings)</li>
            <li>Certificate of Status</li>
            <li>Certificate of Good Standing</li>
            <li>Letter Under Seal</li>
          </ul>
          <p class="mt-6">
            <b>Note:</b> The Beta version of Business Search will not retrieve railways,
            financial institutions, or businesses incorporated under Private Acts.
          </p>
          <p class="mt-6">
            To access documents for other business types, you will need to search through
            <a class="doc-help-info__content__link" :href="bcOnlineURL" target="_blank">
              <span style="text-decoration: underline;">BC OnLine</span>
              <v-icon class="doc-help-info__content__link__icon ml-1">mdi-open-in-new</v-icon>
            </a>, or you may
            <a class="doc-help-info__content__link" :href="requestDocURL" target="_blank">
              <span style="text-decoration: underline;">submit a document search request</span>
              <v-icon class="doc-help-info__content__link__icon ml-1">mdi-open-in-new</v-icon>
            </a>.
          </p>
        </div>
        <span class="doc-help-info__close-btn my-5" @click="showDocHelp = false">Hide help</span>
      </div>
    </v-slide-y-transition>

    <v-tabs v-model="tab" style="height: 65px; margin-top: 20px;">
      <v-tab
        id="search-tab"
        :class="['tab-item-default', tab == '0' ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <v-icon>mdi-magnify</v-icon>
        <b class="ml-1">Find a Business or Person</b>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card class="window-item-card" flat>
          <v-fade-transition hide-on-leave>
            <div v-if="search.unavailable">
              <v-row class="my-16" justify="center" no-gutters>
                <v-col cols="auto">
                  <v-progress-circular color="primary" size="50" indeterminate />
                </v-col>
                <v-col class="mt-5" cols="12" style="text-align: center;">
                  <v-icon class="ml-10 warning-icon" size="25">mdi-alert</v-icon>
                  <span class="ml-1 info-text">{{ unavailableMsg }}</span>
                </v-col>
              </v-row>
            </div>
            <div v-else>
              <p class="mb-7 mt-12 info-text">
                Search for businesses
                <v-tooltip location="top" content-class="bottom-arrow" transition="fade-transition">
                  <template v-slot:activator="{ props }">
                    <span class="tooltip-search-tab" style="position: relative;">
                      <span class="tooltip-search-tab__text" v-bind="props">
                        registered or incorporated in B.C.
                      </span>
                    </span>
                  </template>
                  <span>
                    <b>Note:</b> The Beta version of business search will not
                    retrieve railways, financial institutions, or businesses
                    incorporated under Private Acts.
                  </span>
                </v-tooltip>
                or Directors / Owners of businesses or Addresses of businesses and people.
              </p>
              <search-bar class="pb-5" />
              <search-results class="mt-30px" v-if="search.results!=null && !search.unavailable" />
            </div>
          </v-fade-transition>
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>


<script setup lang="ts">
// external
import { ref } from 'vue'
// local
import { SearchBar, SearchResults } from '@/components'
import { useAuth, useSearch } from '@/composables'
import { AccountType } from '@/enums';

// eslint-disable-next-line
const props = defineProps<{ appReady: boolean }>()

const { auth } = useAuth()
const { search } = useSearch()

const bcOnlineURL = 'http://www.bconline.gov.bc.ca/'
const learnMoreURL = 'https://www2.gov.bc.ca/gov/content?id=B75BE1375F084B138B60D62C0094D9E8'
const requestDocURL = 'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business' +
  '/permits-licences/businesses-incorporated-companies/searches-certificates#submit'
const showDocHelp = ref(false)
const tab = ref('0')

const unavailableMsg = 'Business and Person Search is in the process of a scheduled ' +
  ' update. Searching will be unavailable for up to 15 minutes.'


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
  height: 67px;
  width: 50%;
  min-width: 50%;
  font-size: 1.125rem;
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