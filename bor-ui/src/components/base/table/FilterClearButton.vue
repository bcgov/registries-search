<template>
  <v-btn
    class="base-table__header__item__clear-btn"
    icon
    :style="{ right: right }"
  >
    <v-icon color="primary" size="20">
      mdi-close
    </v-icon>
  </v-btn>
</template>
<script setup lang="ts">
defineProps<{ right: string }>()
</script>
<style lang="scss" scoped>
.base-table__header__item__clear-btn {
  background-color: transparent;
  bottom: 37%;
  box-shadow: none;
  height: 25px;
  position: absolute;
  width: 25px;
}
</style>
