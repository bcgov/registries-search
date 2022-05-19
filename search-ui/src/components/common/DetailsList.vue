<template>
    <div class="details-list">
        <!-- the detail comments list-->
        <v-list class="pb-0">
            <v-list-item class="pl-0 pr-0 detail-body" v-for="(comment, index) in props.filing.comments" :key="index">
                <v-list-item-content>
                    <v-list-item-title class="body-2">
                        <strong v-if="!isRoleStaff">BC Registries Staff</strong>
                        <strong v-else>{{ comment.submitterDisplayName || 'N/A' }}</strong>
                        ({{ apiToPacificDateTime(comment.timestamp) }})
                    </v-list-item-title>
                    <v-list-item-subtitle class="body-2">
                        <div class="pre-line">{{ comment.comment }}</div>
                    </v-list-item-subtitle>
                </v-list-item-content>
            </v-list-item>
        </v-list>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStore } from 'vuex'
import { apiToPacificDateTime } from '@/utils'

const store = useStore()

const props = defineProps({
    filing: {
        default: {
            comments: [],
            filingId: null
        }
    }
})

const isRoleStaff = computed(() => store.getters['isRoleStaff'] as boolean)

</script>

<style lang="scss" scoped>
.title-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
