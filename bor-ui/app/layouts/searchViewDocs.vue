<template>
  <ConnectLayout>
    <template #header>
      <ConnectHeaderAuth />
    </template>
    <template #bottomHeaders>
      <ConnectTombstone />
    </template>
    <slot />
  </ConnectLayout>
</template>
