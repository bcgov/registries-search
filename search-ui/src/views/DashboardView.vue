<template>
  <v-container id="dashboard" class="container" fluid>
    <div>
      <v-row no-gutters>
        <v-col>
          <span class="page-header"><h1>Business Search</h1><span class="beta-version pl-2">BETA</span></span>
        </v-col>
      </v-row>
    </div>

    <v-tabs class="mt-8" v-model="tab">
      <v-tab class="tab-item-default" v-bind:class="[tab == '0' ? 'tab-item-active' : 'tab-item-inactive']">
        <v-icon>mdi-magnify</v-icon>
        <span class="ml-1">Find a Business</span>
      </v-tab>
      <v-tab class="tab-item-default" v-bind:class="[tab == '1' ? 'tab-item-active' : 'tab-item-inactive']">
        <v-icon>mdi-file-document-edit-outline</v-icon>
        <span class="ml-1">View Recently Purchased Documents ({{totalResultsLength}})</span>
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
import { watch } from 'vue'
import { PurchaseHistoryView, SearchView } from '@/views'
import { useDocumentAccessRequest } from '@/composables'
import { ref, computed } from 'vue'

const props = defineProps({ appReady: { type: Boolean } })

const tab = ref('')

const { documentAccessRequest, loadAccessRequestHistory } = useDocumentAccessRequest()

const totalResultsLength = computed(() => documentAccessRequest.requests?.length || 0)

watch(() => props.appReady, (ready: boolean) => {
  if (ready) {
    loadAccessRequestHistory()
  }
})


</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.tab-item-inactive {  
  color: white;
  background-color: #003366;
}

.tab-item-active {  
  color: #495057;
  background-color: white;
}

.tab-item-default {
  width: 50%;
  min-width: 50%;
  font-weight: bold;
}

.v-list-item {
    padding-left: 0;    
}

.beta-version{
  line-height:10px;
  text-decoration: underline;
  font-weight: bold;
  color: $BCgovBlue4;
  font-size: 0.9rem
}

.page-header{
  display: flex;  
}
</style>