<template>
  <div>
    <div v-if="icons" class="detail-icons-container">
      <div v-for="icon in icons" :key="icon.src" class="detail-icon">
        <v-tooltip
          :text="icon.tooltip"
          location="top"
        >
          <template #activator="{ props }">
            <img v-bind="props" :src="icon.src" :alt="icon.alt">
          </template>
        </v-tooltip>
      </div>
    </div>
    <BaseDetailsInfoBox v-if="shares" :title="shares.title" :content="shares.content" />
    <BaseDetailsInfoBox v-if="votes" :title="votes.title" :content="votes.content" />
  </div>
</template>

<script setup lang="ts">
import { convertDetailsToIcon, OtherControlIcon } from '@/utils'
import type { ControlColumnDetailsInfoBoxI, ControlColumnIconI } from '@/interfaces/person-search-table'

const localProps = defineProps<{ item: SearchResultI }>()

const icons: Ref<ControlColumnIconI[]> = ref([])
const shares: Ref<ControlColumnDetailsInfoBoxI | null> = ref(null)
const votes: Ref<ControlColumnDetailsInfoBoxI | null> = ref(null)

for (const role of localProps.item.roles) {
  if (!role.relatedInterests) {
    continue
  }
  // get icons if exist
  for (const relatedInterest of role.relatedInterests) {
    // console.log(icons)
    if (relatedInterest.interestType === 'otherInfluenceOrControl') {
      icons.value.push(OtherControlIcon)
      continue
    }
    const icon = convertDetailsToIcon(relatedInterest.details)
    if (icon && icons.value.findIndex(ic => ic.src === icon.src) === -1) {
      icons.value.push(icon)
    }
  }

  const sharesInterest = role.relatedInterests.find(interest =>
    interest.interestType === 'shareholding' && interest.details.startsWith('controlType.sharesOrVotes.')
  )
  if (sharesInterest) {
    shares.value = {
      title: 'Shares',
      content: `At least ${sharesInterest.sharesMin || 0}%
      and up to ${sharesInterest.sharesMax || sharesInterest.sharesMin || 0}%`
    }
  }

  const votesInterest = role.relatedInterests.find(interest =>
    interest.interestType === 'votingRights' && interest.details.startsWith('controlType.sharesOrVotes.')
  )
  if (votesInterest) {
    votes.value = {
      title: 'Votes',
      content: `At least ${votesInterest.sharesMin || 0}%
      and up to ${votesInterest.sharesMax || votesInterest.sharesMin || 0}%`
    }
  }
}

</script>

<style lang="scss" scoped>
.detail-icons-container {
  display: flex;
  flex-flow: wrap;
}

.detail-icon {
  padding: 1px;
}
</style>
