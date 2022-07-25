<template>
    <v-form id="folio-number-form" ref="folioForm" v-model="folioFormValid">
      <v-text-field
        filled
        id="folio-number-textfield"
        label="Folio Number (Optional)"
        v-model="folio"
        :rules="folioNumberRules"
        :disabled="disabled"
        @focus="emit('focus', true)"
        autocomplete="chrome-off"
        :name="Math.random().toString()"
      />
    </v-form>
</template>

<script setup lang="ts">
import { ref, watch, Ref, nextTick } from 'vue'
import { FormIF } from '@bcrs-shared-components/interfaces'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  validate: { type: Boolean, default: true }
})

const emit = defineEmits<{
  (e: 'focus', value: boolean): void
  (e: 'emitFolioNumber', value: string): void
  (e: 'valid', value: boolean): void
}>()


const folioForm: Ref<FormIF> = ref(null)
const folio = ref('')

/** Folio form model property. */
const folioFormValid = ref(false)

/** Validation rules for Folio Number. */
const folioNumberRules: Array<(v: string) => string | true> = [
  v => (!v || !props.validate || v.length <= 50) || 'Cannot exceed 50 characters' // maximum character count
]

const resetFolioNumber = (): void => folioForm.value.reset()
const resetFolioNumberValidation = (): void => folioForm.value.resetValidation()
const validateFolioNumber = (): boolean => folioForm.value.validate()

defineExpose({ resetFolioNumber, resetFolioNumberValidation, validateFolioNumber })

/** Prompt the field validations. */
watch([() => folioFormValid.value, () => props.validate], async () => {
  await nextTick()
  if (props.validate) {
    folioForm.value.validate()
    emit('valid', validateFolioNumber())
  }
})
watch(() => folio.value, (val) => emit('emitFolioNumber', val))
</script>
