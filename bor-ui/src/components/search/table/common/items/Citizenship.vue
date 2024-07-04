<template>
  <div class="w-2/3 mr-2" :class="countries.length === 1 ? 'flex justify-center' : 'grid gap-x-1 grid-cols-2'">
    <UTooltip
      v-for="code in countries"
      :key="code"
      :text="getName(code) || code"
      :popper="{ arrow: true, placement: 'top' }"
    >
      <CountryFlag
        :country="code"
        size="normal"
        style="margin-top: -5px"
      />
    </UTooltip>
  </div>
</template>

<script setup lang="ts">
import { getName } from 'country-list'

const prop = defineProps<{ item: SearchResultI }>()
const countries = prop.item.nationalities ?? []
</script>
