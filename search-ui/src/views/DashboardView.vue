<template>
  <v-container v-if="appReady" id="dashboard" class="container px-5 py-7" fluid>
    <v-row>
      <v-col>
        <h1 style="display: flex;">
          Business Search
          <span class="beta-version">
            <v-tooltip location="bottom" content-class="tooltip__beta-version px-2" :model-value="showBetaTooltip">
              <template v-slot:activator="{ isActive, props }">
                <div v-if="isActive" class="bottom-tooltip-arrow beta-version__tooltip-arrow"></div>
                <span v-bind="props" class="beta-version__text pl-2" @click="showBetaTooltip = true">BETA</span>
              </template>
              <div
                v-if="betaTooltipOpen"
                class="pa-1"
                style="pointer-events: all"
                v-click-outside="triggerBetaTooltipOff"
              >
                <v-btn class="beta-version__close-btn float-right" icon @click="triggerBetaTooltipOff">
                  <v-icon siz="32">mdi-window-close</v-icon>
                </v-btn>
                <div class="beta-version__info px-3 py-4">
                  <p class="pt-1">
                    Business Search is available as a Beta version. The Business
                    Search Beta allows you to search for most businesses types
                    registered in B.C., but you can only retrieve full information
                    for Benefit Companies, active Cooperative Associations, Sole
                    proprietorships, and General partnerships.
                  </p>
                  <p class="pt-3">
                    Some features of this site may not function as intended,
                    and if you encounter this, please contact us:
                  </p>
                  <p class="pt-3">Toll Free: 1-877-526-1526</p>
                  <p>Victoria Office: 250-387-7848</p>
                  <p>BCRegistries@gov.bc.ca</p>
                  <p class="pt-3">
                    As part of a modern agile software development process the
                    Business Search website will be continually updated and improved
                    based on feedback from citizens and businesses in B.C.
                  </p>
                </div>
              </div>
            </v-tooltip>
          </span>
        </h1>
      </v-col>
      <v-col cols="auto">
        <a class="learn-more" :href="learnMoreURL" target="_blank">
          Learn More
          <v-icon class="learn-more__icon">mdi-open-in-new</v-icon>
        </a>
      </v-col>
    </v-row>
    <v-row class="mt-1 py-2" justify="start" no-gutters>
      <v-col class="account-label pr-5" cols="auto">
        {{ auth.currentAccount.label }}
      </v-col>
      <v-col class="account-name pl-5" cols="auto">
        {{ auth.currentAccount.name }}
      </v-col>
    </v-row>
    <v-btn class="doc-help copy-normal primary mt-5 px-0 text" flat :ripple="false" @click="showDocHelp = !showDocHelp">
      <v-icon class="mr-1">mdi-help-circle-outline</v-icon>
      <span v-if="!showDocHelp">Which Documents Can I Access?</span>
      <span v-else>Hide Document Help</span>
    </v-btn>
    <v-fade-transition>
      <div v-if="showDocHelp" class="doc-help__info mb-5 ml-7">
        <p>The documents available through business search include</p>
        <ul class="ml-4 mt-3">
          <li>Business Summary</li>
          <li>Filing History Documents (ledger filings)</li>
          <li>Certificate of Status</li>
          <li>Certificate of Good Standing</li>
          <li>Letter Under Seal</li>
        </ul>
        <p class="mt-3">
          In the beta version of Business Search you can access documents
          for the following active and historical business types:
        </p>
        <ul class="ml-4 mt-3">
          <li>Benefit Companies</li>
          <li>Cooperative Associations (active only)</li>
          <li>Sole Proprietorships and</li>
          <li>General Partnerships.</li>
        </ul>
        <p class="mt-3">
          To access documents for other business types, you will need to
          search through <a class="doc-help__info__link" :href="bcOnlineURL" target="_blank">BC OnLine</a>, or
          <a class="doc-help__info__link" :href="requestDocURL" target="_blank">request a document search</a>.
        </p>
      </div>
    </v-fade-transition>

    <v-tabs class="mt-2" v-model="tab">
      <v-tab id="search-tab" :class="['tab-item-default', tab == '0' ? 'tab-item-active' : 'tab-item-inactive']">
        <v-icon>mdi-magnify</v-icon>
        <span class="ml-1">Find a Business</span>
      </v-tab>
      <v-tab id="documents-tab" :class="['tab-item-default', tab == '1' ? 'tab-item-active' : 'tab-item-inactive']">
        <v-icon>mdi-file-document-edit-outline</v-icon>
        <span class="ml-1">
          View Recently Purchased Documents
          <span class="ml-1" v-if="documentAccessRequest._loading">
            <v-progress-circular indeterminate size="22" />
          </span>
          <span v-else>({{ totalDocAccessLength }})</span>
        </span>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card class="pa-0" flat>
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
              <p class="mx-7 my-10 info-text">
                Search for businesses registered or incorporated in B.C.&#42; or
                for owners of Firms registered in B.C.
              </p>
              <search-bar class="px-7" />
              <p class="mx-7 my-10 info-text">
                &#42;Note: The beta version of business search will not retrieve Railways, Financial Institutions, or
                businesses incorporated under Private acts.
              </p>
              <search-results v-if="search.results!=null" />
            </div>
          </v-fade-transition>
        </v-card>
      </v-window-item>
      <v-window-item>
        <v-card class="pa-0" flat>
          <p class="mx-7 my-10 info-text">
            This table will display up to 1000 of the most recent document purchases in the last 14 days
          </p>
          <document-access-request-history />
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>


