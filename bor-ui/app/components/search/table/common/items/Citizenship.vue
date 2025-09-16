<script setup lang="ts">
import { getName } from 'country-list'

const prop = defineProps<{ item: SearchResult }>()
const countries = prop.item.nationalities ?? []
</script>

<template>
  <div class="w-2/3 mr-2" :class="countries.length === 1 ? 'flex justify-center' : 'grid gap-x-1 grid-cols-2'">
    <UTooltip
      v-for="code in countries"
      :key="code"
      arrow
      :content="{
        align: 'center',
        side: 'top',
      }"
      :delay-duration="0"
      :text="getName(code) || code"
    >
      <CountryFlag
        :country="code"
        size="normal"
        style="margin-top: -5px"
        :data-testid="'country-flag-' + code"
      />
    </UTooltip>
  </div>
</template>
