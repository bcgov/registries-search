<template>
  <div class="main-results-div white-background soft-corners-top soft-corners-bottom pb-2">
    <v-row class="result-info pt-30px pl-8" no-gutters v-if="totalResultsLength > 0">   
        <v-col cols="12">
        <b>{{ totalResultsLength }}</b> results found
        </v-col>           
    </v-row>
    <v-row class="pt-3 pl-4" no-gutters>
      <v-col cols="12">
          <v-table
          fixed-header
          class="table">
            <thead>
            <tr>
                <th width="25%" class="bg-grey-lighten-4">Business Name</th>
                <th width="15%" class="bg-grey-lighten-4">Registration Number</th>
                <th width="15%" class="bg-grey-lighten-4">Business Number</th>
                <th width="25%" class="bg-grey-lighten-4">Business Type</th>
                <th width="10%" class="bg-grey-lighten-4">Status</th>
                <th width="10%" class="bg-grey-lighten-4 opaque-header"></th>
            </tr>
            </thead>
            <tbody v-if="totalResultsLength>0">
                <tr v-for="item in businesses" :key="item.identifier">
                    <td>{{ item.name }}</td>
                    <td>{{ item.identifier }}</td>
                    <td>{{ item.bn }}</td>
                    <td>{{ getEntityDescription(item.legalType) }}</td>
                    <td>{{ item.status }}</td>
                    <td>
                        <v-btn                         
                        large
                        id="open-business-btn"                     
                        class="search-bar-btn primary mr-2"
                        @click="goToBusinessInfo(item.identifier)">
                            Open
                        </v-btn>
                       <!-- <v-tooltip
                        v-else
                        class="pa-2"
                        content-class="top-tooltip"
                        nudge-right="2"
                        top
                        transition="fade-transition">
                            <template v-slot:activator="{ props }">
                                <v-icon v-bind="props" v-on="props"
                                 class="pl-8 primary-icon">mdi-information-outline</v-icon>
                            </template>
                            <div class="pt-2 pb-2">
                             Historical Business
                            </div>
                        </v-tooltip> -->
                    </td>
                </tr>
            </tbody>
            <tbody v-else>
                <tr>
                    <td colspan="6">
                        <p class="pt-4 pb-2"><b>No results found</b></p>
                    </td>
                </tr>               
            </tbody>
        </v-table>           
      </v-col>   
    </v-row>     
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
// local
import { RouteNames } from '@/enums'
import { SearchResultI } from '@/interfaces'
import { CorpInfoArray } from '@/resources'

// Store
const store = useStore()

const router = useRouter()

const businesses = computed(() => store.getters['getSearchResults'] as SearchResultI[])
const totalResultsLength = computed(() => businesses.value.length ) 

const goToBusinessInfo  = (identifier: string )  => {  
  router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
} 

const getEntityDescription  = (entityType: string)  => {
   const item = CorpInfoArray.find(obj => (entityType === obj.corpTypeCd))
  return (item && item.fullDesc) || ''
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

button {
  font-weight: normal !important;
}

td {
  font-size: 0.875rem !important;
  color: $gray7 !important;
}

th {
  font-size: 0.875rem !important;
  color: $gray9 !important; 
}
 
.main-results-div {
  width: 100%;
}
.result-info {
  color: $gray7 !important;
  font-size: 1rem;
}

.primary-icon{
  color: $app-dk-blue !important;
}

.table{
	max-width: calc(100% - 48px);
	max-height: calc(100vh - 170px);
}
.v-table {
	overflow: auto;
}
.v-table :deep(.v-table__wrapper) {
	overflow: unset;
}

.opaque-header {
  z-index: 1;
}
</style>
