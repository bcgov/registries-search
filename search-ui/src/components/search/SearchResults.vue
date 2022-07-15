<template>
  <base-table
    v-if="search.searchType === 'business'"
    class="mt-10"
    height="100%"
    :itemKey="'identifier'"
    :loading="search._loading"
    :setHeaders="BusinessSearchHeaders"
    :setItems="search.results"
    title="Search Results"
    :totalItems="search.totalResults"
  >
    <template v-slot:item-slot-button="{ item }">
      <v-btn
        v-if="learBusinessTypes.includes(item.legalType)"
        class="btn-basic mx-auto"
        color="primary"
        large
        @click="goToBusinessInfo(item)"
      >
        Open
      </v-btn>
      <v-tooltip v-else location="top" content-class="tooltip">
        <template v-slot:activator="{ isActive, props }">
          <div v-if="isActive" class="top-tooltip-arrow" style="margin-top: -25px !important; left: 48%; !important;" />
          <v-icon class="table-icon" color="primary" size="28" v-bind="props">mdi-information-outline</v-icon>
        </template>
        <span>
          You can access this business through BC Online or by contacting BC Registries.
        </span>
      </v-tooltip>
    </template>
    <template v-slot:item-slot-icon><v-icon>mdi-domain</v-icon></template>
  </base-table>
  <base-table
    v-else
    class="mt-10"
    height="100%"
    :itemKey="'parentIdentifier'"
    :loading="search._loading"
    :setHeaders="PartySearchHeaders"
    :setItems="search.results"
    title="Search Results"
    :totalItems="search.totalResults"
  >
    <template v-slot:item-slot-button="{ item }">
      <v-btn
        v-if="learBusinessTypes.includes(item.parentLegalType)"
        class="btn-basic mx-auto"
        color="primary"
        large
        @click="goToBusinessFromParty(item)"
      >
        Open
      </v-btn>
      <v-tooltip v-else location="top" content-class="tooltip">
        <template v-slot:activator="{ isActive, props }">
          <div v-if="isActive" class="top-tooltip-arrow" style="margin-top: -22px !important; left: 48%; !important;" />
          <v-icon class="table-icon" color="primary" size="28" v-bind="props">mdi-information-outline</v-icon>
        </template>
        <span>
          You can access this business through BC Online or by contacting BC Registries.
        </span>
      </v-tooltip>
    </template>
    <template v-slot:item-slot-icon="{ item }">
      <v-icon v-if="item.partyType === 'person'">mdi-account</v-icon>
      <v-icon v-else>mdi-domain</v-icon>
    </template>
    <template v-slot:item-slot-roles="{ item }">
      <ul class="basic-list">
        <li v-for="(role, index) in item.partyRoles" :key="index">
          <span>{{ capFirstLetter(role) }}</span>
        </li>
      </ul>
    </template>
  </base-table>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
// local
import { BaseTable } from '@/components'
import { useEntity, useSearch } from '@/composables'
import { RouteNames } from '@/enums'
import { SearchPartyResultI, SearchResultI } from '@/interfaces'
import { EntityI } from '@/interfaces/entity'
import { BusinessSearchHeaders, PartySearchHeaders } from '@/resources/table-headers'

// Router
const router = useRouter()
// composables
const { learBusinessTypes, setEntity } = useEntity()
const { search } = useSearch()

// const totalResultsLength = computed(() => search.totalResults || 0 )
const goToBusinessFromParty  = (result: SearchPartyResultI)  => {
  const businessInfo: SearchResultI = {
    bn: result.parentBN,
    identifier: result.parentIdentifier,
    legalType: result.parentLegalType,
    name: result.parentName,
    status: result.parentStatus
  }
  goToBusinessInfo(businessInfo)
}
const goToBusinessInfo  = (result: SearchResultI)  => {
  const identifier = result.identifier
  setEntity(result as EntityI)
  router.push({ name: RouteNames.BUSINESS_INFO, params: { identifier } })
}

const capFirstLetter = (val: string) => val.charAt(0).toUpperCase() + val.slice(1)

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.table-icon {
  left: 45%;
  position: absolute;
  top: 18px;
}
</style>
