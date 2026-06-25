<template>
  <div class="p-6 space-y-6">
    <h2 class="text-2xl font-bold text-white">Exportar Dados</h2>

    <!-- Tipo de dado -->
    <div class="bg-slate-800 rounded-xl p-5">
      <p class="text-slate-400 text-sm font-medium mb-3 uppercase tracking-wide">Tipo de dado</p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button
          v-for="type in dataTypes"
          :key="type.id"
          @click="selectDataType(type)"
          :class="[
            'px-4 py-3 rounded-lg text-sm font-medium transition text-left border',
            selectedType?.id === type.id
              ? 'bg-blue-600 border-blue-500 text-white'
              : 'bg-slate-700 border-slate-600 text-slate-300 hover:border-blue-500 hover:text-white'
          ]"
        >
          <span class="block text-lg mb-1">{{ type.icon }}</span>
          {{ type.name }}
        </button>
      </div>
    </div>

    <!-- Liga e Temporada -->
    <div v-if="selectedType" class="bg-slate-800 rounded-xl p-5 space-y-4">
      <p class="text-slate-400 text-sm font-medium uppercase tracking-wide">Filtros</p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-slate-300 text-sm mb-2">Liga</label>
          <select v-model="selectedLeague" class="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:outline-none focus:border-blue-500">
            <option value="">Selecione uma liga</option>
            <option v-for="l in leagues" :key="l.id" :value="l.id">
              {{ l.name }} — {{ l.country }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-slate-300 text-sm mb-2">Temporada</label>
          <select v-model="selectedSeason" class="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:outline-none focus:border-blue-500">
            <option value="">Selecione uma temporada</option>
            <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <!-- Datas (somente Fixtures) -->
      <div v-if="selectedType.id === '1'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-slate-300 text-sm mb-2">Data inicial</label>
          <input
            type="date"
            v-model="fromDate"
            class="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-slate-300 text-sm mb-2">Data final</label>
          <input
            type="date"
            v-model="toDate"
            class="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- Campos (checkboxes) -->
    <div v-if="selectedType" class="bg-slate-800 rounded-xl p-5">
      <div class="flex items-center justify-between mb-4">
        <p class="text-slate-400 text-sm font-medium uppercase tracking-wide">Informações a exportar</p>
        <div class="flex gap-2">
          <button @click="selectAll" class="text-xs px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition">
            Todos
          </button>
          <button @click="clearAll" class="text-xs px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition">
            Nenhum
          </button>
        </div>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        <label
          v-for="field in selectedType.fields"
          :key="field.key"
          class="flex items-center gap-2 cursor-pointer group"
        >
          <input
            type="checkbox"
            :value="field.key"
            v-model="selectedFields"
            class="w-4 h-4 rounded border-slate-500 text-blue-600 bg-slate-700 focus:ring-blue-500 focus:ring-offset-slate-800 cursor-pointer"
          />
          <span class="text-sm text-slate-300 group-hover:text-white transition select-none">
            {{ field.label }}
          </span>
        </label>
      </div>
    </div>

    <!-- Botão exportar -->
    <div v-if="selectedType" class="flex items-center gap-4">
      <button
        @click="doExport"
        :disabled="!canExport || loading"
        class="px-6 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition flex items-center gap-2"
      >
        <span v-if="loading" class="animate-spin">⏳</span>
        <span v-else>📥</span>
        {{ loading ? 'Exportando...' : 'Exportar CSV' }}
      </button>
      <span v-if="selectedFields.length === 0" class="text-amber-400 text-sm">
        Selecione ao menos um campo
      </span>
      <span v-else-if="!selectedLeague" class="text-amber-400 text-sm">
        Selecione uma liga
      </span>
      <span v-else-if="!selectedSeason" class="text-amber-400 text-sm">
        Selecione uma temporada
      </span>
      <span v-else-if="selectedType.id === '1' && (!fromDate || !toDate)" class="text-amber-400 text-sm">
        Informe o período de datas
      </span>
    </div>

    <!-- Feedback -->
    <div
      v-if="message"
      :class="[
        'px-4 py-3 rounded-xl text-sm font-medium',
        messageType === 'success' ? 'bg-green-900/50 border border-green-700 text-green-300' : 'bg-red-900/50 border border-red-700 text-red-300'
      ]"
    >
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

const API_URL = 'http://localhost:3001'

const FIELD_LABELS = {
  id: 'ID', league: 'Liga', season: 'Temporada', timestamp: 'Timestamp',
  date: 'Data', status: 'Status', home: 'Time Casa', away: 'Time Fora',
  goals_home: 'Gols Casa', goals_away: 'Gols Fora',
  halftime_home: 'HT Casa', halftime_away: 'HT Fora',
  position: 'Posição', team: 'Time', played: 'Jogos',
  wins: 'Vitórias', draws: 'Empates', losses: 'Derrotas',
  points: 'Pontos', goals_for: 'Gols Feitos', goals_against: 'Gols Sofridos',
  goal_difference: 'Saldo de Gols', rank: 'Posição', player: 'Jogador',
  goals: 'Gols', assists: 'Assistências', appearances: 'Jogos',
  fixture_id: 'ID Partida', reason: 'Motivo', until: 'Até quando',
}

