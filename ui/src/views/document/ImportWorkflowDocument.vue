<template>
  <div class="upload-document p-12-24">
    <div class="flex align-center mb-16">
      <back-button to="-1" style="margin-left: -4px"></back-button>
      <h3 style="display: inline-block">{{ $t('views.document.importDocument') }}</h3>
    </div>
    <el-card style="--el-card-padding: 0">
      <div class="upload-document__main flex" v-loading="loading">
        <div class="upload-document__component main-calc-height">
          <div class="upload-component p-24" style="min-width: 850px">
            <keep-alive>
              <component
                ref="ActionRef"
                :is="ak[active]"
                v-model:loading="loading"
                :workflow="_workflow"
                :knowledge_id="knowledgeId"
                :id="action_id"
              ></component>
            </keep-alive>
          </div>
        </div>
      </div>
    </el-card>
    <div class="upload-document__footer text-right border-t">
      <el-button :disabled="loading" @click="router.go(-1)">{{ $t('common.cancel') }}</el-button>
      <el-button
        v-if="base_form_list.length > 0 && active == 'knowledge_base'"
        :loading="loading"
        @click="up"
      >
        {{ $t('views.document.buttons.prev') }}</el-button
      >
      <el-button
        v-if="base_form_list.length > 0 && active == 'data_source'"
        :disabled="loading"
        @click="next"
      >
        {{ $t('views.document.buttons.next') }}
      </el-button>
      <el-button
        v-if="base_form_list.length > 0 ? active == 'knowledge_base' : true"
        @click="upload"
        type="primary"
        :disabled="loading"
      >
        {{ $t('views.document.buttons.import') }}
      </el-button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref, provide, type Ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import DataSource from '@/views/knowledge-workflow/component/action/DataSource.vue'
import Result from '@/views/knowledge-workflow/component/action/Result.vue'
import applicationApi from '@/api/application/application'
import KnowledgeBase from '@/views/knowledge-workflow/component/action/KnowledgeBase.vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api.ts'
import { WorkflowType } from '@/enums/application'
provide('upload', (file: any, loading?: Ref<boolean>) => {
  return applicationApi.postUploadFile(file, knowledgeId as string, 'KNOWLEDGE', loading)
})
const router = useRouter()
const route = useRoute()
const {
  params: { knowledgeId },
} = route
const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const ak = {
  data_source: DataSource,
  knowledge_base: KnowledgeBase,
  result: Result,
}

const loading = ref(false)
const ActionRef = ref()
const action_id = ref<string>()
const form_data = ref<any>({})
const active = ref<'data_source' | 'knowledge_base' | 'result'>('data_source')
const _workflow = ref<any>(null)

const base_form_list = computed(() => {
  const kBase = _workflow.value?.nodes?.find((n: any) => n.type === WorkflowType.KnowledgeBase)
  if (kBase) {
    return kBase.properties.user_input_field_list
  }
  return []
})
const next = () => {
  ActionRef.value.validate().then(() => {
    form_data.value[active.value] = ActionRef.value.get_data()
    active.value = 'knowledge_base'
  })
}
const up = () => {
  ActionRef.value.validate().then(() => {
    active.value = 'data_source'
  })
}
const upload = () => {
  ActionRef.value.validate().then(() => {
    form_data.value[active.value] = ActionRef.value.get_data()
    loadSharedApi({ type: 'knowledge', systemType: apiType.value })
      .workflowUpload(knowledgeId, form_data.value, loading)
      .then((ok: any) => {
        router.go(-1)
      })
  })
}
function getDetail() {
  loadSharedApi({ type: 'knowledge', systemType: apiType.value })
    .getKnowledgeDetail(knowledgeId, loading)
    .then((res: any) => {
      _workflow.value = res.data.work_flow
    })
}

onMounted(() => {
  getDetail()
})
</script>
<style lang="scss">
@use './index.scss';
</style>
