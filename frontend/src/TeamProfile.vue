<template>
  <!-- Dark overlay -->
  <div class="fixed inset-0 z-50 flex">
    <div class="flex-1 bg-black/40" @click="$emit('close')"></div>

    <!-- Slide-over panel -->
    <div class="w-full max-w-md bg-white border-l border-gray-200 flex flex-col h-full overflow-hidden shadow-2xl">

      <!-- Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0 bg-blue-700">
        <div class="flex items-center gap-3 min-w-0">
          <div>
            <h2 class="text-lg font-bold text-white truncate">{{ team.team?.name || team.name }}</h2>
            <p class="text-blue-200 text-sm">Temporada {{ season }}</p>
          </div>
        </div>
        <button
          @click="$emit('close')"
          class="text-blue-200 hover:text-white text-2xl leading-none flex-shrink-0 ml-2"
        >×</button>
      </div>

      <!-- Scrollable content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- Resumo da temporada -->
        <div class="bg-gray-50 rounded-xl border border-gray-200 p-4">
          <h3 class="text-gray-500 font-semibold mb-3 text-sm uppercase tracking-wider">Temporada Atual</h3>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div>
              <p class="text-2xl font-bold text-gray-900">{{ team.rank }}º</p>
              <p class="text-gray-500 text-xs mt-1">Posição</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-blue-600">{{ team.points }}</p>
              <p class="text-gray-500 text-xs mt-1">Pontos</p>
            </div>
            <div>
              <p class="text-2xl font-bold text-gray-900">{{ team.all?.played }}</p>
              <p class="text-gray-500 text-xs mt-1">Jogos</p>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-2 text-center mt-3 pt-3 border-t border-gray-200">
            <div>
              <p class="text-lg font-semibold text-emerald-600">{{ team.all?.win }}</p>
              <p class="text-gray-500 text-xs">V</p>
            </div>
            <div>
              <p class="text-lg font-semibold text-amber-600">{{ team.all?.draw }}</p>
              <p class="text-gray-500 text-xs">E</p>
            </div>
            <div>
              <p class="text-lg font-semibold text-red-600">{{ team.all?.lose }}</p>
              <p class="text-gray-500 text-xs">D</p>
            </div>
            <div>
              <p class="text-lg font-semibold text-gray-900">{{ team.goalsDiff > 0 ? '+' : '' }}{{ team.goalsDiff }}</p>
              <p class="text-gray-500 text-xs">SG</p>
            </div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="text-center py-8 text-gray-400">
          <span class="animate-spin text-2xl">⏳</span>
          <p class="mt-2 text-sm">Carregando histórico...</p>
        </div>

        <template v-else-if="profileData">

          <!-- Forma (últimas 5) -->
          <div v-if="recentForm.length" class="bg-gray-50 rounded-xl border border-gray-200 p-4">
            <h3 class="text-gray-900 font-semibold mb-3 text-sm">Forma Recente</h3>
            <div class="flex gap-2">
              <span
                v-for="(r, i) in recentForm"
                :key="i"
                :class="['w-8 h-8 rounded flex items-center justify-center text-sm font-bold', formCls(r)]"
              >{{ r }}</span>
            </div>
          </div>

          <!-- Últimas partidas -->
          <div v-if="profileData.recent?.length" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <h3 class="text-gray-900 font-semibold text-sm">Últimas Partidas</h3>
            </div>
            <div class="divide-y divide-gray-200">
              <div
                v-for="(m, i) in profileData.recent"
                :key="i"
                class="px-4 py-2.5 flex items-center gap-3 text-sm"
              >
                <span :class="['w-5 h-5 rounded text-xs font-bold flex items-center justify-center flex-shrink-0', formCls(m.result)]">
                  {{ m.result }}
                </span>
                <span class="text-gray-500 text-xs w-10 flex-shrink-0">{{ m.is_home ? 'Casa' : 'Fora' }}</span>
                <span class="text-gray-900 flex-1 truncate">{{ m.opponent }}</span>
                <span class="font-bold text-gray-900 flex-shrink-0">{{ m.goals_for }}–{{ m.goals_against }}</span>
                <span class="text-gray-400 text-xs flex-shrink-0">{{ formatDate(m.date) }}</span>
              </div>
            </div>
          </div>

          <!-- Próximas partidas -->
          <div v-if="profileData.upcoming?.length" class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-4 py-3 border-b border-gray-200 bg-gray-50">
              <h3 class="text-gray-900 font-semibold text-sm">Próximas Partidas</h3>
            </div>
            <div class="divide-y divide-gray-200">
              <div
                v-for="(m, i) in profileData.upcoming"
                :key="i"
                class="px-4 py-2.5 flex items-center gap-3 text-sm"
              >
                <span class="text-gray-400 text-xs flex-shrink-0 w-16">{{ formatDate(m.date) }}</span>
                <span class="text-gray-500 text-xs w-10 flex-shrink-0">{{ m.is_home ? 'Casa' : 'Fora' }}</span>
                <span class="text-gray-900 flex-1 truncate">{{ m.opponent }}</span>
                <span class="text-gray-500 text-xs flex-shrink-0 truncate max-w-[100px]">{{ m.league }}</span>
              </div>
            </div>
          </div>

          <div v-if="!profileData.recent?.length && !profileData.upcoming?.length" class="text-center py-6 text-gray-400 text-sm">
            Sem histórico de partidas disponível para esta temporada.
          </div>

        </template>

        <!-- Erro -->
        <div v-if="fetchError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
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
      if (result === 'D') return 'bg-amber-500 text-white'
      return 'bg-red-600 text-white'
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
