<template>
  <div class="flex self-center h-[32px] w-[32px] bg-blue-300">
    <p data-cy="al-avatar" class="m-auto self-center text-xl font-bold" :class="avatarClasses">
      {{ username.slice(0,1) }}
    </p>
  </div>
  <div class="ml-3 text-left">
    <p :class="accountName ? '' : 'mt-[6px]'" data-cy="al-username">
      {{ username }}
    </p>
    <p v-if="accountName" class="text-xs opacity-75" data-cy="al-account-name">
      {{ accountName }}
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps({
  avatarClasses: { default: '', type: String },
  accountName: { default: 'N/A', type: String },
  username: { default: 'N/A', type: String }
})

</script>

<style scoped>
</style>
