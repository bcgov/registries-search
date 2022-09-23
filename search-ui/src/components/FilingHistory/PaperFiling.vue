<template>
    <div class="paper-filing-details body-2">
        <p>
            This filing is available on paper only. To request copies of paper documents,
            contact BC Registries staff:
        </p>

        <ContactInfo class="mt-4" :contacts="RegistriesInfo" />
    </div>
</template>

<script setup lang="ts">
import { ContactInfo } from '@/components'
import { RegistriesInfo } from '@/resources/contact-info'
</script>

<style lang="scss" scoped>
p {
    margin-top: 1rem !important;
}
</style>
