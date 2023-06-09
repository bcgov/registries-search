<template>
  <v-container v-if="appReady" id="dashboard" class="container" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>Business Search</h1>
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
        <span v-if="auth.currentAccount.accountType === AccountTypes.STAFF">BC Registries Staff</span>
        <span v-else>{{ auth.currentAccount.label }}</span>
      </v-col>
      <v-col class="account-name pl-5" cols="auto">
        {{ auth.currentAccount.name }}
      </v-col>
    </v-row>
    <v-btn class="doc-help-btn copy-normal primary px-0 text" flat :ripple="false" @click="showDocHelp = !showDocHelp">
      <v-icon>mdi-help-circle-outline</v-icon>
      <span v-if="!showDocHelp">Help with Business Search</span>
      <span v-else>Hide Help</span>
    </v-btn>
    <v-slide-y-transition>
      <div v-if="showDocHelp" class="doc-help-info mb-10 mt-5 pb-16 pt-6">
        <div class="doc-help-info__content mx-auto">
          <h3 style="text-align: center;">Help with Business Search</h3>
          <p class="mt-5">
            In the Beta version of Business Search you can access documents for
            the following active and historical business types:
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
        <b class="ml-1">Find a Business</b>
      </v-tab>
      <v-tab
        id="documents-tab"
        :class="['tab-item-default', tab == '1' ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <v-icon style="margin-bottom: 2px;">mdi-file-document-outline</v-icon>
        <b class="mx-1">View Recently Purchased Documents</b>
        <span class="ml-1" v-if="documentAccessRequest._loading">
          <v-progress-circular indeterminate size="22" />
        </span>
        <span v-else-if="totalDocAccessLength">({{ totalDocAccessLength }})</span>
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
                or for owners of firms, and access their business documents.
              </p>
              <search-bar class="pb-5" />
              <search-results class="mt-30px" v-if="search.results!=null && !search.unavailable" />
            </div>
          </v-fade-transition>
        </v-card>
      </v-window-item>
      <v-window-item>
        <v-card class="window-item-card" flat>
          <p class="info-text mt-50px">
            This table will display up to 1000 of the most recent document purchases in the last 14 days.
          </p>
          <document-access-request-history />
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>


<script setup lang="ts">
// local
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DocumentAccessRequestHistory, SearchBar, SearchResults } from '@/components'
import { useAuth, useDocumentAccessRequest, useSearch } from '@/composables'
import { AccountTypes, RouteNames } from '@/enums';

const props = defineProps({ appReady: { type: Boolean } })

const { auth } = useAuth()
const { documentAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()
const { search } = useSearch()

const bcOnlineURL = 'http://www.bconline.gov.bc.ca/'
const learnMoreURL = 'https://www2.gov.bc.ca/gov/content?id=B75BE1375F084B138B60D62C0094D9E8'
const requestDocURL = 'https://www2.gov.bc.ca/gov/content/employment-business/business/managing-a-business' +
  '/permits-licences/businesses-incorporated-companies/searches-certificates#submit'
const showDocHelp = ref(false)
const tab = ref('0')

const totalDocAccessLength = computed(() => documentAccessRequest.requests?.length)

const unavailableMsg = 'Business Search is in the process of a scheduled ' +
  ' update. Searching will be unavailable for up to 15 minutes.'

const route = useRoute()
const router = useRouter()

watch(() => props.appReady, (ready: boolean) => {
  if (ready) {
    if (route.query?.identifier) {
      router.push({
        name: RouteNames.BUSINESS_INFO,
        params: { identifier: route.query?.identifier }
      })
    }
    loadAccessRequestHistory()
  }
})


</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
#documents-tab {
  border-left: 2.5px solid $gray1;
}

#search-tab {
  border-right: 2.5px solid $gray1;
}

.account-label {
  padding-left: 2px !important;
}
.account-label + .account-name {
  border-left: 1px solid $gray4;
}
.beta-version {
  display: flex;
  position: relative;

  &__tooltip-arrow {
    left: 35%;
    margin-top: 22px;
  }

  &__text {
    line-height:10px;
    text-decoration: underline;
    font-weight: bold;
    color: $primary-blue;
    cursor: pointer;
    font-size: 0.9rem;
  }

  &__close-btn {
    background-color: transparent;
    box-shadow: none;
    font-size: .875rem;
    height: 30px;
    pointer-events: all;
    width: 30px;
  }

  &__info {
    font-size: 0.825rem;
    line-height: 1.125rem;

    a {
      color: white;
    }
  }
}

.doc-help-btn {
  margin-top: 14px;
}

.doc-help-info {
  border-bottom: 1px dashed $gray7;
  border-top: 1px dashed $gray7;

  &__content {
    max-width: 60%;

    &__link {
      color: $primary-blue;
      white-space: nowrap;
      text-decoration: none;

      &__icon {
        font-size: 1rem;
        color: $primary-blue;
      }
    }
  }

  &__close-btn {
    color: $primary-blue;
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
  color: $primary-blue;
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
  background-color: $primary-blue;
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

.v-list-item {
    padding-left: 0;    
}

.warning-icon {
  color: $BCgovGold7;
}

.window-item-card {
  padding: 0 30px 30px 30px;
}
</style>