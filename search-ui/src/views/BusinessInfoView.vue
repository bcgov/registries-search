<template>
  <v-container id="business-info" class="container" fluid>
    <v-row no-gutters>
      <v-col cols="9">
        <h2>How to Access Business Documents</h2>
        <p class="pt-3">1. Select from Available Documents to Download.</p>
        <p class="pt-1">2. Pay the appropriate fee.</p>
        <p class="pt-1">3. Download the individual files you require.</p>
        <p class="pt-3">
          Note: some documents are available on paper only and not available 
          to download. To request copies of paper documents, contact BC Registries Staff.
        </p>
        <v-divider class="my-10" />
        <h2>Available Documents to Download:</h2>
        <v-divider class="my-10" />
      </v-col>
      <v-col cols="3">
        <!-- pay summary to go here -->
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">

// const props = defineProps({
//   identifier: { type: String }  // passed with param value in route.push
// })
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.v-divider {
  border-width: 1px;
}
</style>