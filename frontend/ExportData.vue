<template>
  <div class="min-h-screen bg-slate-900 text-white p-8">
    <!-- Header -->
    <div class="max-w-6xl mx-auto">
      <h1 class="text-4xl font-bold mb-2">📊 Exportar Dados</h1>
      <p class="text-slate-400 mb-8">Extraia dados de ligas e salve em CSV</p>

      <!-- Grid Principal -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Formulário -->
        <div class="lg:col-span-1">
          <div class="bg-slate-800 rounded-lg p-6 sticky top-8">
            <h2 class="text-xl font-bold mb-6">⚙️ Configurações</h2>

            <!-- Tipo de Dados -->
            <div class="mb-6">
              <label class="block text-sm font-medium mb-2">Tipo de Dados</label>
              <select 
                v-model="selectedDataType"
                @change="onDataTypeChange"
                class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              >
                <option value="">Selecione um tipo...</option>
                <option v-for="type in dataTypes" :key="type.id" :value="type.id">
                  {{ type.name }}
                </option>
              </select>
            </div>

            <!-- Liga -->
            <div class="mb-6">
              <label class="block text-sm font-medium mb-2">Liga</label>
              <select 
                v-model="selectedLeague"
                class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              >
                <option value="">Selecione uma liga...</option>
                <option v-for="league in leagues" :key="league.id" :value="league.id">
                  {{ league.name }} ({{ league.country }})
                </option>
              </select>
            </div>

            <!-- Temporada -->
            <div class="mb-6">
              <label class="block text-sm font-medium mb-2">Temporada (Ano)</label>
              <input 
                v-model="selectedSeason"
                type="number"
                :min="2018"
                :max="new Date().getFullYear()"
                class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
                placeholder="2024"
              />
            </div>

            <!-- Período (apenas para Fixtures) -->
            <div v-if="selectedDataType === '1'" class="mb-6">
              <label class="block text-sm font-medium mb-2">Data Inicial</label>
              <input 
                v-model="fromDate"
                type="date"
                class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              />
              
              <label class="block text-sm font-medium mb-2 mt-4">Data Final</label>
              <input 
                v-model="toDate"
                type="date"
                class="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-white"
              />
            </div>

            <!-- Botão Exportar -->
            <button 
              @click="exportData"
              :disabled="!canExport || loading"
              class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-bold py-3 rounded-lg transition mb-4"
            >
              <span v-if="loading" class="inline-block mr-2">⏳</span>
              {{ loading ? 'Processando...' : '📥 Exportar' }}
            </button>

            <!-- Status -->
            <div v-if="statusMessage" :class="[
              'p-3 rounded text-sm',
              statusMessage.success ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'
            ]">
              {{ statusMessage.message }}
            </div>
          </div>
        </div>

        <!-- Resultados -->
        <div class="lg:col-span-2">
          <!-- Tabela de Dados -->
          <div v-if="exportedData.length > 0" class="bg-slate-800 rounded-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-xl font-bold">📋 Dados Exportados ({{ exportedData.length }})</h3>
              <button
                @click="downloadCSV"
                class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm font-bold"
              >
                💾 Download CSV
              </button>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-slate-700">
                    <th 
                      v-for="field in currentFields" 
                      :key="field"
                      class="text-left py-2 px-3 font-semibold text-slate-300"
                    >
                      {{ field }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr 
                    v-for="(row, idx) in exportedData.slice(0, 10)" 
                    :key="idx"
                    class="border-b border-slate-700 hover:bg-slate-700"
                  >
                    <td 
                      v-for="field in currentFields" 
                      :key="field"
                      class="py-2 px-3 text-slate-300"
                    >
                      {{ row[field] || '-' }}
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-if="exportedData.length > 10" class="text-sm text-slate-400 mt-4">
                Mostrando 10 de {{ exportedData.length }} registros
              </p>
            </div>
          </div>

          <!-- Arquivos Disponíveis -->
          <div class="bg-slate-800 rounded-lg p-6">
            <h3 class="text-xl font-bold mb-4">📁 Arquivos Exportados</h3>
            
            <div v-if="downloadedFiles.length > 0" class="space-y-2">
              <div 
                v-for="file in downloadedFiles.slice(0, 10)" 
                :key="file.filename"
                class="flex justify-between items-center bg-slate-700 p-3 rounded"
              >
                <div>
                  <p class="font-medium">{{ file.filename }}</p>
                  <p class="text-sm text-slate-400">{{ file.size_kb.toFixed(2) }} KB</p>
                </div>
                <button
                  @click="downloadFile(file.filename)"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                >
                  ⬇️ Download
                </button>
              </div>
              <p v-if="downloadedFiles.length > 10" class="text-sm text-slate-400 mt-4">
                Mostrando 10 de {{ downloadedFiles.length }} arquivos
              </p>
            </div>
            <p v-else class="text-slate-400">Nenhum arquivo exportado ainda</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const BFF_URL = import.meta.env.VITE_BFF_URL || 'http://localhost:3001'

// Estado
const dataTypes = ref([])
const leagues = ref([])
const selectedDataType = ref('')
const selectedLeague = ref('')
const selectedSeason = ref(new Date().getFullYear())
const fromDate = ref('')
const toDate = ref('')
const loading = ref(false)
const statusMessage = ref(null)
const exportedData = ref([])
const downloadedFiles = ref([])

// Campos por tipo de dado
const fieldsMap = {
  '1': ['id', 'league', 'season', 'date', 'status', 'home', 'away', 'goals_home', 'goals_away'],
  '2': ['position', 'team', 'played', 'wins', 'draws', 'losses', 'points', 'goals_for', 'goals_against'],
  '3': ['rank', 'player', 'team', 'goals', 'assists', 'appearances'],
  '4': ['player', 'team', 'reason', 'until']
}

const currentFields = computed(() => fieldsMap[selectedDataType.value] || [])

const canExport = computed(() => {
  const hasBasicFields = selectedDataType.value && selectedLeague.value && selectedSeason.value
  if (selectedDataType.value === '1') {
    return hasBasicFields && fromDate.value && toDate.value
  }
  return hasBasicFields
})

// Funções
onMounted(async () => {
  await loadDataTypes()
  await loadLeagues()
  await loadDownloads()
})

const loadDataTypes = async () => {
  try {
    const response = await axios.get(`${BFF_URL}/export/data-types`)
    dataTypes.value = response.data.types
  } catch (error) {
    console.error('Erro ao carregar tipos:', error)
  }
}

const loadLeagues = async () => {
  try {
    const response = await axios.get(`${BFF_URL}/export/leagues`)
    leagues.value = response.data.leagues
  } catch (error) {
    console.error('Erro ao carregar ligas:', error)
  }
}

const loadDownloads = async () => {
  try {
    const response = await axios.get(`${BFF_URL}/export/downloads`)
    downloadedFiles.value = response.data.exports || []
  } catch (error) {
    console.error('Erro ao carregar downloads:', error)
  }
}

const onDataTypeChange = () => {
  exportedData.value = []
  statusMessage.value = null
}

const exportData = async () => {
  if (!canExport.value || loading.value) return

  loading.value = true
  statusMessage.value = null

  try {
    let response

    if (selectedDataType.value === '1') {
      response = await axios.post(`${BFF_URL}/export/fixtures`, {
        league_id: selectedLeague.value,
        season: selectedSeason.value.toString(),
        from_date: fromDate.value,
        to_date: toDate.value
      })
    } else if (selectedDataType.value === '2') {
      response = await axios.post(`${BFF_URL}/export/standings`, {
        league_id: selectedLeague.value,
        season: selectedSeason.value.toString()
      })
    } else if (selectedDataType.value === '3') {
      response = await axios.post(`${BFF_URL}/export/topscorers`, {
        league_id: selectedLeague.value,
        season: selectedSeason.value.toString()
      })
    } else if (selectedDataType.value === '4') {
      response = await axios.post(`${BFF_URL}/export/injuries`, {
        league_id: selectedLeague.value,
        season: selectedSeason.value.toString()
      })
    }

    if (response.data.success) {
      exportedData.value = response.data.data
      statusMessage.value = {
        success: true,
        message: `✅ ${response.data.message}`
      }
      await loadDownloads()
    } else {
      statusMessage.value = {
        success: false,
        message: `❌ ${response.data.message}`
      }
    }
  } catch (error) {
    statusMessage.value = {
      success: false,
      message: `❌ Erro: ${error.message}`
    }
  } finally {
    loading.value = false
  }
}

const downloadCSV = () => {
  if (exportedData.value.length === 0) return

  // Criar CSV
  const headers = currentFields.value
  const rows = exportedData.value.map(row => 
    headers.map(field => {
      const value = row[field] || ''
      return `"${value}"`
    }).join(',')
  )

  const csv = [headers.join(','), ...rows].join('\n')

  // Download
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `export_${new Date().getTime()}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const downloadFile = (filename) => {
  // Baixar arquivo do servidor
  const dataDir = '/data/exports/'
  window.open(`${BFF_URL}${dataDir}${filename}`, '_blank')
}
</script>

<style scoped>
/* Estilos adicionais se necessário */
</style>