const DATA_TYPES = [
  {
    id: '1', name: 'Partidas', icon: '⚽',
    endpoint: 'fixtures',
    fields: ['id','league','season','timestamp','date','status','home','away','goals_home','goals_away','halftime_home','halftime_away'],
  },
  {
    id: '2', name: 'Classificação', icon: '📊',
    endpoint: 'standings',
    fields: ['position','team','played','wins','draws','losses','points','goals_for','goals_against','goal_difference'],
  },
  {
    id: '3', name: 'Artilheiros', icon: '🎯',
    endpoint: 'topscorers',
    fields: ['rank','player','team','season','goals','assists','appearances'],
  },
  {
    id: '4', name: 'Lesões', icon: '🩹',
    endpoint: 'injuries',
    fields: ['player','team','season','fixture_id','reason','until'],
  },
].map(t => ({
  ...t,
  fields: t.fields.map(k => ({ key: k, label: FIELD_LABELS[k] || k }))
}))

const SEASONS = ['2024', '2023', '2022', '2021', '2020']

export default {
  name: 'ExportData',
  setup() {
    const leagues = ref([])
    const selectedType = ref(null)
    const selectedLeague = ref('')
    const selectedSeason = ref('')
    const fromDate = ref('')
    const toDate = ref('')
    const selectedFields = ref([])
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('success')

    const dataTypes = DATA_TYPES
    const seasons = SEASONS

    function showMessage(text, type = 'success') {
      message.value = text
      messageType.value = type
      setTimeout(() => { message.value = '' }, 4000)
    }

    function selectDataType(type) {
      selectedType.value = type
      selectedFields.value = type.fields.map(f => f.key)
    }

    function selectAll() {
      selectedFields.value = selectedType.value.fields.map(f => f.key)
    }

    function clearAll() {
      selectedFields.value = []
    }

    const canExport = computed(() => {
      if (!selectedType.value || selectedFields.value.length === 0) return false
      if (!selectedLeague.value || !selectedSeason.value) return false
      if (selectedType.value.id === '1' && (!fromDate.value || !toDate.value)) return false
      return true
    })

    function buildQueryString(params) {
      return Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&')
    }

    function toCSV(rows, fields) {
      const headers = fields.map(k => FIELD_LABELS[k] || k).join(',')
      const lines = rows.map(row =>
        fields.map(f => {
          const val = row[f] ?? ''
          return typeof val === 'string' && val.includes(',') ? `"${val}"` : val
        }).join(',')
      )
      return [headers, ...lines].join('\n')
    }

    function downloadCSV(content, filename) {
      const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    }

    async function doExport() {
      if (!canExport.value || loading.value) return
      loading.value = true
      message.value = ''

      try {
        const type = selectedType.value
        let qs = buildQueryString({
          league_id: selectedLeague.value,
          season: selectedSeason.value,
          ...(type.id === '1' ? { from_date: fromDate.value, to_date: toDate.value } : {})
        })

        const res = await fetch(`${API_URL}/export/${type.endpoint}?${qs}`, { method: 'POST' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json = await res.json()

        if (!json.success) throw new Error(json.message || 'Falha na exportação')

        const dataKey = { '1': 'data', '2': 'data', '3': 'data', '4': 'data' }[type.id]
        const rows = json[dataKey] || []

        if (rows.length === 0) {
          showMessage('Nenhum dado encontrado para os filtros selecionados.', 'error')
          return
        }

        const csv = toCSV(rows, selectedFields.value)
        const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
        const leagueName = leagues.value.find(l => l.id == selectedLeague.value)?.name?.replace(/\s/g, '_') || selectedLeague.value
        downloadCSV(csv, `${leagueName}_${type.endpoint}_${selectedSeason.value}_${ts}.csv`)

        showMessage(`${rows.length} registros exportados com sucesso!`)
      } catch (err) {
        showMessage(`Erro: ${err.message}`, 'error')
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      try {
        const res = await fetch(`${API_URL}/export/leagues`)
        const json = await res.json()
        leagues.value = json.leagues || []
      } catch {
        leagues.value = [
          { id: 39, name: 'Premier League', country: 'England' },
          { id: 61, name: 'Ligue 1', country: 'France' },
          { id: 78, name: 'Bundesliga', country: 'Germany' },
          { id: 135, name: 'Serie A', country: 'Italy' },
          { id: 71, name: 'Série A', country: 'Brazil' },
          { id: 140, name: 'La Liga', country: 'Spain' },
        ]
      }
    })

    return {
      leagues, dataTypes, seasons,
      selectedType, selectedLeague, selectedSeason, fromDate, toDate,
      selectedFields, loading, message, messageType, canExport,
      selectDataType, selectAll, clearAll, doExport,
    }
  }
}
</script>
