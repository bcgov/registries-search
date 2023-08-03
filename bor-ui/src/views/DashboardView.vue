<template>
  <v-container v-if="appReady" id="dashboard" class="container" fluid>
    <v-row no-gutters>
      <v-col>
        <h1>Director Search</h1>
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
    <v-btn
      id="doc-help-btn"
      class="copy-normal mt-3 primary px-0 text"
      flat
      :ripple="false"
      @click="showDocHelp = !showDocHelp"
    >
      <v-icon>mdi-help-circle-outline</v-icon>
      <span v-if="!showDocHelp">Help with Director Search</span>
      <span v-else>Hide Help</span>
    </v-btn>
    <v-slide-y-transition>
      <div v-if="showDocHelp" class="doc-help-info mb-10 mt-5 pb-16 pt-6">
        <div class="doc-help-info__content mx-auto">
          <h3 style="text-align: center;">Help with Director Search</h3>
          <h3 class="mt-6">Search</h3>
          <p class="mt-6">
            The Beta version of Director Search returns results for people
            associated with all businesses in British Columbia.
          </p>
          <p class="mt-6">
            You can find people by searching for any part of the person's name,
            or you can enter an address to find people by address. Note that all searches
            priortize name matches, so searches for an address will list name matches first.
            For example, searches for Parker Ave. will list matches for peoples' names containing
            Parker above addresses containing Parker.
          </p>
          <h3 class="mt-6">Business Information</h3>
          <p class="mt-6">
            You can directly view information for the business types listed below in Director Search.
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
        </div>
        <span class="doc-help-info__close-btn my-5" @click="showDocHelp = false">Hide help</span>
      </div>
    </v-slide-y-transition>

    <!-- NB: will be added back in once this includes more than just director search -->
    <!-- <v-tabs v-model="tab" style="height: 65px; margin-top: 20px;">
      <v-tab
        id="search-tab"
        :class="['tab-item-default', tab == '0' ? 'tab-item-active' : 'tab-item-inactive']"
        :ripple="false"
      >
        <v-icon>mdi-magnify</v-icon>
        <b class="ml-1">Find a Director</b>
      </v-tab>
    </v-tabs> -->

    <v-window class="mt-5" v-model="tab">
      <v-window-item class="ma-0">
        <v-card class="window-item-card" flat>
          <p class="mb-7 mt-12 info-text">
            Search for the names and addresses of people associated with businesses in BC.
          </p>
          <search-bar class="pb-5" />
          <search-results class="mt-30px" v-if="search.results!=null" />
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