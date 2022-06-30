<template>
  <v-container id="dashboard" class="container" fluid>
    <div>
      <v-row no-gutters>
        <v-col>
          <h1>Business Search</h1>
        </v-col>
      </v-row>
    </div>

    <v-tabs class="mt-8" v-model="tab" background-color="transparent">
      <v-tab class="tab-item-style">
        <v-icon>mdi-magnify</v-icon>
        <span class="ml-1">Find a Business</span>
      </v-tab>
      <v-tab class="tab-item-style">
        <v-icon>mdi-file-document-edit-outline</v-icon>
        <span class="ml-1">View Recently Purchased Documents</span>
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item>
        <v-card flat>
          <v-card-text>
            <SearchView />
          </v-card-text>
        </v-card>
      </v-window-item>
      <v-window-item>
        <v-card flat>
          <v-card-text>
            <PurchaseHistoryView />
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>
  </v-container>
</template>


<script setup lang="ts">
// local
import { PurchaseHistoryView, SearchView } from '@/views'
import { ref } from 'vue'

const tab = ref('')

</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.tab-item-style {
  width: 50%;
  min-width: 50%;
  font-weight: bold;
}
</style>