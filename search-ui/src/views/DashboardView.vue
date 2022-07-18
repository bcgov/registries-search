<template>
  <v-container id="dashboard" class="container px-5 py-7" fluid>
    <div>
      <v-row no-gutters>
        <v-col>
          <span class="page-header"><h1>Business Search</h1><span class="beta-version pl-2">BETA</span></span>
        </v-col>
      </v-row>
    </div>

    <v-tabs class="mt-8" v-model="tab">
      <v-tab id="search-tab" class="tab-item-default" :class="[tab == '0' ? 'tab-item-active' : 'tab-item-inactive']">
        <v-icon>mdi-magnify</v-icon>
        <span class="ml-1">Find a Business</span>
      </v-tab>
      <v-tab id="documents-tab" class="tab-item-default" :class="[tab == '1' ? 'tab-item-active' : 'tab-item-inactive']">
        <v-icon>mdi-file-document-edit-outline</v-icon>
        <span class="ml-1">View Recently Purchased Documents ({{totalDocAccessLength}})</span>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item class="ma-0">
        <v-card class="pa-0" flat>
          <p class="mx-7 my-10 info-text">
            Search for businesses registered or incorporated in B.C.&#42; or
            for owners of Firms registered in B.C.
          </p>
          <search-bar class="mx-7" />
          <p class="mx-7 my-10 info-text">
            &#42;Note: The beta version of business search will not retrieve Railways, Financial Institutions, or
            businesses incorporated under Private acts.
          </p>
          <search-results v-if="search.results!=null" />
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
import { computed, ref, watch } from 'vue'
import { DocumentAccessRequestHistory, SearchBar, SearchResults } from '@/components'
import { useDocumentAccessRequest, useSearch } from '@/composables'

const props = defineProps({ appReady: { type: Boolean } })

const tab = ref('0')

const { documentAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()
const { search } = useSearch()

const totalDocAccessLength = computed(() => documentAccessRequest.requests?.length || 0)

watch(() => props.appReady, (ready: boolean) => {
  if (ready) {
    loadAccessRequestHistory()
  }
})


</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.info-text {
  font-size: 16px;
  color: $gray7
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

.beta-version{
  line-height:10px;
  text-decoration: underline;
  font-weight: bold;
  color: $BCgovBlue4;
  font-size: 0.9rem
}

.page-header{
  display: flex;  
}
</style>