<template>
  <div id="wecom-qr" class="wecom-qr flex"></div>
</template>

<script lang="ts" setup>
import {nextTick, defineProps, onBeforeUnmount} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {getBrowserLang} from '@/locales'
import useStore from '@/stores'
const WE_COM_ORIGIN = 'https://login.work.weixin.qq.com'
const LOGIN_SUCCESS_EVENT = 'onLoginSuccess'
const LOGIN_STATE = 'fit2cloud-wecom-qr'
const props = defineProps<{
  config: {
    app_secret: string
    app_key: string
    corp_id?: string
    agent_id?: string
    callback_url: string
  }
}>()

const router = useRouter()
const route = useRoute()
const {chatUser} = useStore()

const {
  params: {accessToken},
} = route as any

let iframe: HTMLIFrameElement | null = null

function createTransparentIFrame(el: string) {
  const container = document.querySelector(el)
  if (!container) return null

  const iframeEl = document.createElement('iframe')
  iframeEl.style.cssText = `
    display: block;
    border: none;
    background: transparent;
  `
  iframeEl.referrerPolicy = 'origin'
  iframeEl.setAttribute('frameborder', '0')
  iframeEl.setAttribute('allowtransparency', 'true')

  container.appendChild(iframeEl)
  return iframeEl
}

function getLang() {
  const lang = localStorage.getItem('MaxKB-locale') || getBrowserLang()
  return lang === 'en-US' ? 'en' : 'zh'
}

function safeParse(data: unknown) {
  try {
    return typeof data === 'string' ? JSON.parse(data) : data
  } catch {
    return null
  }
}

async function handleLoginSuccess(code: string) {
  await chatUser.wecomCallback(code, accessToken)

  router.push({
    name: 'chat',
    params: {accessToken},
    query: route.query,
  })
}

function handleWindowMessage(event: MessageEvent) {
  if (event.origin !== WE_COM_ORIGIN) return

  const payload: any = safeParse(event.data)
  if (!payload?.args) return

  if (payload.args.name === LOGIN_SUCCESS_EVENT) {
    const code = payload.args?.data?.code
    if (!code) return

    handleLoginSuccess(code)
    cleanup()
  }
}

function cleanup() {
  window.removeEventListener('message', handleWindowMessage)
  iframe?.remove()
  iframe = null
}

const init = async () => {
  await nextTick()

  iframe = createTransparentIFrame('#wecom-qr')
  if (!iframe) return

  const redirectUri = encodeURIComponent(props.config.callback_url)

  iframe.src =
    `${WE_COM_ORIGIN}/wwlogin/sso/login` +
    `?login_type=CorpApp` +
    `&appid=${props.config.corp_id}` +
    `&agentid=${props.config.agent_id}` +
    `&redirect_uri=${redirectUri}` +
    `&state=${LOGIN_STATE}` +
    `&lang=${getLang()}` +
    `&panel_size=small` +
    `&redirect_type=callback`

  window.addEventListener('message', handleWindowMessage)
}

onBeforeUnmount(cleanup)

init()
</script>

<style scoped lang="scss">
#wecom-qr {
  margin-top: -20px;
  height: 360px;
  justify-content: center;
}
</style>