<script setup lang="ts">
// local
import { computed, nextTick, ref, watch } from 'vue'
import { DocumentAccessRequestHistory, SearchBar, SearchResults } from '@/components'
import { useAuth, useDocumentAccessRequest, useSearch } from '@/composables'

const props = defineProps({ appReady: { type: Boolean } })

const { auth } = useAuth()
const { documentAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()
const { search } = useSearch()

const bcOnlineURL = 'https://www.bconline.gov.bc.ca'
const learnMoreURL = 'https://www2.gov.bc.ca/gov/content?id=B75BE1375F084B138B60D62C0094D9E8'
const requestDocURL = 'https://www2.gov.bc.ca/gov/content?id=B75BE1375F084B138B60D62C0094D9E8'
const showDocHelp = ref(false)
const tab = ref('0')

const totalDocAccessLength = computed(() => documentAccessRequest.requests?.length || 0)

const showBetaTooltip = ref(false)
// NB: needed for v-click-outside to work properly
const betaTooltipOpen = ref(false)
const triggerBetaTooltipOff = () => {
  if (betaTooltipOpen.value) {
    showBetaTooltip.value = false
    betaTooltipOpen.value = false
  }
}

const unavailableMsg = 'Business Search is in the process of a scheduled ' +
  ' update. Searching will be unavailable for up to 15 minutes.'

watch(() => showBetaTooltip.value, async (val) => {
  if (val) {
    await nextTick()
    betaTooltipOpen.value = val
  }
})

watch(() => props.appReady, (ready: boolean) => {
  if (ready) {
    loadAccessRequestHistory()
  }
})


</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
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
    color: $BCgovBlue4;
    cursor: pointer;
    font-size: 0.9rem;
  }

  &__close-btn {
    background-color: transparent;
    box-shadow: none;
    height: 30px;
    pointer-events: all;
    width: 30px;
  }
}

.doc-help {

  &__info {
    max-width: 50%;

    &__link {
      color: inherit;
      white-space: nowrap;
      text-decoration: underline;
    }
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
  background-color: #003366;
}

.tab-item-active {  
  color: #495057;
  background-color: white;
}

.tab-item-default {
  width: 50%;
  min-width: 50%;
  font-weight: bold;
}

.v-list-item {
    padding-left: 0;    
}

.warning-icon {
  color: $BCgovGold7;
}
</style>