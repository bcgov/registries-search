<template>
  <div class="w-2/3 mr-2" :class="countries.length === 1 ? 'flex justify-center' : 'grid gap-x-1 grid-cols-2'">
    <CountryFlag
      v-for="code in countries"
      :key="code"
      :country="code"
      size="normal"
      style="margin-top: -5px"
    />
  </div>
</template>

<script setup lang="ts">
const prop = defineProps<{ item: SearchResultI }>()
const countries = prop.item.nationalities ?? []
</script>
