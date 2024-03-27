<template>
  <v-btn
    v-if="showBtn"
    class="btn-basic action-btn"
    color="primary"
    large
    :ripple="false"
    @click="emit('action', true)"
  >
    Open
  </v-btn>
  <v-tooltip v-else location="top" transition="fade-transition">
    <template #activator="{ isActive, props }">
      <div class="action-div">
        <v-fade-transition>
          <div v-if="isActive" class="table-tooltip-arrow" />
        </v-fade-transition>
        <v-icon color="primary" size="24" v-bind="props">
          mdi-information-outline
        </v-icon>
      </div>
    </template>
    <span>{{ tooltipMsg }}</span>
  </v-tooltip>
</template>

<script setup lang="ts">
defineProps<{ showBtn: boolean, tooltipMsg?: string }>()
const emit = defineEmits<{(e: 'action', value: boolean): void }>()

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';
.action-btn {
  height: 36px;
  margin-top: 16px;
  min-width: 108px;
  width: 100%;
}

.action-div {
  height: 36px;
  margin: auto;
  // NB: need magin/padding combo otherwise xtra space below
  margin-top: -10px;
  padding-top: 6px;
  position: relative;
  width: 24px;
}

.table-tooltip-arrow {
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 9px solid RGBA(73, 80, 87);
  left: 2px;
  margin-top: -10px !important;
  position: absolute;
  width: 20px;
}
</style>
