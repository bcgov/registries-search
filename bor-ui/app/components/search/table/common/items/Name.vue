<script setup lang="ts">
type NameInfoT = {
  legalName: string
  alternateName?: string
  birthDate?: string
}
const prop = defineProps<{ icon?: string, item: NameInfoT }>()
const { highlightMatch } = useSearchStore()

const legalName = highlightMatch(prop.item.legalName.toUpperCase())
</script>

<template>
  <div class="flex space-x-2">
    <div>
      <UIcon
        v-if="icon"
        class="text-xl"
        :name="icon"
      />
    </div>
    <div class="flex flex-col">
      <!-- eslint-disable-next-line vue/no-v-html ; Controlled variable on the backend -->
      <span class="break-all" v-html="legalName" />
      <DetailsInfoBox
        v-if="item.alternateName"
        class="info-section"
        :title="$t('label.preferredName')"
        :content="item.alternateName"
      />
      <DetailsInfoBox
        v-if="item.birthDate"
        class="info-section"
        :title="$t('label.born')"
        :content="item.birthDate"
      />
    </div>
  </div>
</template>

<style scoped>
.info-section {
  margin-top: 10px;
}

.birthdate {
  font-size: smaller;
}
</style>
