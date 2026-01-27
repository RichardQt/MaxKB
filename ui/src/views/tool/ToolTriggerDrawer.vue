<template>
  <el-drawer v-model="visible" size="600">
    <template #header>
      <h4>{{ $t('views.trigger.title') }}</h4>
    </template>
    <div class="flex-between">
      <h4 class="title-decoration-1 mb-16 mt-16">
        {{ $t('views.trigger.title') }}
      </h4>
      <el-button link type="primary" @click="openCreateTriggerDrawer()">
        <AppIcon iconName="app-add-outlined" class="mr-4"></AppIcon>
        {{ $t('common.add') }}
      </el-button>
    </div>

    <div v-if="triggerList.length > 0" class="w-full" v-loading="loading">
      <template v-for="(item, index) in triggerList" :key="index">
        <div class="flex-between border border-r-6 white-bg mb-8" style="padding: 2px 8px">
          <div class="flex align-center">
            <TriggerIcon :type="item.trigger_type" class="mr-8" :size="20" />
            <span class="ellipsis-1"> {{ item.name }}</span>
          </div>
          <div>
            <span class="mr-4">
              <el-button text @click="openEditTriggerDrawer(item)">
                <AppIcon iconName="app-edit" class="color-secondary"></AppIcon>
              </el-button>
            </span>

            <el-button text @click="removeTrigger(item)">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
    </div>
    <el-empty v-else :description="$t('common.noData')" />

    <TriggerDrawer
      @refresh="refreshTrigger"
      ref="triggerDrawerRef"
      :create-trigger="createTrigger"
      :edit-trigger="editTrigger"
      resourceType="TOOL"
    ></TriggerDrawer>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import permissionMap from '@/permission'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import TriggerDrawer from '@/views/trigger/component/TriggerDrawer.vue'
import triggerAPI from '@/api/trigger/trigger'
const route = useRoute()

const apiType = computed(() => {
  if (route.path.includes('shared')) {
    return 'systemShare'
  } else if (route.path.includes('resource-management')) {
    return 'systemManage'
  } else {
    return 'workspace'
  }
})

const permissionPrecise = computed(() => {
  return permissionMap['tool'][apiType.value]
})

const toolId = ref<string>('')
const visible = ref<boolean>(false)
const loading = ref<boolean>(false)

const emit = defineEmits(['refresh'])

const createTrigger = (trigger: any) => {
  if (toolId.value) {
    return triggerAPI.postResourceTrigger('TOOL', toolId.value, trigger)
  }
  return Promise.resolve<any>({})
}
const editTrigger = (trigger_id: string, trigger: any) => {
  if (toolId.value) {
    return triggerAPI.putResourceTrigger('TOOL', toolId.value, trigger_id, trigger)
  }
  return Promise.resolve<any>({})
}
const triggerList = ref<Array<any>>([])

const triggerDrawerRef = ref<InstanceType<typeof TriggerDrawer>>()

const openCreateTriggerDrawer = () => {
  triggerDrawerRef.value?.open(undefined, 'TOOL', toolId.value)
}
const openEditTriggerDrawer = (trigger: any) => {
  triggerDrawerRef.value?.open(trigger.id)
}

function getTriggerList() {
  loadSharedApi({ type: 'trigger', systemType: apiType.value })
    .getResourceTriggerList('APPLICATION', toolId.value, loading)
    .then((res: any) => {
      triggerList.value = res.data
    })
}

function refreshTrigger() {
  getTriggerList()
}

function removeTrigger(trigger: any) {
  loadSharedApi({ type: 'trigger', systemType: apiType.value })
    .deleteResourceTrigger('APPLICATION', toolId.value, trigger.id, loading)
    .then((res: any) => {
      getTriggerList()
    })
}

const open = (data: any) => {
  toolId.value = data.id
  getTriggerList()
  visible.value = true
}

defineExpose({
  open,
})
</script>
<style lang="scss" scoped></style>
