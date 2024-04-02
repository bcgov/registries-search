<template>
  <div class="dates">
    <div v-for="(effectiveDate, index) in effectiveDates" :key="index">
      {{ effectiveDate.dateRange }}
    </div>
  </div>
</template>

<script setup lang="ts">
const prop = defineProps<{ item: SearchResultI }>()

const getEffectiveDates = (item: SearchResultI) => {
  const effectiveDates = []
  if (item.roles && item.roles.length > 0) {
    // only 1 role per item for now
    const roleType = item.roles[0].roleType

    for (const i in item.roles[0].roleDates) {
      const start = toDateStr(item.roles[0].roleDates[i].start)
      const end = toDateStr(item.roles[0].roleDates[i].end as Date)
      let dateRange = ''
      if (roleType === RoleTypeE.INCORPORATOR) {
        dateRange += start
      } else {
        dateRange += `${start || 'Unknown'} To ${end || 'Current'}`
      }

      effectiveDates.push({ start, dateRange })
    }
  }

  // sort effectiveDates by start date
  effectiveDates.sort((a, b) => b.start.getTime() - a.start.getTime())
  return effectiveDates
}

const effectiveDates = ref(getEffectiveDates(prop.item))
</script>

<style lang="scss" scoped>
.dates > div:not(:first-child) {
  margin-top: 8px;
}
</style>
