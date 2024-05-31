<template>
  <div>
    <div v-if="icons" class="flex space-x-1" data-cy="control-icons-container">
      <div v-for="icon in icons" :key="icon.src">
        <UTooltip
          :text="icon.tooltip"
          :popper="{ placement: 'top' }"
          location="top"
        >
          <img :src="icon.src" :alt="icon.alt">
        </UTooltip>
      </div>
    </div>
    <BaseDetailsInfoBox v-if="shares" :title="shares.title" :content="shares.content" />
    <BaseDetailsInfoBox v-if="votes" :title="votes.title" :content="votes.content" />
  </div>
</template>

<script setup lang="ts">
import { convertDetailsToIcon, OtherControlIcon } from '@/utils'
import type { ControlColumnDetailsInfoBoxI, ControlColumnIconI } from '@/interfaces/person-search-table'

const localProps = defineProps<{ role: SearchResultRoleI }>()

const icons: Ref<ControlColumnIconI[]> = ref([])
const shares: Ref<ControlColumnDetailsInfoBoxI | null> = ref(null)
const votes: Ref<ControlColumnDetailsInfoBoxI | null> = ref(null)

// get icons if exist
if (localProps.role.relatedInterests) {
  for (const relatedInterest of localProps.role.relatedInterests) {
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

  const sharesInterest = localProps.role.relatedInterests.find(interest =>
    interest.interestType === 'shareholding' && interest.details.startsWith('controlType.sharesOrVotes.')
  )
  if (sharesInterest) {
    shares.value = {
      title: 'Shares',
      content: `At least ${sharesInterest.sharesMin || 0}%
      and up to ${sharesInterest.sharesMax || sharesInterest.sharesMin || 0}%`
    }
  }

  const votesInterest = localProps.role.relatedInterests.find(interest =>
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
