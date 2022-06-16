<template>
  <v-dialog v-model="dialogRef">
    <v-card>
      <v-card-title>Error</v-card-title>

      <v-card-text>
        <p class="font-15">An error occured while trying to complete the request.</p>

        
        <p class="font-15">If this error persists, please contact us.</p>
        <ContactInfo class="mt-5" />
        
      </v-card-text>

      <v-divider class="my-0"></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn id="dialog-close-button" color="primary" text @click="close()">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script  setup lang="ts"> 
import { ContactInfo } from '@/components'
import { toRef } from 'vue'
 
const props = defineProps<{   
    dialog: boolean,
    attach: string 
}>()

const dialogRef = toRef(props, 'dialog')

const emit = defineEmits(['close'])

const close = () => {
    emit('close')
 }
</script>
