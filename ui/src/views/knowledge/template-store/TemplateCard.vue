<template>
  <CardBox :title="props.tool.name" :description="props.tool.desc" class="cursor tool-card">
    <template #icon>
      <el-avatar shape="square" :size="32" style="background: none">
        <img src="@/assets/knowledge/icon_basic_template.svg" alt="" />
      </el-avatar>
    </template>
    <template #title>
      <span :title="props.tool?.name" class="ellipsis"> {{ props.tool?.name }}</span>
    </template>
    <!-- <template #tag>
      <el-tag type="info" v-if="props.tool?.label === 'knowledge_template'" class="info-tag">
        {{ $t('知识库') }}
      </el-tag>
      <el-tag type="info" class="info-tag" v-else>
        {{ $t('views.tool.title') }}
      </el-tag>
    </template> -->
    <!-- <template #subTitle>
      <el-text class="color-secondary lighter" size="small">
        {{ getSubTitle(props.tool) }}
      </el-text>
    </template> -->
    <template #footer>
      <span class="card-footer-left color-secondary flex align-center" v-if="props.tool?.downloads != undefined">
        <AppIcon iconName="app-download" class="mr-4" />
        <span> {{ numberFormat(props.tool.downloads || 0) }} </span>
      </span>

      <div class="card-footer-operation mb-8" @click.stop>
        <el-button @click="emit('handleDetail')">
          {{ $t('common.detail') }}
        </el-button>
        <el-button type="primary" :loading="props.addLoading" @click="emit('handleAdd')">
          {{ $t('common.use') }}
        </el-button>
      </div>
    </template>
  </CardBox>
</template>

<script setup lang="ts">
import { isAppIcon, numberFormat, resetUrl } from '@/utils/common'

const props = defineProps<{
  tool: any
  getSubTitle: (v: any) => string
  addLoading: boolean
}>()

const emit = defineEmits<{
  (e: 'handleAdd'): void
  (e: 'handleDetail'): void
}>()
</script>

<style lang="scss" scoped>
.tool-card {
  :deep(.card-footer) {
    & > div:first-of-type {
      flex: 1;
    }

    .card-footer-operation {
      display: none;
    }
  }

  &:hover {
    .card-footer-left {
      display: none;
    }

    .card-footer-operation {
      display: flex !important;

      .el-button {
        flex: 1;
      }
    }
  }
}
</style>
