<template>
  <v-card class="auto-complete-card" elevation="5">
    <v-row class="justify-center" no-gutters>
      <v-col>
        <v-item-group v-model="suggest.query">
          <v-row
            v-for="(result, i) in suggest.results"
            :key="i"
            class="auto-complete-row"
            no-gutters
          >
            <v-col class="title-size">
              <v-item>
                <v-label class="auto-complete-item py-2 pl-4" @click="submitSearch(result.value)">
                  <span v-html="result.value"/> 
                </v-label>
              </v-item>
            </v-col>
          </v-row>
        </v-item-group>
      </v-col>
    </v-row>
  </v-card>
</template>

<script setup lang="ts">
// local
import { useSearch, useSuggest } from '@/composables'

const { getSearchResults } = useSearch()
const { suggest } = useSuggest()

const submitSearch = (val: string) => {
  suggest.disabled = true
  suggest.query = val
  getSearchResults(suggest.query)
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

#auto-complete-close-btn {
  color: $gray5 !important;
  background-color: transparent !important;
}
.auto-complete-item {
  min-height: 0;
  width: 100%;
}

.auto-complete-card {
  z-index: 3;
}

.auto-complete-item:hover {
  color: $primary-blue !important;
  background-color: $gray1 !important;
}

.auto-complete-item[aria-selected='true'] {
  color: $primary-blue !important;
  background-color: $blueSelected !important;
}
.auto-complete-item:focus {
  background-color: $gray3 !important;
}

.auto-complete-row {
  color: $gray7 !important;
}
.auto-complete-row:hover {
  color: $primary-blue !important;
}
.close-btn {
  background-color: transparent;
  box-shadow: none;
  color: $gray5;
  font-weight: 700;
}
.title-size {
  font-size: 1rem;
}
</style>
