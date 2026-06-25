<template>
  <div class="space-y-6">

    <!-- HEADER -->
    <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
      <div class="flex items-center justify-between flex-wrap gap-4">
        <div class="flex items-center gap-3">
          <span class="relative flex h-3 w-3">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
          </span>
          <div>
            <h2 class="text-2xl font-bold text-white">Ao Vivo</h2>
            <p class="text-slate-400 text-sm">
              {{ fixtures.length ? `${fixtures.length} partida(s) em andamento` : 'Nenhuma partida ao vivo agora' }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="lastUpdated" class="text-slate-500 text-xs">
            Atualizado: {{ lastUpdated }}
          </span>
          <button
            @click="toggle"
            :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition', autoRefresh ? 'bg-emerald-700 hover:bg-emerald-600 text-white' : 'bg-slate-700 hover:bg-slate-600 text-slate-300']"
          >
            {{ autoRefresh ? '⏸ Pausar' : '▶ Retomar' }}
          </button>
          <button
            @click="loadLive"
            :disabled="loading"
            class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition"
          >
            <span v-if="loading" class="animate-spin inline-block">⏳</span>
            <span v-else>🔄</span>
          </button>
        </div>
      </div>
    </div>

    <!-- ERRO -->
    <div v-if="error" class="bg-red-900/20 border border-red-700 text-red-400 px-4 py-3 rounded-lg">
      ❌ {{ error }}
    </div>

    <!-- EMPTY STATE -->
    <div v-if="!loading && !fixtures.length && !error" class="bg-slate-800 rounded-xl border border-dashed border-slate-600 p-16 text-center">
      <div class="text-5xl mb-4">📺</div>
      <p class="text-slate-300 text-lg font-medium">Nenhuma partida ao vivo no momento</p>
      <p class="text-slate-500 mt-2 text-sm">
        A aba será atualizada automaticamente a cada 30 segundos quando matches começarem.
      </p>
    </div>

    <!-- LIVE FIXTURES GRID -->
    <div v-if="fixtures.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="f in fixtures"
        :key="f.id"
        class="bg-slate-800 rounded-xl border border-slate-700 p-5 hover:border-slate-600 transition"
      >
        <!-- Liga + Minuto -->
        <div class="flex items-center justify-between mb-4">
          <span class="text-slate-400 text-xs truncate max-w-[60%]">{{ f.league }}</span>
          <span :class="['px-2 py-0.5 rounded text-xs font-bold flex items-center gap-1', statusCls(f.status)]">
            <span v-if="isLive(f.status)" class="relative flex h-1.5 w-1.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75"></span>
              <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-current"></span>
            </span>
            {{ formatStatus(f) }}
          </span>
        </div>

        <!-- Times + Placar -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 min-w-0">
              <img v-if="f.home.logo" :src="f.home.logo" class="w-6 h-6 object-contain flex-shrink-0" />
              <span class="text-white font-semibold text-sm truncate">{{ f.home.name }}</span>
            </div>
            <span class="text-white font-bold text-xl w-6 text-center flex-shrink-0">
              {{ f.goals.home ?? '-' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 min-w-0">
              <img v-if="f.away.logo" :src="f.away.logo" class="w-6 h-6 object-contain flex-shrink-0" />
              <span class="text-white font-semibold text-sm truncate">{{ f.away.name }}</span>
            </div>
            <span class="text-white font-bold text-xl w-6 text-center flex-shrink-0">
              {{ f.goals.away ?? '-' }}
            </span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

const API_URL = 'http://localhost:3001'

export default {
  name: 'LiveTab',
  setup() {
    const fixtures    = ref([])
    const loading     = ref(false)
    const error       = ref('')
    const lastUpdated = ref('')
    const autoRefresh = ref(true)
    let intervalId    = null

    async function loadLive() {
      error.value   = ''
      loading.value = true
      try {
        const r = await fetch(`${API_URL}/fixtures/live`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const data = await r.json()
        fixtures.value    = data.fixtures || []
        lastUpdated.value = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      } catch (e) {
        error.value = `Erro ao buscar partidas: ${e.message}`
      } finally {
        loading.value = false
      }
    }

    function startInterval() {
      if (intervalId) return
      intervalId = setInterval(loadLive, 30_000)
    }

    function stopInterval() {
      if (intervalId) { clearInterval(intervalId); intervalId = null }
    }

    function toggle() {
      autoRefresh.value = !autoRefresh.value
      autoRefresh.value ? startInterval() : stopInterval()
    }

    function isLive(status) {
      return ['1H', '2H', 'ET', 'BT', 'P'].includes(status)
    }

    function statusCls(status) {
      if (isLive(status))   return 'bg-emerald-900/50 text-emerald-400 border border-emerald-700'
      if (status === 'HT')  return 'bg-yellow-900/50 text-yellow-400 border border-yellow-700'
      return 'bg-slate-700 text-slate-400'
    }

    function formatStatus(f) {
      if (f.status === 'HT')  return 'Intervalo'
      if (f.elapsed != null)  return `${f.elapsed}'`
      return f.status_long || f.status || '—'
    }

    onMounted(() => {
      loadLive()
      startInterval()
    })

    onUnmounted(() => stopInterval())

    return {
      fixtures, loading, error, lastUpdated, autoRefresh,
      loadLive, toggle, isLive, statusCls, formatStatus,
    }
  }
}
</script>
