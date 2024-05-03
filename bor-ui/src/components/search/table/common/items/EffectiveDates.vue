<template>
  <div class="dates pr-2">
    <div v-for="(effectiveDate, index) in effectiveDates" :key="index" class="text-right">
      {{ effectiveDate.dateRange }}
    </div>
  </div>
</template>

<script setup lang="ts">
const prop = defineProps<{ role: SearchResultRoleI }>()

const getEffectiveDates = (role: SearchResultRoleI) => {
  const effectiveDates = []

  for (const i in role.roleDates) {
    const start = toDateStr(role.roleDates[i].start)
    const end = toDateStr(role.roleDates[i].end as Date)
    let dateRange = ''
    if (role.roleType === RoleTypeE.INCORPORATOR) {
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

<style lang="scss" scoped>
.dates > div:not(:first-child) {
  margin-top: 8px;
}
</style>
