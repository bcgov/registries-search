
<template>
  <v-row no-gutters>
    <v-col cols="auto">
      <v-icon class="search-table__icon-name">{{ icon }}</v-icon>
    </v-col>
    <v-col class="ml-2">
      <span v-html="name" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{ icon: string, name: string }>()

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.search-table {
  border: solid 1px $gray2;

  &__action-btn {
    height: 36px;
    margin-top: -9px;
    width: 90%;
  }

  &__action-div {
    height: 36px;
    margin: auto;
    // NB: need magin/padding combo otherwise xtra space below
    margin-top: -10px;
    padding-top: 6px;
    position: relative;
    width: 24px;
  }

  &__icon-name {
    margin-top: -7px;
    color: $gray9;
  }
}
.table-tooltip-arrow {
  left: 2px;
  margin-top: -10px !important;
}
</style>
  