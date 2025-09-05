<script setup lang="ts">
const prop = defineProps<{ role: SearchResultRole }>()

const getEffectiveDates = (role: SearchResultRole) => {
  const effectiveDates = []

  for (const startEndDates of role.roleDates) {
    const start = startEndDates.start ? toDateStr(new Date(startEndDates.start)) : undefined
    const end = startEndDates.end ? toDateStr(new Date(startEndDates.end)) : undefined
    let dateRange = ''
    if (role.roleType === SearchRoleType.INCORPORATOR) {
      dateRange += start
    } else {
      dateRange += `${start || 'Unknown'} To ${end || 'Current'}`
    }

    effectiveDates.push({ start, dateRange })
  }

  // sort effectiveDates by start date
  effectiveDates.sort((a, b) => b.start.localeCompare(a.start))
  return effectiveDates
}

const effectiveDates = ref(getEffectiveDates(prop.role))
</script>

<template>
  <div class="dates pr-2">
    <div
      v-for="(effectiveDate, index) in effectiveDates"
      :key="index"
      class="text-right"
    >
      {{ effectiveDate.dateRange }}
    </div>
  </div>
</template>

<style scoped>
.dates > div:not(:first-child) {
  margin-top: 8px;
}
</style>
