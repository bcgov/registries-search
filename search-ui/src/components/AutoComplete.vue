<template>
  <v-card v-if="showAutoComplete" class="auto-complete-card" elevation="5">
    <v-row class="pt-2 pb-2" no-gutters justify="center">
      <v-col no-gutters cols="11">
        <v-item-group v-model="autoCompleteSelected">
          <v-row
            v-for="(result, i) in autoCompleteResults"
            :key="i" class="pt-0 pb-0 pl-3">
            <v-col class="title-size">
              <v-item>
                <v-label class="auto-complete-item" @click="autoCompleteSelected = i">
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
import { computed, ref, watch } from 'vue'
import { getAutoComplete } from '@/requests'
import { SuggestionResponseI } from '@/interfaces' // eslint-disable-line no-unused-vars

const regex = /(<([^>]+)>)/ig 

const props = defineProps({
  setAutoCompleteIsActive: { default: false },   
  searchValue: { default: '' }
})

const emit = defineEmits(['hide-details', 'search-value'])

const autoCompleteIsActive = ref(props.setAutoCompleteIsActive)
const  autoCompleteResults = ref([])
const autoCompleteSelected = ref(-1)
const showAutoComplete =  computed((): boolean => {
  const value = autoCompleteResults.value?.length > 0 && autoCompleteIsActive.value
  emit('hide-details', value)
  return value
})


const updateAutoCompleteResults = async (searchValue: string) => {
  const response: SuggestionResponseI = await getAutoComplete(searchValue);
  // check if results are still relevant before updating list
  if (searchValue === props.searchValue && response?.results) {
    // will take up to 10 results
    autoCompleteResults.value = response?.results.slice(0, 10)
  }
  else if (response.error) {
    console.error('getDraft failed: ' + response.error.statusCode + ': ' + response.error.message)     
  }
}

watch(autoCompleteSelected, (val: number) => {
   if (val >= 0) {    
    const searchValue = autoCompleteResults.value[val]?.value
    autoCompleteIsActive.value = false
    emit('search-value', searchValue.replace(regex,""))
  }
})

watch(autoCompleteIsActive, (val: boolean) => {
  if (!val) autoCompleteResults.value = []
})
 

watch(
  () => props.setAutoCompleteIsActive,
  (val: boolean) => {autoCompleteIsActive.value = val}
)
    
watch(
  () => props.searchValue,
  (val: string) => {
    if (autoCompleteIsActive.value && val.trim().length >= 3) {
      updateAutoCompleteResults(val)
    }
  }
) 
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
.close-btn-row {
  height: 1rem;
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
  width: 35rem;
  color: $gray7 !important;
}
.auto-complete-row:hover {
  color: $primary-blue !important;
}

.title-size {
  font-size: 1rem;
}
</style>
