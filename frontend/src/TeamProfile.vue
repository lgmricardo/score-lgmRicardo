<template>
  <!-- Dark overlay -->
  <div class="fixed inset-0 z-50 flex">
    <div class="flex-1 bg-black/50" @click="$emit('close')"></div>

    <!-- Slide-over panel -->
    <div class="w-full max-w-md bg-slate-900 border-l border-slate-700 flex flex-col h-full overflow-hidden shadow-2xl">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-slate-700 flex-shrink-0">
        <div class="flex items-center gap-3 min-w-0">
          <div>
            <h2 class="text-lg font-bold text-white truncate">{{ team.team?.name || team.name }}</h2>
            <p class="text-slate-400 text-sm">Temporada {{ season }}</p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="text-slate-400 hover:text-white text-2xl leading-none flex-shrink-0 ml-2"
        >×</button>
      </div>

      <!-- Scrollable content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- Resumo da temporada -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-4">
          <h3 class="text-white font-semibold mb-3 text-sm uppercase tracking-wider text-slate-400">Temporada Atual</h3>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div>
              <p class="text-2xl font-bold text-white">{{ team.rank }}º</p>
              <p class="text-slate-400 text-xs mt-1">Posição</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-blue-400">{{ team.points }}</p>
              <p class="text-slate-400 text-xs mt-1">Pontos</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-white">{{ team.all?.played }}</p>
              <p class="text-slate-400 text-xs mt-1">Jogos</p>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-2 text-center mt-3 pt-3 border-t border-slate-700">
            <div>
              <p class="text-lg font-semibold text-emerald-400">{{ team.all?.win }}</p>
              <p class="text-slate-400 text-xs">V</p>
            </div>
            <div>
              <p class="text-lg font-semibold text-yellow-400">{{ team.all?.draw }}</p>
              <p class="text-slate-400 text-xs">E</p>
            </div>
            <div>
              <p class="text-lg font-semibold text-red-400">{{ team.all?.lose }}</p>
              <p class="text-slate-400 text-xs">D</p>
            </div>
            <div>
              <p class="text-lg font-semibold text-white">{{ team.goalsDiff > 0 ? '+' : '' }}{{ team.goalsDiff }}</p>
              <p class="text-slate-400 text-xs">SG</p>
            </div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="text-center py-8 text-slate-400">
          <span class="animate-spin text-2xl">⏳</span>
          <p class="mt-2 text-sm">Carregando histórico...</p>
        </div>

        <template v-else-if="profileData">

          <!-- Forma (últimas 5) -->
          <div v-if="recentForm.length" class="bg-slate-800 rounded-xl border border-slate-700 p-4">
            <h3 class="text-white font-semibold mb-3 text-sm">Forma Recente</h3>
            <div class="flex gap-2">
              <span
                v-for="(r, i) in recentForm"
                :key="i"
                :class="['w-8 h-8 rounded flex items-center justify-center text-sm font-bold', formCls(r)]"
              >{{ r }}</span>
            </div>
          </div>

          <!-- Últimas partidas -->
          <div v-if="profileData.recent?.length" class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div class="px-4 py-3 border-b border-slate-700">
              <h3 class="text-white font-semibold text-sm">Últimas Partidas</h3>
            </div>
            <div class="divide-y divide-slate-700/50">
              <div
                v-for="(m, i) in profileData.recent"
                :key="i"
                class="px-4 py-2.5 flex items-center gap-3 text-sm"
              >
                <span :class="['w-5 h-5 rounded text-xs font-bold flex items-center justify-center flex-shrink-0', formCls(m.result)]">
                  {{ m.result }}
                </span>
                <span class="text-slate-400 text-xs w-10 flex-shrink-0">{{ m.is_home ? 'Casa' : 'Fora' }}</span>
                <span class="text-white flex-1 truncate">{{ m.opponent }}</span>
                <span class="font-bold text-white flex-shrink-0">{{ m.goals_for }}–{{ m.goals_against }}</span>
                <span class="text-slate-500 text-xs flex-shrink-0">{{ formatDate(m.date) }}</span>
              </div>
            </div>
          </div>

          <!-- Próximas partidas -->
          <div v-if="profileData.upcoming?.length" class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div class="px-4 py-3 border-b border-slate-700">
              <h3 class="text-white font-semibold text-sm">Próximas Partidas</h3>
            </div>
            <div class="divide-y divide-slate-700/50">
              <div
                v-for="(m, i) in profileData.upcoming"
                :key="i"
                class="px-4 py-2.5 flex items-center gap-3 text-sm"
              >
                <span class="text-slate-500 text-xs flex-shrink-0 w-16">{{ formatDate(m.date) }}</span>
                <span class="text-slate-400 text-xs w-10 flex-shrink-0">{{ m.is_home ? 'Casa' : 'Fora' }}</span>
                <span class="text-white flex-1 truncate">{{ m.opponent }}</span>
                <span class="text-slate-400 text-xs flex-shrink-0 truncate max-w-[100px]">{{ m.league }}</span>
              </div>
            </div>
          </div>

          <div v-if="!profileData.recent?.length && !profileData.upcoming?.length" class="text-center py-6 text-slate-400 text-sm">
            Sem histórico de partidas disponível para esta temporada.
          </div>

        </template>

        <!-- Erro -->
        <div v-if="fetchError" class="bg-red-900/20 border border-red-700 text-red-400 px-4 py-3 rounded-lg text-sm">
          ❌ {{ fetchError }}
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

const API_URL = 'http://localhost:3001'

export default {
  name: 'TeamProfile',
  props: {
    team:   { type: Object, required: true },
    season: { type: String, required: true },
  },
  emits: ['close'],

  setup(props) {
    const profileData = ref(null)
    const loading     = ref(false)
    const fetchError  = ref('')

    const recentForm = computed(() => {
      if (!profileData.value?.recent?.length) return []
      return profileData.value.recent
        .filter(m => m.result && ['W', 'D', 'L'].includes(m.result))
        .slice(0, 5)
        .map(m => m.result)
    })

    function formCls(result) {
      if (result === 'W') return 'bg-emerald-600 text-white'
      if (result === 'D') return 'bg-yellow-600 text-white'
      return 'bg-red-700 text-white'
    }

    function formatDate(dateStr) {
      if (!dateStr) return '—'
      const d = new Date(dateStr)
      return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    }

    async function fetchProfile() {
      const teamId = props.team?.team?.id
      if (!teamId) return
      loading.value    = true
      fetchError.value = ''
      try {
        const r = await fetch(`${API_URL}/team/profile/${teamId}/${props.season}`)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        profileData.value = await r.json()
      } catch (e) {
        fetchError.value = `Erro ao carregar perfil: ${e.message}`
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchProfile)

    return { profileData, loading, fetchError, recentForm, formCls, formatDate }
  }
}
</script>
