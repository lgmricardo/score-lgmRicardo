<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
    <header class="bg-slate-800 border-b border-slate-700 sticky top-0 z-50 shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-3">
            <div class="text-3xl">⚽</div>
            <div>
              <h1 class="text-2xl font-bold text-white">Football App</h1>
              <p class="text-sm text-slate-400">API-Football Dashboard</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div v-if="loading" class="text-amber-400 flex items-center gap-2">
              <span class="animate-spin">⏳</span> Carregando...
            </div>
            <button
              @click="clearCache"
              class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
            >
              🔄 Atualizar
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex gap-2 mb-6 overflow-x-auto pb-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition whitespace-nowrap',
            activeTab === tab.id
              ? 'bg-blue-600 text-white'
              : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
          ]"
        >
          {{ tab.icon }} {{ tab.name }}
        </button>

      </div>

      <div v-if="error" class="bg-red-900/20 border border-red-700 text-red-400 px-4 py-3 rounded-lg mb-6">
        ❌ {{ error }}
      </div>

      <template v-if="activeTab === 'dashboard'">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <p class="text-slate-400 text-sm">Partidas Hoje</p>
            <p class="text-3xl font-bold text-white">{{ todayFixtures.length }}</p>
          </div>
          <div class="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <p class="text-slate-400 text-sm">Próximas Partidas</p>
            <p class="text-3xl font-bold text-white">{{ nextFixtures.length }}</p>
          </div>
          <div class="bg-slate-700 rounded-lg p-4 border border-slate-600">
            <p class="text-slate-400 text-sm">Ligas Disponíveis</p>
            <p class="text-3xl font-bold text-white">{{ leagues.length }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div class="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 class="text-xl font-bold text-white mb-4">⚽ Partidas Hoje</h2>
            <div v-if="todayFixtures.length === 0" class="text-slate-400 text-center py-8">
              Nenhuma partida hoje
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="(fixture, i) in todayFixtures.slice(0, 5)"
                :key="i"
                class="bg-slate-700 p-3 rounded-lg border border-slate-600"
              >
                <div class="flex justify-between">
                  <span class="text-white font-medium">{{ fixture.home.name }}</span>
                  <span class="text-slate-300 text-sm">{{ formatTime(fixture.date) }}</span>
                </div>
                <div class="text-white">vs {{ fixture.away.name }}</div>
              </div>
            </div>
          </div>

          <div class="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h2 class="text-xl font-bold text-white mb-4">📅 Próximas Partidas</h2>
            <div v-if="nextFixtures.length === 0" class="text-slate-400 text-center py-8">
              Nenhuma partida nos próximos dias
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="(fixture, i) in nextFixtures.slice(0, 5)"
                :key="i"
                class="bg-slate-700 p-3 rounded-lg border border-slate-600"
              >
                <div class="flex justify-between">
                  <span class="text-white font-medium">{{ fixture.home.name }}</span>
                  <span class="text-slate-300 text-sm">{{ formatDate(fixture.date) }}</span>
                </div>
                <div class="text-white">vs {{ fixture.away.name }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'live'">
        <LiveTab />
      </template>

      <template v-if="activeTab === 'leagues'">
        <div class="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 class="text-xl font-bold text-white mb-4">🌍 Ligas</h2>
          <input
            v-model="leagueSearch"
            type="text"
            placeholder="Buscar liga..."
            class="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 mb-4"
          />
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="league in filteredLeagues"
              :key="league.id"
              class="bg-slate-700 p-4 rounded-lg border border-slate-600 cursor-pointer hover:border-blue-500"
              @click="selectLeague(league)"
            >
              <p class="font-bold text-white">{{ league.name }}</p>
              <p class="text-slate-400 text-sm">{{ league.country }}</p>
              <p class="text-slate-500 text-xs mt-2">ID: {{ league.id }}</p>
            </div>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'standings'">
        <div class="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 class="text-xl font-bold text-white mb-4">📊 Tabela</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-slate-400 text-sm mb-2">Liga</label>
              <select v-model="selectedLeagueId" class="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600">
                <option value="">Selecione</option>
                <option value="39">Premier League</option>
                <option value="61">Ligue 1</option>
                <option value="78">Bundesliga</option>
                <option value="135">Serie A</option>
                <option value="71">Serie A Brasil</option>
              </select>
            </div>
            <div>
              <label class="block text-slate-400 text-sm mb-2">Temporada</label>
              <select v-model="selectedSeason" class="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600">
                <option value="">Selecione</option>
                <option value="2024">2024</option>
                <option value="2023">2023</option>
              </select>
            </div>
          </div>
          <button @click="loadStandings" class="px-6 py-2 bg-blue-600 text-white rounded-lg mb-4">
            Carregar Tabela
          </button>
          <div v-if="standings.length > 0" class="overflow-x-auto">
            <table class="w-full text-sm text-white">
              <tr class="bg-slate-700">
                <th class="px-4 py-2 text-left">Pos</th>
                <th class="px-4 py-2 text-left">Time</th>
                <th class="px-4 py-2">J</th>
                <th class="px-4 py-2">V</th>
                <th class="px-4 py-2">E</th>
                <th class="px-4 py-2">D</th>
                <th class="px-4 py-2">Pts</th>
              </tr>
              <tr v-for="team in standings" :key="team.team.id" class="border-b border-slate-700 cursor-pointer hover:bg-slate-700/60" @click="selectedTeam = team">
                <td class="px-4 py-2 font-bold">{{ team.rank }}</td>
                <td class="px-4 py-2">{{ team.team.name }}</td>
                <td class="px-4 py-2 text-center">{{ team.all.played }}</td>
                <td class="px-4 py-2 text-center text-green-400">{{ team.all.win }}</td>
                <td class="px-4 py-2 text-center text-yellow-400">{{ team.all.draw }}</td>
                <td class="px-4 py-2 text-center text-red-400">{{ team.all.lose }}</td>
                <td class="px-4 py-2 text-center font-bold">{{ team.points }}</td>
              </tr>
            </table>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'topscorers'">
        <div class="bg-slate-800 rounded-lg border border-slate-700 p-6">
          <h2 class="text-xl font-bold text-white mb-4">🎯 Top Artilheiros</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <select v-model="selectedLeagueScorerssId" class="px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600">
              <option value="">Selecione Liga</option>
              <option value="39">Premier League</option>
              <option value="61">Ligue 1</option>
              <option value="78">Bundesliga</option>
              <option value="135">Serie A</option>
            </select>
            <select v-model="selectedScorerssSeason" class="px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600">
              <option value="">Selecione Temporada</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
            </select>
          </div>
          <button @click="loadTopscorers" class="px-6 py-2 bg-blue-600 text-white rounded-lg mb-4">
            Carregar
          </button>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div v-for="(scorer, index) in topscorers" :key="scorer.player.id" class="bg-slate-700 p-4 rounded-lg border border-slate-600">
              <div class="text-3xl font-bold text-yellow-400">{{ index + 1 }}. {{ scorer.statistics[0].goals.total }}</div>
              <p class="text-white font-medium mt-2">{{ scorer.player.name }}</p>
              <p class="text-slate-400 text-sm">{{ scorer.statistics[0].team.name }}</p>
            </div>
          </div>
        </div>
      </template>

      <template v-if="activeTab === 'export'">
        <ExportData />
      </template>

      <template v-if="activeTab === 'analytics'">
        <AnalyticsTab />
      </template>
    </main>

    <TeamProfile v-if="selectedTeam" :team="selectedTeam" :season="selectedSeason" @close="selectedTeam = null" />

    <footer class="bg-slate-800 border-t border-slate-700 mt-12 py-6 text-center text-slate-400 text-sm">
      <p>⚽ Football App | API-Football Dashboard</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import ExportData from './ExportData.vue'
import AnalyticsTab from './AnalyticsTab.vue'
import LiveTab from './LiveTab.vue'
import TeamProfile from './TeamProfile.vue'

const API_URL = 'http://localhost:3001'

export default {
  name: 'App',
  components: { ExportData, AnalyticsTab, LiveTab, TeamProfile },
  setup() {
    const activeTab = ref('dashboard')
    const loading = ref(false)
    const error = ref('')

    const todayFixtures = ref([])
    const nextFixtures = ref([])
    const leagues = ref([])
    const leagueSearch = ref('')

    const selectedLeagueId = ref('')
    const selectedSeason = ref('')
    const standings = ref([])

    const selectedLeagueScorerssId = ref('')
    const selectedScorerssSeason = ref('')
    const topscorers = ref([])
    const selectedTeam = ref(null)

    const tabs = [
      { id: 'dashboard', name: 'Dashboard', icon: '🏠' },
      { id: 'live', name: 'Ao Vivo', icon: '🔴' },
      { id: 'leagues', name: 'Ligas', icon: '🌍' },
      { id: 'standings', name: 'Tabela', icon: '📊' },
      { id: 'topscorers', name: 'Artilheiros', icon: '🎯' },
      { id: 'export', name: 'Exportar', icon: '📥' },
      { id: 'analytics', name: 'Análise', icon: '🧠' }
    ]

    const filteredLeagues = computed(() => {
      if (!leagueSearch.value) return leagues.value
      return leagues.value.filter(l =>
        l.name.toLowerCase().includes(leagueSearch.value.toLowerCase())
      )
    })

    async function fetchAPI(endpoint) {
      try {
        error.value = ''
        loading.value = true
        const response = await fetch(`${API_URL}${endpoint}`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        return await response.json()
      } catch (err) {
        error.value = `Erro: ${err.message}`
        return null
      } finally {
        loading.value = false
      }
    }

    async function loadDashboard() {
      const [today, next, leaguesData] = await Promise.all([
        fetchAPI('/fixtures/today'),
        fetchAPI('/fixtures/next'),
        fetchAPI('/leagues')
      ])
      if (today) todayFixtures.value = today.fixtures || []
      if (next) nextFixtures.value = next.fixtures || []
      if (leaguesData) leagues.value = leaguesData.leagues || []
    }

    async function loadStandings() {
      if (!selectedLeagueId.value || !selectedSeason.value) {
        error.value = 'Selecione liga e temporada'
        return
      }
      const data = await fetchAPI(`/standings/${selectedLeagueId.value}/${selectedSeason.value}`)
      if (data) standings.value = data.standings || []
    }

    async function loadTopscorers() {
      if (!selectedLeagueScorerssId.value || !selectedScorerssSeason.value) {
        error.value = 'Selecione liga e temporada'
        return
      }
      const data = await fetchAPI(
        `/players/topscorers/${selectedLeagueScorerssId.value}/${selectedScorerssSeason.value}`
      )
      if (data) topscorers.value = data.scorers || []
    }

    function selectLeague(league) {
      selectedLeagueId.value = league.id
      selectedSeason.value = '2024'
      activeTab.value = 'standings'
    }

    function formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    }

    function formatTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    }

    function clearCache() {
      loading.value = true
      setTimeout(() => loadDashboard(), 500)
    }

    loadDashboard()

    return {
      activeTab, loading, error, tabs, todayFixtures, nextFixtures, leagues, leagueSearch,
      filteredLeagues, selectedLeagueId, selectedSeason, standings, selectedLeagueScorerssId,
      selectedScorerssSeason, topscorers, loadStandings, loadTopscorers, selectLeague,
      formatDate, formatTime, clearCache, selectedTeam
    }
  }
}
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>
