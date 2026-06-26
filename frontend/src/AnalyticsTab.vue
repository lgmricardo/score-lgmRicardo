<template>
  <div class="space-y-6">

    <!-- HEADER -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
      <div class="flex items-center gap-3 mb-5">
        <span class="text-3xl">🧠</span>
        <div>
          <h2 class="text-2xl font-bold text-gray-900">Análise ML</h2>
          <p class="text-gray-500 text-sm">Isolation Forest · Z-Score · LOF · Random Forest · Logistic Regression · SHAP</p>
        </div>
      </div>

      <!-- Seletores principais (compartilhados exceto multi-liga) -->
      <div v-if="activeSubTab !== 'multiliga'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-gray-500 text-xs uppercase tracking-wider mb-1">Liga</label>
          <select v-model="selectedLeague" class="w-full px-4 py-2 bg-white text-gray-900 rounded-lg border border-gray-300 focus:border-blue-500 focus:outline-none">
            <option value="">Selecione uma liga</option>
            <option v-for="l in leagues" :key="l.id" :value="l.id">{{ l.name }} ({{ l.country }})</option>
          </select>
        </div>
        <div>
          <label class="block text-gray-500 text-xs uppercase tracking-wider mb-1">Temporada</label>
          <select v-model="selectedSeason" class="w-full px-4 py-2 bg-white text-gray-900 rounded-lg border border-gray-300 focus:border-blue-500 focus:outline-none">
            <option value="">Selecione</option>
            <option v-for="y in seasons" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="handleMainAction"
            :disabled="!selectedLeague || !selectedSeason || phaseLoading"
            class="w-full px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
          >
            <span v-if="phaseLoading" class="animate-spin">⏳</span>
            <span v-else>{{ activeAction.icon }}</span>
            {{ phaseLoading ? 'Carregando...' : activeAction.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- ERRO -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      ❌ {{ error }}
    </div>

    <!-- SUMMARY CARDS -->
    <div v-if="summaryCards" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        v-for="card in summaryCards"
        :key="card.label"
        class="rounded-xl border p-4 text-center"
        :class="card.cls"
      >
        <p class="text-xs uppercase tracking-wider mb-1" :class="card.labelCls">{{ card.label }}</p>
        <p class="text-3xl font-bold" :class="card.valCls">{{ card.value }}</p>
      </div>
    </div>

    <!-- SUB-TABS -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="tab in subTabs"
        :key="tab.id"
        @click="switchSubTab(tab.id)"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition text-sm border',
          activeSubTab === tab.id
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-100'
        ]"
      >
        {{ tab.icon }} {{ tab.name }}
      </button>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- FASE 1: CLASSIFICAÇÃO                                        -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'standings'" class="space-y-6">
      <div v-if="!standingsData" class="empty-state">
        <div class="text-4xl mb-3">📊</div>
        <p>Selecione uma liga e temporada, depois clique em <strong>Analisar</strong>.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="📍 Posição vs Pontos">
            <canvas ref="standingsScatterCanvas"></canvas>
          </ChartBox>
          <ChartBox title="📊 Z-Score de Pontos por Time">
            <canvas ref="standingsZScoreCanvas"></canvas>
          </ChartBox>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatsCard v-for="(s, k) in standingsData.statistics" :key="k" :stat="s" />
        </div>
        <OutlierTable :items="standingsData.items" type="standings" />
        <InsightPanel :insights="standingsData.insights" />
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- FASE 1: ARTILHEIROS                                          -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'topscorers'" class="space-y-6">
      <div v-if="!scorersData" class="empty-state">
        <div class="text-4xl mb-3">🎯</div>
        <p>Selecione uma liga e temporada, depois clique em <strong>Analisar</strong>.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="⚽ Gols vs Assistências">
            <canvas ref="scorersBubbleCanvas"></canvas>
          </ChartBox>
          <ChartBox title="⚡ Eficiência (Gols/Jogo)">
            <canvas ref="scorersEffCanvas"></canvas>
          </ChartBox>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatsCard v-for="(s, k) in scorersData.statistics" :key="k" :stat="s" />
        </div>
        <OutlierTable :items="scorersData.items" type="topscorers" />
        <InsightPanel :insights="scorersData.insights" />
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- FASE 2: LESÕES                                               -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'injuries'" class="space-y-6">
      <div v-if="!injuriesData" class="empty-state">
        <div class="text-4xl mb-3">🏥</div>
        <p>Selecione liga e temporada, depois clique em <strong>Analisar Lesões</strong>.</p>
        <p class="text-xs text-gray-400 mt-2">Disponibilidade depende da cobertura da API para a liga/temporada.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="🏥 Lesões por Time">
            <canvas ref="injuriesTeamCanvas"></canvas>
          </ChartBox>
          <ChartBox title="📋 Tipos de Lesão">
            <canvas ref="injuriesTypeCanvas"></canvas>
          </ChartBox>
        </div>

        <!-- Tabela de lesões por time -->
        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 class="text-gray-900 font-semibold">Times com mais lesões</h3>
            <span class="text-gray-500 text-sm">{{ injuriesData.summary.teams_affected }} times afetados</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Lesões</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Z-Score</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="t in injuriesData.by_team.slice(0, 15)"
                  :key="t.team"
                  class="border-t border-gray-200/50 hover:bg-gray-50"
                >
                  <td class="px-4 py-3 text-gray-900 font-medium">{{ t.team }}</td>
                  <td class="px-4 py-3 text-center text-gray-900">{{ t.count }}</td>
                  <td class="px-4 py-3 text-center text-blue-600">{{ t.z_score }}σ</td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="t.is_outlier" class="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 border border-red-300">
                      ⚠️ Anômalo
                    </span>
                    <span v-else class="px-2 py-0.5 rounded text-xs text-gray-500">Normal</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <InsightPanel :insights="injuriesData.insights" />
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- FASE 2: MULTI-LIGA                                           -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'multiliga'" class="space-y-6">

      <!-- Controles Multi-Liga -->
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h3 class="text-gray-900 font-semibold mb-4">Selecione as ligas para comparar (2–5)</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-gray-500 text-xs uppercase tracking-wider mb-2">Ligas</label>
            <div class="space-y-2 max-h-52 overflow-y-auto pr-1">
              <label
                v-for="l in leagues"
                :key="l.id"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 cursor-pointer"
                :class="{ 'bg-gray-100': selectedLeagues.includes(l.id) }"
              >
                <input
                  type="checkbox"
                  :value="l.id"
                  v-model="selectedLeagues"
                  :disabled="!selectedLeagues.includes(l.id) && selectedLeagues.length >= 5"
                  class="w-4 h-4 accent-blue-500"
                />
                <span class="text-gray-900 text-sm">{{ l.name }}</span>
                <span class="text-gray-500 text-xs ml-auto">{{ l.country }}</span>
              </label>
            </div>
            <p class="text-gray-400 text-xs mt-2">{{ selectedLeagues.length }} / 5 selecionadas</p>
          </div>
          <div class="flex flex-col gap-4">
            <div>
              <label class="block text-gray-500 text-xs uppercase tracking-wider mb-1">Temporada</label>
              <select v-model="multiligaSeason" class="w-full px-4 py-2 bg-white text-gray-900 rounded-lg border border-gray-300 focus:border-blue-500 focus:outline-none">
                <option v-for="y in seasons" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <button
              @click="runCompare"
              :disabled="selectedLeagues.length < 2 || compareLoading"
              class="w-full px-6 py-3 bg-violet-600 hover:bg-violet-500 disabled:bg-gray-200 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition flex items-center justify-center gap-2 mt-auto"
            >
              <span v-if="compareLoading" class="animate-spin">⏳</span>
              <span v-else>🌍</span>
              {{ compareLoading ? 'Comparando...' : 'Comparar Ligas' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="!multiligaData" class="empty-state">
        <div class="text-4xl mb-3">🌍</div>
        <p>Selecione 2 a 5 ligas acima e clique em <strong>Comparar Ligas</strong>.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="🕸️ Radar Comparativo">
            <canvas ref="multiligaRadarCanvas"></canvas>
          </ChartBox>
          <ChartBox title="📊 Gols por Jogo por Liga">
            <canvas ref="multiligaBarsCanvas"></canvas>
          </ChartBox>
        </div>

        <!-- Tabela comparativa -->
        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200">
            <h3 class="text-gray-900 font-semibold">Comparativo Detalhado</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Liga</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Times</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Líder</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Pts Líder</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Média Pts</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Gols/Jogo</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Equilíbrio</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="lg in multiligaData.leagues"
                  :key="lg.id"
                  class="border-t border-gray-200/50 hover:bg-gray-50"
                >
                  <td class="px-4 py-3 text-gray-900 font-semibold">{{ lg.name }}</td>
                  <td class="px-4 py-3 text-center text-gray-700">{{ lg.teams }}</td>
                  <td class="px-4 py-3 text-gray-700">{{ lg.leader }}</td>
                  <td class="px-4 py-3 text-center font-bold text-gray-900">{{ lg.leader_pts }}</td>
                  <td class="px-4 py-3 text-center text-blue-600">{{ lg.avg_pts }}</td>
                  <td class="px-4 py-3 text-center text-emerald-600">{{ lg.goals_per_game }}</td>
                  <td class="px-4 py-3 text-center">
                    <div class="flex items-center gap-2">
                      <div class="flex-1 bg-gray-200 rounded-full h-1.5">
                        <div class="bg-violet-500 h-1.5 rounded-full" :style="{width: lg.competitive_balance + '%'}"></div>
                      </div>
                      <span class="text-gray-700 text-xs w-8">{{ lg.competitive_balance }}</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <InsightPanel :insights="multiligaData.insights" />
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- FASE 2: PREVISÕES                                            -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'predictions'" class="space-y-6">
      <div v-if="!predictionsData" class="empty-state">
        <div class="text-4xl mb-3">📈</div>
        <p>Selecione liga e temporada, depois clique em <strong>Prever Temporada</strong>.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="📍 Posição vs Pontos + Curva de Regressão">
            <canvas ref="predictScatterCanvas"></canvas>
          </ChartBox>
          <ChartBox title="📊 Pontos Projetados vs Atuais">
            <canvas ref="predictBarCanvas"></canvas>
          </ChartBox>
        </div>

        <!-- Tabela de previsões -->
        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 class="text-gray-900 font-semibold">Previsão de Classificação Final</h3>
            <span class="text-gray-500 text-sm">
              R²={{ predictionsData.summary.regression_r2 }} · ±{{ predictionsData.summary.residual_std }} pts
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Pos. Atual</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Pts Atual</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Pts Proj.</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Intervalo</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Pts/Jogo</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Pos. Final</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Var.</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Forma</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in predictionsData.predictions"
                  :key="p.name"
                  class="border-t border-gray-200/50 hover:bg-gray-50"
                >
                  <td class="px-4 py-3 text-center text-gray-700 font-bold">{{ p.current_rank }}</td>
                  <td class="px-4 py-3 text-gray-900 font-medium">{{ p.name }}</td>
                  <td class="px-4 py-3 text-center text-gray-900">{{ p.current_pts }}</td>
                  <td class="px-4 py-3 text-center font-bold text-blue-600">{{ p.projected_pts }}</td>
                  <td class="px-4 py-3 text-center text-gray-500 text-xs">
                    {{ p.proj_pts_low }}–{{ p.proj_pts_high }}
                  </td>
                  <td class="px-4 py-3 text-center text-gray-700">{{ p.points_rate }}</td>
                  <td class="px-4 py-3 text-center font-bold text-gray-900">{{ p.predicted_rank }}</td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="p.rank_change > 0" class="text-emerald-600 font-semibold">↑{{ p.rank_change }}</span>
                    <span v-else-if="p.rank_change < 0" class="text-red-600 font-semibold">↓{{ Math.abs(p.rank_change) }}</span>
                    <span v-else class="text-gray-400">—</span>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="p.overperforming" class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-700 border border-emerald-300">Acima</span>
                    <span v-else-if="p.underperforming" class="px-2 py-0.5 rounded text-xs bg-red-100 text-red-700 border border-red-300">Abaixo</span>
                    <span v-else class="text-gray-400 text-xs">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <InsightPanel :insights="predictionsData.insights" />
      </template>
    </div>

    <!-- FASE 3: CLUSTERS -->
    <div v-show="activeSubTab === 'clusters'" class="space-y-6">
      <div v-if="!clustersData" class="empty-state">
        <div class="text-4xl mb-3">🔵</div>
        <p>Selecione liga e temporada, depois clique em <strong>Agrupar Times</strong>.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="🔵 Ataque vs Defesa por Cluster">
            <canvas ref="clustersScatterCanvas" style="height:340px"></canvas>
          </ChartBox>
          <ChartBox title="📊 Times por Cluster">
            <canvas ref="clustersBarCanvas" style="height:340px"></canvas>
          </ChartBox>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="c in clustersData.clusters" :key="c.id" class="bg-white rounded-xl border border-gray-200 p-4">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: c.color }"></div>
              <h4 class="text-gray-900 font-semibold text-sm truncate">{{ c.name }}</h4>
              <span class="ml-auto text-gray-500 text-xs flex-shrink-0">{{ c.size }} times</span>
            </div>
            <div class="flex flex-wrap gap-1 mb-3">
              <span v-for="t in c.teams" :key="t" class="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-700">{{ t }}</span>
            </div>
            <div class="grid grid-cols-2 gap-x-2 gap-y-1 text-xs border-t border-gray-200 pt-3">
              <span class="text-gray-500">Ataque/j</span><span class="text-right text-gray-900">{{ c.centroid.attack_rate }}</span>
              <span class="text-gray-500">Defesa/j</span><span class="text-right text-gray-900">{{ c.centroid.defense_rate }}</span>
              <span class="text-gray-500">Pts/j</span><span class="text-right font-medium text-blue-600">{{ c.centroid.pts_rate }}</span>
            </div>
          </div>
        </div>
        <InsightPanel :insights="clustersData.insights" />
      </template>
    </div>

    <!-- FASE 3: MONTE CARLO -->
    <div v-show="activeSubTab === 'montecarlo'" class="space-y-6">
      <div v-if="!mcData" class="empty-state">
        <div class="text-4xl mb-3">🎲</div>
        <p>Selecione liga e temporada, depois clique em <strong>Simular Temporada</strong>.</p>
        <p class="text-xs text-gray-400 mt-2">10.000 simulações baseadas em taxas de V/E/D de cada time.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="🏆 Probabilidade de Título (Top 10)">
            <canvas ref="mcChampCanvas" style="height:360px"></canvas>
          </ChartBox>
          <ChartBox title="📊 Top-4 vs Rebaixamento por Time">
            <canvas ref="mcPositionsCanvas" style="height:360px"></canvas>
          </ChartBox>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 class="text-gray-900 font-semibold">Probabilidades por Time</h3>
            <span class="text-gray-500 text-sm">
              {{ mcData.summary?.season_complete ? 'Temporada encerrada' : (mcData.summary?.n_simulations || 0).toLocaleString('pt-BR') + ' simulações' }}
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Pos</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Pts</th>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Rest.</th>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Título%</th>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Top-4%</th>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Rebai.%</th>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Pts Final</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in mcData.results" :key="r.name" class="border-t border-gray-200/50 hover:bg-gray-50">
                  <td class="px-3 py-2 text-center font-bold text-gray-700">{{ r.current_rank }}</td>
                  <td class="px-4 py-2 text-gray-900 font-medium">{{ r.name }}</td>
                  <td class="px-3 py-2 text-center text-gray-900">{{ r.current_pts }}</td>
                  <td class="px-3 py-2 text-center text-gray-500">{{ r.games_remaining }}</td>
                  <td class="px-3 py-2 text-center">
                    <span :class="r.championship_prob > 0.5 ? 'text-amber-600 font-bold' : r.championship_prob > 0.1 ? 'text-amber-600' : 'text-gray-400'">
                      {{ (r.championship_prob * 100).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center">
                    <span :class="r.top4_prob > 0.5 ? 'text-emerald-600' : r.top4_prob > 0.2 ? 'text-emerald-500/70' : 'text-gray-400'">
                      {{ (r.top4_prob * 100).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center">
                    <span :class="r.relegation_prob > 0.3 ? 'text-red-600 font-semibold' : r.relegation_prob > 0.05 ? 'text-orange-400' : 'text-gray-400'">
                      {{ (r.relegation_prob * 100).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center text-blue-600">{{ r.avg_final_pts }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <InsightPanel :insights="mcData.insights" />
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- ZONAS: Random Forest + LR + SHAP — TIMES                   -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'zonas'" class="space-y-6">
      <div v-if="!zoneData" class="empty-state">
        <div class="text-4xl mb-3">🏅</div>
        <p>Selecione liga e temporada, depois clique em <strong>Classificar Zonas</strong>.</p>
        <p class="text-xs text-gray-400 mt-2">Random Forest + Regressão Logística + SHAP por time.</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="📊 Importância das Features (RF vs SHAP)">
            <canvas ref="zoneFeatCanvas"></canvas>
          </ChartBox>
          <ChartBox title="🏟️ Distribuição de Zonas">
            <canvas ref="zoneDistCanvas"></canvas>
          </ChartBox>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-6 text-sm">
          <div><span class="text-gray-500">RF Acurácia (in-sample):</span><span class="text-gray-900 font-bold ml-2">{{ (zoneData.models.rf_accuracy * 100).toFixed(0) }}%</span></div>
          <div><span class="text-gray-500">LR Acurácia (in-sample):</span><span class="text-gray-900 font-bold ml-2">{{ (zoneData.models.lr_accuracy * 100).toFixed(0) }}%</span></div>
          <div>
            <span class="text-gray-500">SHAP:</span>
            <span :class="zoneData.models.shap_enabled ? 'text-emerald-600' : 'text-gray-400'" class="ml-2 font-medium">
              {{ zoneData.models.shap_enabled ? '✓ Ativo' : '— Não instalado' }}
            </span>
          </div>
          <span class="text-gray-400 text-xs self-center ml-auto">{{ zoneData.models.note }}</span>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 class="text-gray-900 font-semibold">Classificação por Zona Competitiva</h3>
            <span class="text-gray-500 text-sm">{{ zoneData.total_teams }} times · Clique para ver SHAP</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">Pos</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Zona RF</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Zona LR</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Proba RF</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Driver SHAP</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in zoneData.items"
                  :key="item.name"
                  @click="selectZoneItem(item)"
                  class="border-t border-gray-200/50 hover:bg-gray-50 cursor-pointer transition"
                  :class="{ 'bg-blue-50 border-blue-300': selectedZoneItem?.name === item.name }"
                >
                  <td class="px-3 py-3 text-center font-bold text-gray-700">{{ item.rank }}</td>
                  <td class="px-4 py-3 text-gray-900 font-medium">{{ item.name }}</td>
                  <td class="px-4 py-3 text-center">
                    <span :class="zoneBadgeCls(item.rf_zone)" class="px-2 py-0.5 rounded text-xs font-medium">{{ item.rf_zone_label }}</span>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span :class="zoneBadgeCls(item.lr_zone)" class="px-2 py-0.5 rounded text-xs font-medium">{{ item.lr_zone_label }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex h-2 rounded overflow-hidden w-24">
                      <div v-for="z in 4" :key="z" :style="{ width: Math.max((item.rf_proba[z-1] || 0) * 100, 0) + '%', backgroundColor: zoneColors[z-1] }"></div>
                    </div>
                    <div class="text-gray-500 text-xs mt-0.5">{{ ((item.rf_proba[item.rf_zone] || 0) * 100).toFixed(0) }}%</div>
                  </td>
                  <td class="px-4 py-3 text-xs">
                    <span class="font-medium text-blue-600">{{ item.main_driver_label }}</span>
                    <span v-if="item.shap && item.shap[item.main_driver] !== undefined" class="text-gray-400 ml-1">
                      {{ item.shap[item.main_driver] > 0 ? '▲' : '▼' }} {{ Math.abs(item.shap[item.main_driver]).toFixed(3) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="selectedZoneItem" class="bg-white rounded-xl border border-blue-200 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-gray-900 font-semibold">
              🔍 SHAP — {{ selectedZoneItem.name }}
              <span :class="zoneBadgeCls(selectedZoneItem.rf_zone)" class="ml-2 px-2 py-0.5 rounded text-xs font-medium">{{ selectedZoneItem.rf_zone_label }}</span>
            </h3>
            <button @click="selectedZoneItem = null" class="text-gray-500 hover:text-gray-900 text-sm px-2">✕</button>
          </div>
          <p class="text-gray-500 text-sm mb-4">{{ selectedZoneItem.explanation }}</p>
          <div v-if="selectedZoneItem.shap && Object.keys(selectedZoneItem.shap).length > 0" style="height:180px">
            <canvas ref="zoneShapCanvas"></canvas>
          </div>
          <p v-else class="text-gray-400 text-sm">SHAP não disponível (instale a biblioteca shap no backend).</p>
        </div>

        <InsightPanel :insights="zoneData.insights" />
      </template>
    </div>

    <!-- ══════════════════════════════════════════════════════════════ -->
    <!-- ARQUÉTIPOS: Random Forest + LR + SHAP — JOGADORES           -->
    <!-- ══════════════════════════════════════════════════════════════ -->
    <div v-show="activeSubTab === 'arquetipos'" class="space-y-6">
      <div v-if="!archetypeData" class="empty-state">
        <div class="text-4xl mb-3">🎭</div>
        <p>Selecione liga e temporada, depois clique em <strong>Classificar Arquétipos</strong>.</p>
        <p class="text-xs text-gray-400 mt-2">Artilheiro Puro · Polivalente · Criador · Contribuição Limitada</p>
      </div>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartBox title="📊 Importância das Features (RF vs SHAP)">
            <canvas ref="archFeatCanvas"></canvas>
          </ChartBox>
          <ChartBox title="⚽ Gols/Jogo vs Assist./Jogo por Arquétipo">
            <canvas ref="archScatterCanvas"></canvas>
          </ChartBox>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-4 flex flex-wrap gap-6 text-sm">
          <div><span class="text-gray-500">RF Acurácia (in-sample):</span><span class="text-gray-900 font-bold ml-2">{{ (archetypeData.models.rf_accuracy * 100).toFixed(0) }}%</span></div>
          <div><span class="text-gray-500">LR Acurácia (in-sample):</span><span class="text-gray-900 font-bold ml-2">{{ (archetypeData.models.lr_accuracy * 100).toFixed(0) }}%</span></div>
          <div>
            <span class="text-gray-500">SHAP:</span>
            <span :class="archetypeData.models.shap_enabled ? 'text-emerald-600' : 'text-gray-400'" class="ml-2 font-medium">
              {{ archetypeData.models.shap_enabled ? '✓ Ativo' : '— Não instalado' }}
            </span>
          </div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div v-for="arch in archetypeData.archetypes" :key="arch.id" class="bg-white rounded-xl border border-gray-200 p-3">
            <div class="flex items-center gap-2 mb-2">
              <div class="w-2.5 h-2.5 rounded-full flex-shrink-0" :style="{ backgroundColor: arch.color }"></div>
              <span class="text-gray-900 text-xs font-semibold truncate">{{ arch.label }}</span>
              <span class="ml-auto text-gray-500 text-xs flex-shrink-0">{{ arch.count }}</span>
            </div>
            <div class="flex flex-wrap gap-1">
              <span v-for="p in arch.players.slice(0, 4)" :key="p" class="text-xs text-gray-500">{{ p.split(' ').pop() }}</span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 class="text-gray-900 font-semibold">Classificação por Arquétipo</h3>
            <span class="text-gray-500 text-sm">{{ archetypeData.total_players }} jogadores · Clique para ver SHAP</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-3 py-3 text-center text-gray-500 font-medium">#</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Jogador</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Arquétipo RF</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Arquétipo LR</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Gols</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">Assist</th>
                  <th class="px-4 py-3 text-center text-gray-500 font-medium">G/J</th>
                  <th class="px-4 py-3 text-left text-gray-500 font-medium">Driver SHAP</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in archetypeData.items"
                  :key="item.name"
                  @click="selectArchItem(item)"
                  class="border-t border-gray-200/50 hover:bg-gray-50 cursor-pointer transition"
                  :class="{ 'bg-blue-50 border-blue-300': selectedArchItem?.name === item.name }"
                >
                  <td class="px-3 py-3 text-center text-gray-500">{{ item.rank }}</td>
                  <td class="px-4 py-3 text-gray-900 font-medium">{{ item.name }}</td>
                  <td class="px-4 py-3 text-gray-700">{{ item.team }}</td>
                  <td class="px-4 py-3 text-center">
                    <span :class="archBadgeCls(item.rf_archetype)" class="px-2 py-0.5 rounded text-xs font-medium">{{ item.rf_archetype_label }}</span>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span :class="archBadgeCls(item.lr_archetype)" class="px-2 py-0.5 rounded text-xs font-medium">{{ item.lr_archetype_label }}</span>
                  </td>
                  <td class="px-4 py-3 text-center text-gray-900 font-bold">{{ item.features.goals }}</td>
                  <td class="px-4 py-3 text-center text-blue-600">{{ item.features.assists }}</td>
                  <td class="px-4 py-3 text-center text-emerald-600">{{ item.features.gpg }}</td>
                  <td class="px-4 py-3 text-xs">
                    <span class="font-medium text-blue-600">{{ item.main_driver_label }}</span>
                    <span v-if="item.shap && item.shap[item.main_driver] !== undefined" class="text-gray-400 ml-1">
                      {{ item.shap[item.main_driver] > 0 ? '▲' : '▼' }} {{ Math.abs(item.shap[item.main_driver]).toFixed(3) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="selectedArchItem" class="bg-white rounded-xl border border-blue-200 p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-gray-900 font-semibold">
              🔍 SHAP — {{ selectedArchItem.name }}
              <span :class="archBadgeCls(selectedArchItem.rf_archetype)" class="ml-2 px-2 py-0.5 rounded text-xs font-medium">{{ selectedArchItem.rf_archetype_label }}</span>
            </h3>
            <button @click="selectedArchItem = null" class="text-gray-500 hover:text-gray-900 text-sm px-2">✕</button>
          </div>
          <p class="text-gray-500 text-sm mb-4">{{ selectedArchItem.explanation }}</p>
          <div v-if="selectedArchItem.shap && Object.keys(selectedArchItem.shap).length > 0" style="height:180px">
            <canvas ref="archShapCanvas"></canvas>
          </div>
          <p v-else class="text-gray-400 text-sm">SHAP não disponível (instale a biblioteca shap no backend).</p>
        </div>

        <InsightPanel :insights="archetypeData.insights" />
      </template>
    </div>

    <!-- PLACEHOLDER INICIAL -->
    <div v-if="!hasAnyData && !phaseLoading && !compareLoading" class="bg-white rounded-xl border border-dashed border-gray-200 p-16 text-center">
      <div class="text-5xl mb-4">🧠</div>
      <p class="text-gray-700 text-lg font-medium">Selecione uma liga e temporada para iniciar</p>
      <p class="text-gray-400 mt-2 text-sm">Fase 1: Outliers | Fase 2: Lesões · Multi-Liga · Previsões por ML</p>
    </div>

  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const API_URL = 'http://localhost:3001'

const LEAGUE_COLORS = [
  { border: 'rgba(59,130,246,1)',   bg: 'rgba(59,130,246,0.15)'  },
  { border: 'rgba(239,68,68,1)',    bg: 'rgba(239,68,68,0.15)'   },
  { border: 'rgba(16,185,129,1)',   bg: 'rgba(16,185,129,0.15)'  },
  { border: 'rgba(245,158,11,1)',   bg: 'rgba(245,158,11,0.15)'  },
  { border: 'rgba(139,92,246,1)',   bg: 'rgba(139,92,246,0.15)'  },
]

// ─── Sub-components ───────────────────────────────────────────────────────────

const ChartBox = {
  name: 'ChartBox',
  props: { title: String },
  template: `
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
      <h3 class="text-gray-900 font-semibold mb-4 text-sm">{{ title }}</h3>
      <div class="relative" style="height:280px"><slot /></div>
    </div>
  `
}

const StatsCard = {
  name: 'StatsCard',
  props: { stat: Object },
  template: `
    <div class="bg-gray-100 rounded-xl border border-gray-200 p-4">
      <p class="text-gray-500 text-xs uppercase tracking-wider mb-3">{{ stat.metric }}</p>
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
        <span class="text-gray-500">Média</span>    <span class="text-gray-900 font-medium text-right">{{ stat.mean }}</span>
        <span class="text-gray-500">Mediana</span>  <span class="text-gray-900 font-medium text-right">{{ stat.median }}</span>
        <span class="text-gray-500">Desvio σ</span> <span class="text-gray-900 font-medium text-right">{{ stat.std }}</span>
        <span class="text-gray-500">Mín / Máx</span><span class="text-gray-900 font-medium text-right">{{ stat.min }} / {{ stat.max }}</span>
        <span class="text-gray-500">Q1 / Q3</span>  <span class="text-gray-900 font-medium text-right">{{ stat.q1 }} / {{ stat.q3 }}</span>
        <span class="text-gray-500">IQR</span>       <span class="text-gray-900 font-medium text-right">{{ stat.iqr }}</span>
      </div>
    </div>
  `
}

const OutlierTable = {
  name: 'OutlierTable',
  props: { items: Array, type: String },
  computed: {
    outliers() { return (this.items || []).filter(i => i.analysis?.is_outlier) }
  },
  methods: {
    badgeCls(dir) {
      if (dir === 'above') return 'bg-emerald-100 text-emerald-700 border border-emerald-300'
      if (dir === 'below') return 'bg-red-100 text-red-700 border border-red-300'
      return 'bg-gray-200 text-gray-700'
    },
    badgeTxt(dir) { return dir === 'above' ? '↑ Acima' : dir === 'below' ? '↓ Abaixo' : 'Normal' },
    scorePct(item) { return ((item.analysis?.outlier_score ?? 0) * 100).toFixed(0) + '%' },
    barCls(item) {
      const s = item.analysis?.outlier_score ?? 0
      return s > 0.75 ? 'bg-red-500' : s > 0.55 ? 'bg-amber-500' : 'bg-gray-400'
    },
  },
  template: `
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-gray-900 font-semibold">⚠️ Outliers Detectados</h3>
        <span class="text-gray-500 text-sm">{{ outliers.length }} de {{ (items||[]).length }}</span>
      </div>
      <div v-if="!outliers.length" class="px-5 py-8 text-center text-gray-500">
        Nenhum outlier significativo detectado nesta análise.
      </div>
      <div v-else class="overflow-x-auto">
        <table v-if="type === 'standings'" class="w-full text-sm">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Pts</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">GF</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">GA</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Z-Score</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Score ML</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Status</th>
              <th class="px-4 py-3 text-left text-gray-500 font-medium">Razão</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in outliers" :key="item.analysis.team_name" class="border-t border-gray-200/50 hover:bg-gray-50">
              <td class="px-4 py-3 text-gray-900 font-medium">{{ item.analysis.team_name }}</td>
              <td class="px-4 py-3 text-center text-gray-900">{{ item.points }}</td>
              <td class="px-4 py-3 text-center text-emerald-600">{{ item.analysis.goals_for }}</td>
              <td class="px-4 py-3 text-center text-red-600">{{ item.analysis.goals_against }}</td>
              <td class="px-4 py-3 text-center text-blue-600">{{ item.analysis.z_score_points }}σ</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div :class="barCls(item)" class="h-1.5 rounded-full" :style="{width: scorePct(item)}"></div>
                  </div>
                  <span class="text-gray-700 text-xs w-8">{{ scorePct(item) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span :class="['px-2 py-0.5 rounded text-xs font-medium', badgeCls(item.analysis.outlier_direction)]">
                  {{ badgeTxt(item.analysis.outlier_direction) }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-700 text-xs max-w-xs">{{ (item.analysis.reasons||[]).join(' · ') }}</td>
            </tr>
          </tbody>
        </table>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-3 text-left text-gray-500 font-medium">Jogador</th>
              <th class="px-4 py-3 text-left text-gray-500 font-medium">Time</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Gols</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Assist</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">G/J</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Z-Score</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Score ML</th>
              <th class="px-4 py-3 text-center text-gray-500 font-medium">Status</th>
              <th class="px-4 py-3 text-left text-gray-500 font-medium">Razão</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in outliers" :key="item.name" class="border-t border-gray-200/50 hover:bg-gray-50">
              <td class="px-4 py-3 text-gray-900 font-medium">{{ item.name }}</td>
              <td class="px-4 py-3 text-gray-700">{{ item.team }}</td>
              <td class="px-4 py-3 text-center text-gray-900 font-bold">{{ item.goals }}</td>
              <td class="px-4 py-3 text-center text-blue-600">{{ item.assists }}</td>
              <td class="px-4 py-3 text-center text-emerald-600">{{ item.goals_per_game }}</td>
              <td class="px-4 py-3 text-center text-blue-600">{{ item.analysis.z_score_goals }}σ</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-gray-200 rounded-full h-1.5">
                    <div :class="barCls(item)" class="h-1.5 rounded-full" :style="{width: scorePct(item)}"></div>
                  </div>
                  <span class="text-gray-700 text-xs w-8">{{ scorePct(item) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span :class="['px-2 py-0.5 rounded text-xs font-medium', badgeCls(item.analysis.outlier_direction)]">
                  {{ badgeTxt(item.analysis.outlier_direction) }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-700 text-xs max-w-xs">{{ (item.analysis.reasons||[]).join(' · ') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
}

const InsightPanel = {
  name: 'InsightPanel',
  props: { insights: Array },
  template: `
    <div v-if="insights && insights.length" class="bg-white rounded-xl border border-blue-200 p-5">
      <h3 class="text-gray-900 font-semibold mb-4">💡 Insights Automáticos</h3>
      <ul class="space-y-3">
        <li v-for="(insight, i) in insights" :key="i" class="flex gap-3 text-gray-700 text-sm leading-relaxed">
          <span class="text-blue-600 font-bold flex-shrink-0 mt-0.5">{{ i + 1 }}.</span>
          <span>{{ insight }}</span>
        </li>
      </ul>
    </div>
  `
}

// ─── Main component ───────────────────────────────────────────────────────────
export default {
  name: 'AnalyticsTab',
  components: { ChartBox, StatsCard, OutlierTable, InsightPanel },

  setup() {
    // ── State ──────────────────────────────────────────────────────────────────
    const leagues        = ref([])
    const selectedLeague = ref('')
    const selectedSeason = ref('')
    const seasons        = ['2024', '2023', '2022', '2021', '2020']

    const activeSubTab  = ref('standings')
    const phaseLoading  = ref(false)
    const compareLoading= ref(false)
    const error         = ref('')

    // Phase 1
    const standingsData = ref(null)
    const scorersData   = ref(null)
    // Phase 2
    const injuriesData    = ref(null)
    const multiligaData   = ref(null)
    const predictionsData = ref(null)
    // Phase 3
    const clustersData = ref(null)
    const mcData       = ref(null)

    // Multi-liga controls
    const selectedLeagues = ref([])
    const multiligaSeason = ref('2024')

    const subTabs = [
      { id: 'standings',   name: 'Classificação', icon: '📊' },
      { id: 'topscorers',  name: 'Artilheiros',   icon: '🎯' },
      { id: 'injuries',    name: 'Lesões',         icon: '🏥' },
      { id: 'multiliga',   name: 'Multi-Liga',     icon: '🌍' },
      { id: 'predictions', name: 'Previsões',      icon: '📈' },
      { id: 'clusters',    name: 'Clusters',       icon: '🔵' },
      { id: 'montecarlo',  name: 'Monte Carlo',    icon: '🎲' },
      { id: 'zonas',       name: 'Zonas RF',       icon: '🏅' },
      { id: 'arquetipos',  name: 'Arquétipos',     icon: '🎭' },
    ]

    const activeAction = computed(() => {
      const map = {
        standings:   { icon: '🔍', label: 'Analisar' },
        topscorers:  { icon: '🔍', label: 'Analisar' },
        injuries:    { icon: '🏥', label: 'Analisar Lesões' },
        predictions: { icon: '📈', label: 'Prever Temporada' },
        zonas:       { icon: '🏅', label: 'Classificar Zonas' },
        arquetipos:  { icon: '🎭', label: 'Classificar Arquétipos' },
        clusters:    { icon: '🔵', label: 'Agrupar Times' },
        montecarlo:  { icon: '🎲', label: 'Simular Temporada' },
      }
      return map[activeSubTab.value] || { icon: '🔍', label: 'Carregar' }
    })

    const hasAnyData = computed(() =>
      standingsData.value || scorersData.value || injuriesData.value ||
      multiligaData.value  || predictionsData.value ||
      clustersData.value   || mcData.value ||
      zoneData.value       || archetypeData.value
    )

    const summaryCards = computed(() => {
      const tab = activeSubTab.value
      if (tab === 'standings' && standingsData.value) {
        const s = standingsData.value.summary
        return [
          { label: 'Times',    value: s.total,    cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500', valCls: 'text-gray-900'      },
          { label: 'Outliers', value: s.outliers,  cls: 'bg-white border-amber-300',   labelCls: 'text-amber-600', valCls: 'text-amber-600'  },
          { label: 'Acima',    value: s.above,     cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'},
          { label: 'Abaixo',   value: s.below,     cls: 'bg-white border-red-300',     labelCls: 'text-red-600',   valCls: 'text-red-600'   },
        ]
      }
      if (tab === 'topscorers' && scorersData.value) {
        const s = scorersData.value.summary
        return [
          { label: 'Jogadores', value: s.total,   cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500', valCls: 'text-gray-900'      },
          { label: 'Outliers',  value: s.outliers, cls: 'bg-white border-amber-300',   labelCls: 'text-amber-600', valCls: 'text-amber-600'  },
          { label: 'Acima',     value: s.above,    cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'},
          { label: 'Abaixo',    value: s.below,    cls: 'bg-white border-red-300',     labelCls: 'text-red-600',   valCls: 'text-red-600'   },
        ]
      }
      if (tab === 'injuries' && injuriesData.value) {
        const s = injuriesData.value.summary
        return [
          { label: 'Lesões',   value: s.total,          cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500',   valCls: 'text-gray-900'      },
          { label: 'Times',    value: s.teams_affected,  cls: 'bg-white border-blue-200',    labelCls: 'text-blue-600',    valCls: 'text-blue-600'   },
          { label: 'Tipos',    value: s.injury_types,   cls: 'bg-white border-violet-300',  labelCls: 'text-violet-600',  valCls: 'text-violet-600' },
          { label: 'Anômalos', value: s.outlier_teams,  cls: 'bg-white border-red-300',     labelCls: 'text-red-600',     valCls: 'text-red-600'    },
        ]
      }
      if (tab === 'multiliga' && multiligaData.value) {
        const s = multiligaData.value.leagues
        const offens = s.reduce((a, b) => b.goals_per_game > a.goals_per_game ? b : a, s[0])
        const balanc = s.reduce((a, b) => b.competitive_balance > a.competitive_balance ? b : a, s[0])
        return [
          { label: 'Ligas',      value: s.length,             cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500',   valCls: 'text-gray-900'      },
          { label: 'Mais gols',  value: offens?.goals_per_game, cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'},
          { label: 'Mais equil.', value: balanc?.competitive_balance, cls: 'bg-white border-blue-200', labelCls: 'text-blue-600', valCls: 'text-blue-600' },
          { label: 'Temporada',  value: multiligaSeason.value,  cls: 'bg-white border-violet-300', labelCls: 'text-violet-600',  valCls: 'text-violet-600' },
        ]
      }
      if (tab === 'predictions' && predictionsData.value) {
        const s = predictionsData.value.summary
        return [
          { label: 'Jogos Total',  value: s.total_games,          cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500', valCls: 'text-gray-900'     },
          { label: 'Sobem',        value: s.risers,               cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'},
          { label: 'Caem',         value: s.fallers,              cls: 'bg-white border-red-300',     labelCls: 'text-red-600',   valCls: 'text-red-600'   },
          { label: 'R² modelo',    value: s.regression_r2,        cls: 'bg-white border-blue-200',    labelCls: 'text-blue-600',  valCls: 'text-blue-600'  },
        ]
      }
      if (tab === 'clusters' && clustersData.value) {
        const d   = clustersData.value
        const dom = d.clusters?.[0]
        return [
          { label: 'Times',     value: d.total_teams,                    cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500',   valCls: 'text-gray-900'                  },
          { label: 'Clusters',  value: d.n_clusters,                     cls: 'bg-white border-blue-200',    labelCls: 'text-blue-600',    valCls: 'text-blue-600'               },
          { label: 'Dominante', value: dom?.name ?? '—',                  cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600 text-sm'    },
          { label: 'Pts/jogo',  value: dom?.centroid?.pts_rate ?? '—',    cls: 'bg-white border-violet-300', labelCls: 'text-violet-600',  valCls: 'text-violet-600'             },
        ]
      }
      if (tab === 'zonas' && zoneData.value) {
        const d = zoneData.value
        return [
          { label: 'Times',      value: d.total_teams,                                  cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500',   valCls: 'text-gray-900'      },
          { label: 'RF Acc.',    value: (d.models.rf_accuracy  * 100).toFixed(0) + '%', cls: 'bg-white border-blue-200',    labelCls: 'text-blue-600',    valCls: 'text-blue-600'   },
          { label: 'LR Acc.',    value: (d.models.lr_accuracy  * 100).toFixed(0) + '%', cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'},
          { label: 'SHAP',       value: d.models.shap_enabled ? 'Ativo' : 'Inativo',    cls: 'bg-white border-violet-300',  labelCls: 'text-violet-600',  valCls: 'text-violet-600 text-sm'},
        ]
      }
      if (tab === 'arquetipos' && archetypeData.value) {
        const d = archetypeData.value
        return [
          { label: 'Jogadores',  value: d.total_players,                                cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500',   valCls: 'text-gray-900'      },
          { label: 'RF Acc.',    value: (d.models.rf_accuracy  * 100).toFixed(0) + '%', cls: 'bg-white border-blue-200',    labelCls: 'text-blue-600',    valCls: 'text-blue-600'   },
          { label: 'LR Acc.',    value: (d.models.lr_accuracy  * 100).toFixed(0) + '%', cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'},
          { label: 'Arquétipos', value: 4,                                               cls: 'bg-white border-violet-300',  labelCls: 'text-violet-600',  valCls: 'text-violet-600' },
        ]
      }
      if (tab === 'montecarlo' && mcData.value) {
        const rs    = [...(mcData.value.results || [])].sort((a, b) => b.championship_prob - a.championship_prob)
        const champ = rs[0]
        const risk  = (mcData.value.results || []).filter(r => r.relegation_prob > 0.1).length
        return [
          { label: 'Simulações',   value: (mcData.value.summary?.n_simulations || 0).toLocaleString('pt-BR'), cls: 'bg-white border-gray-200',      labelCls: 'text-gray-500',   valCls: 'text-gray-900 text-lg'          },
          { label: 'Favorito',     value: champ?.name ?? '—',                                                  cls: 'bg-white border-amber-300',  labelCls: 'text-amber-600',  valCls: 'text-amber-600 text-sm'     },
          { label: 'Prob. Título', value: champ ? (champ.championship_prob * 100).toFixed(1) + '%' : '—',      cls: 'bg-white border-emerald-300', labelCls: 'text-emerald-600', valCls: 'text-emerald-600'            },
          { label: 'Risco Rebai.', value: risk,                                                                cls: 'bg-white border-red-300',     labelCls: 'text-red-600',     valCls: 'text-red-600'                },
        ]
      }
      return null
    })

    // ── State: RF + LR + SHAP ─────────────────────────────────────────────────
    const zoneData          = ref(null)
    const archetypeData     = ref(null)
    const selectedZoneItem  = ref(null)
    const selectedArchItem  = ref(null)

    const zoneColors = ['#f59e0b', '#3b82f6', '#6b7280', '#ef4444']

    const featLabelMap = {
      pts_rate: 'Pts/Jogo', attack_rate: 'Gols Marc./Jogo', defense_rate: 'Gols Sofr./Jogo',
      win_rate: 'Taxa Vitórias', goal_diff_rate: 'Saldo/Jogo',
      goals: 'Gols Totais', assists: 'Assistências', gpg: 'Gols/Jogo', apg: 'Assist./Jogo',
      contribution: 'Contribuição',
    }

    function zoneBadgeCls(zone) {
      return [
        'bg-amber-100 text-amber-700 border border-amber-300',
        'bg-blue-100 text-blue-700 border border-blue-300',
        'bg-gray-100 text-gray-600 border border-gray-300',
        'bg-red-100 text-red-700 border border-red-300',
      ][zone] ?? 'bg-gray-100 text-gray-700'
    }

    function archBadgeCls(arch) {
      return [
        'bg-red-100 text-red-700 border border-red-300',
        'bg-emerald-100 text-emerald-700 border border-emerald-300',
        'bg-blue-100 text-blue-700 border border-blue-300',
        'bg-gray-100 text-gray-600 border border-gray-300',
      ][arch] ?? 'bg-gray-100 text-gray-700'
    }

    // ── Canvas refs ────────────────────────────────────────────────────────────
    const standingsScatterCanvas = ref(null)
    const standingsZScoreCanvas  = ref(null)
    const scorersBubbleCanvas    = ref(null)
    const scorersEffCanvas       = ref(null)
    const injuriesTeamCanvas     = ref(null)
    const injuriesTypeCanvas     = ref(null)
    const multiligaRadarCanvas   = ref(null)
    const multiligaBarsCanvas    = ref(null)
    const predictScatterCanvas   = ref(null)
    const predictBarCanvas       = ref(null)
    const clustersScatterCanvas  = ref(null)
    const clustersBarCanvas      = ref(null)
    const mcChampCanvas          = ref(null)
    const mcPositionsCanvas      = ref(null)
    const zoneFeatCanvas         = ref(null)
    const zoneDistCanvas         = ref(null)
    const zoneShapCanvas         = ref(null)
    const archFeatCanvas         = ref(null)
    const archScatterCanvas      = ref(null)
    const archShapCanvas         = ref(null)

    const charts = {}
    const destroy = (k) => { if (charts[k]) { charts[k].destroy(); delete charts[k] } }
    const destroyAll = () => Object.keys(charts).forEach(destroy)
    onUnmounted(destroyAll)

    // ── Chart helpers ──────────────────────────────────────────────────────────
    const DARK = { grid: 'rgba(156,163,175,0.25)', tick: '#6b7280', title: '#374151' }
    const scales = (xl, yl) => ({
      x: { title: { display: true, text: xl, color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
      y: { title: { display: true, text: yl, color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
    })
    const tip = (bg = '#ffffff') => ({
      backgroundColor: bg, borderColor: '#e5e7eb', borderWidth: 1, titleColor: '#111827', bodyColor: '#6b7280'
    })
    const ptColor  = (isOut) => isOut ? 'rgba(239,68,68,0.85)' : 'rgba(59,130,246,0.75)'
    const ptBorder = (isOut) => isOut ? 'rgba(239,68,68,1)'    : 'rgba(59,130,246,1)'

    // ── Build: Standings scatter ───────────────────────────────────────────────
    function buildStandingsScatter() {
      destroy('stScatter'); const cv = standingsScatterCanvas.value
      if (!cv || !standingsData.value) return
      const pts = standingsData.value.chart_data.scatter
      charts.stScatter = new Chart(cv, {
        type: 'scatter',
        data: { datasets: [{ label: 'Times', data: pts.map(p => ({ x: p.x, y: p.y })),
          backgroundColor: pts.map(p => ptColor(p.is_outlier)),
          borderColor: pts.map(p => ptBorder(p.is_outlier)),
          pointRadius: pts.map(p => p.is_outlier ? 10 : 7), pointHoverRadius: 13 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: {
          title: ctx => pts[ctx[0].dataIndex]?.label ?? '',
          label: ctx => [`Posição: ${ctx.parsed.x}`, `Pontos: ${ctx.parsed.y}`, pts[ctx[0].dataIndex]?.is_outlier ? '⚠️ Outlier' : ''].filter(Boolean)
        }}}, scales: scales('Posição', 'Pontos') }
      })
    }

    // ── Build: Standings Z-Score bar ──────────────────────────────────────────
    function buildStandingsZScore() {
      destroy('stZ'); const cv = standingsZScoreCanvas.value
      if (!cv || !standingsData.value) return
      const zd = standingsData.value.chart_data.z_scores
      const colors = zd.is_outlier.map((o, i) => o ? (zd.values[i] >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)') : 'rgba(100,116,139,0.6)')
      charts.stZ = new Chart(cv, {
        type: 'bar',
        data: { labels: zd.labels, datasets: [{ label: 'Z-Score', data: zd.values, backgroundColor: colors, borderRadius: 3 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `Z-Score: ${ctx.parsed.x}σ` } } },
          scales: {
            x: { title: { display: true, text: 'Z-Score (σ)', color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } }
          }
        }
      })
    }

    // ── Build: Scorers bubble ─────────────────────────────────────────────────
    function buildScorersBubble() {
      destroy('scBubble'); const cv = scorersBubbleCanvas.value
      if (!cv || !scorersData.value) return
      const pts = scorersData.value.chart_data.scatter
      charts.scBubble = new Chart(cv, {
        type: 'bubble',
        data: { datasets: [{ label: 'Jogadores', data: pts.map(p => ({ x: p.x, y: p.y, r: Math.max(5, Math.min(20, p.r)) })),
          backgroundColor: pts.map(p => ptColor(p.is_outlier)),
          borderColor: pts.map(p => ptBorder(p.is_outlier)), borderWidth: 1.5 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: {
          title: ctx => pts[ctx[0].dataIndex]?.label ?? '',
          label: ctx => [`Gols: ${ctx.parsed.x}`, `Assist: ${ctx.parsed.y}`, `Aparições: ${pts[ctx[0].dataIndex]?.appearances}`, pts[ctx[0].dataIndex]?.is_outlier ? '⚠️ Outlier' : ''].filter(Boolean)
        }}}, scales: scales('Gols', 'Assistências') }
      })
    }

    // ── Build: Scorers efficiency bar ─────────────────────────────────────────
    function buildScorersEff() {
      destroy('scEff'); const cv = scorersEffCanvas.value
      if (!cv || !scorersData.value) return
      const ef = scorersData.value.chart_data.efficiency
      const colors = ef.is_outlier.map((o, i) => o ? (ef.values[i] >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)') : 'rgba(100,116,139,0.6)')
      charts.scEff = new Chart(cv, {
        type: 'bar',
        data: { labels: ef.labels, datasets: [{ label: 'G/J', data: ef.values, backgroundColor: colors, borderRadius: 3 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `${ctx.parsed.x} gols/jogo` } } },
          scales: {
            x: { title: { display: true, text: 'Gols por Jogo', color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } }
          }
        }
      })
    }

    // ── Build: Injuries team bar ──────────────────────────────────────────────
    function buildInjuriesTeam() {
      destroy('injTeam'); const cv = injuriesTeamCanvas.value
      if (!cv || !injuriesData.value) return
      const cd = injuriesData.value.chart_data.teams
      const colors = cd.is_outlier.map(o => o ? 'rgba(239,68,68,0.8)' : 'rgba(100,116,139,0.6)')
      charts.injTeam = new Chart(cv, {
        type: 'bar',
        data: { labels: cd.labels, datasets: [{ label: 'Lesões', data: cd.values, backgroundColor: colors, borderRadius: 3 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `${ctx.parsed.x} lesões` } } },
          scales: {
            x: { title: { display: true, text: 'Lesões', color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } }
          }
        }
      })
    }

    // ── Build: Injuries type doughnut ─────────────────────────────────────────
    function buildInjuriesType() {
      destroy('injType'); const cv = injuriesTypeCanvas.value
      if (!cv || !injuriesData.value) return
      const cd = injuriesData.value.chart_data.types
      const palette = ['rgba(59,130,246,0.8)','rgba(239,68,68,0.8)','rgba(16,185,129,0.8)',
        'rgba(245,158,11,0.8)','rgba(139,92,246,0.8)','rgba(236,72,153,0.8)',
        'rgba(20,184,166,0.8)','rgba(251,146,60,0.8)','rgba(163,230,53,0.8)','rgba(148,163,184,0.8)']
      charts.injType = new Chart(cv, {
        type: 'doughnut',
        data: { labels: cd.labels, datasets: [{ data: cd.values, backgroundColor: palette.slice(0, cd.labels.length), borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: {
          legend: { position: 'right', labels: { color: DARK.tick, font: { size: 11 }, boxWidth: 12, padding: 8 } },
          tooltip: { ...tip(), callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } }
        }}
      })
    }

    // ── Build: Multi-liga radar ───────────────────────────────────────────────
    function buildMultiligaRadar() {
      destroy('mlRadar'); const cv = multiligaRadarCanvas.value
      if (!cv || !multiligaData.value) return
      const rd = multiligaData.value.chart_data.radar
      charts.mlRadar = new Chart(cv, {
        type: 'radar',
        data: {
          labels: rd.labels,
          datasets: rd.datasets.map((ds, i) => ({
            label: ds.name, data: ds.values,
            borderColor:     LEAGUE_COLORS[i % LEAGUE_COLORS.length].border,
            backgroundColor: LEAGUE_COLORS[i % LEAGUE_COLORS.length].bg,
            borderWidth: 2, pointRadius: 4,
          }))
        },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: DARK.tick } }, tooltip: { ...tip() } },
          scales: { r: {
            grid: { color: DARK.grid }, angleLines: { color: DARK.grid },
            ticks: { color: DARK.tick, backdropColor: 'transparent', stepSize: 25 },
            pointLabels: { color: DARK.title, font: { size: 11 } },
            min: 0, max: 100,
          }}
        }
      })
    }

    // ── Build: Multi-liga goals bar ───────────────────────────────────────────
    function buildMultiligaBars() {
      destroy('mlBars'); const cv = multiligaBarsCanvas.value
      if (!cv || !multiligaData.value) return
      const bd = multiligaData.value.chart_data.bars
      charts.mlBars = new Chart(cv, {
        type: 'bar',
        data: {
          labels: bd.labels,
          datasets: [
            { label: 'Gols/Jogo', data: bd.goals_per_game, backgroundColor: 'rgba(16,185,129,0.75)', borderRadius: 4 },
            { label: 'Equilíbrio/10', data: bd.competitive_balance.map(v => v / 10), backgroundColor: 'rgba(139,92,246,0.75)', borderRadius: 4 },
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: DARK.tick } }, tooltip: { ...tip() } },
          scales: {
            x: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } }
          }
        }
      })
    }

    // ── Build: Predictions scatter + regression line ───────────────────────────
    function buildPredictScatter() {
      destroy('prScatter'); const cv = predictScatterCanvas.value
      if (!cv || !predictionsData.value) return
      const cd  = predictionsData.value.chart_data
      const pts = cd.scatter
      const rl  = cd.regression_line

      const pColors = pts.map(p =>
        p.overperforming  ? 'rgba(16,185,129,0.85)' :
        p.underperforming ? 'rgba(239,68,68,0.85)'  :
        'rgba(100,116,139,0.75)'
      )

      charts.prScatter = new Chart(cv, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'Times',
              type: 'scatter',
              data: pts.map(p => ({ x: p.x, y: p.y })),
              backgroundColor: pColors,
              borderColor: pColors,
              pointRadius: 8, pointHoverRadius: 12,
            },
            {
              label: 'Curva esperada',
              type: 'line',
              data: rl.x.map((x, i) => ({ x, y: rl.y[i] })),
              borderColor: 'rgba(245,158,11,0.7)',
              borderWidth: 2, borderDash: [6, 3],
              pointRadius: 0, fill: false,
            },
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: DARK.tick } },
            tooltip: { ...tip(), callbacks: {
              title: ctx => ctx[0].datasetIndex === 0 ? (pts[ctx[0].dataIndex]?.label ?? '') : 'Curva de regressão',
              label: ctx => ctx.datasetIndex === 0
                ? [`Posição: ${ctx.parsed.x}`, `Pts: ${ctx.parsed.y}`, `Projetado: ${pts[ctx.dataIndex]?.projected}`,
                   pts[ctx.dataIndex]?.overperforming ? '↑ Acima do esperado' : pts[ctx.dataIndex]?.underperforming ? '↓ Abaixo do esperado' : ''].filter(Boolean)
                : [`Y = ${ctx.parsed.y.toFixed(1)}`]
            }}
          },
          scales: scales('Posição Atual', 'Pontos')
        }
      })
    }

    // ── Build: Predictions projected bar ─────────────────────────────────────
    function buildPredictBar() {
      destroy('prBar'); const cv = predictBarCanvas.value
      if (!cv || !predictionsData.value) return
      const pb = predictionsData.value.chart_data.projected_bar
      const extra = pb.projected.map((p, i) => Math.max(0, p - pb.current[i]))
      charts.prBar = new Chart(cv, {
        type: 'bar',
        data: {
          labels: pb.labels,
          datasets: [
            { label: 'Pts atuais',   data: pb.current, backgroundColor: 'rgba(100,116,139,0.7)', borderRadius: 0 },
            { label: 'Pts proj. (+)', data: extra,      backgroundColor: 'rgba(59,130,246,0.75)', borderRadius: [4,4,0,0] },
          ]
        },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: DARK.tick } },
            tooltip: { ...tip(), mode: 'index', callbacks: {
              footer: items => `Total projetado: ${items.reduce((s, i) => s + i.parsed.x, 0).toFixed(1)}`
            }}
          },
          scales: {
            x: { stacked: true, title: { display: true, text: 'Pontos', color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { stacked: true, ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } }
          }
        }
      })
    }

    // ── Build: Clusters scatter ───────────────────────────────────────────────
    function buildClustersScatter() {
      destroy('clScatter'); const cv = clustersScatterCanvas.value
      if (!cv || !clustersData.value) return
      const pts = clustersData.value.chart_data.scatter
      const CC  = ['rgba(59,130,246,0.85)', 'rgba(16,185,129,0.85)', 'rgba(245,158,11,0.85)', 'rgba(239,68,68,0.85)']
      const CB  = ['rgba(59,130,246,1)',    'rgba(16,185,129,1)',    'rgba(245,158,11,1)',    'rgba(239,68,68,1)'   ]
      charts.clScatter = new Chart(cv, {
        type: 'scatter',
        data: { datasets: [{ label: 'Times',
          data:            pts.map(p => ({ x: p.x, y: p.y })),
          backgroundColor: pts.map(p => CC[p.cluster_id] ?? 'rgba(148,163,184,0.8)'),
          borderColor:     pts.map(p => CB[p.cluster_id] ?? 'rgba(148,163,184,1)'),
          pointRadius: 9, pointHoverRadius: 13,
        }] },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: {
            title: ctx => pts[ctx[0].dataIndex]?.label ?? '',
            label: ctx => [`Cluster: ${pts[ctx[0].dataIndex]?.cluster_name}`, `Ataque: ${ctx.parsed.x} gols/j`, `Defesa: ${ctx.parsed.y} gols/j`],
          }}},
          scales: scales('Gols Marcados/Jogo (Ataque)', 'Gols Sofridos/Jogo (Defesa)'),
        }
      })
    }

    // ── Build: Clusters bar ───────────────────────────────────────────────────
    function buildClustersBar() {
      destroy('clBar'); const cv = clustersBarCanvas.value
      if (!cv || !clustersData.value) return
      const bd = clustersData.value.chart_data.bar
      charts.clBar = new Chart(cv, {
        type: 'bar',
        data: { labels: bd.labels, datasets: [{ label: 'Times por Cluster', data: bd.values,
          backgroundColor: bd.colors.map(c => c + 'cc'), borderColor: bd.colors,
          borderWidth: 2, borderRadius: 6,
        }] },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `${ctx.parsed.y} time(s)` } } },
          scales: {
            x: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, stepSize: 1 }, grid: { color: DARK.grid } },
          },
        }
      })
    }

    // ── Build: Monte Carlo championship ──────────────────────────────────────
    function buildMCChampionship() {
      destroy('mcChamp'); const cv = mcChampCanvas.value
      if (!cv || !mcData.value) return
      const cd = mcData.value.chart_data.championship
      charts.mcChamp = new Chart(cv, {
        type: 'bar',
        data: { labels: cd.labels, datasets: [{ label: 'Prob. Título %', data: cd.probs,
          backgroundColor: cd.probs.map(v => v > 50 ? 'rgba(245,158,11,0.85)' : v > 10 ? 'rgba(59,130,246,0.7)' : 'rgba(100,116,139,0.5)'),
          borderRadius: 4,
        }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `${ctx.parsed.x.toFixed(1)}%` } } },
          scales: {
            x: { title: { display: true, text: 'Probabilidade (%)', color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } },
          },
        }
      })
    }

    // ── Build: Monte Carlo positions ──────────────────────────────────────────
    function buildMCPositions() {
      destroy('mcPos'); const cv = mcPositionsCanvas.value
      if (!cv || !mcData.value) return
      const cd = mcData.value.chart_data.positions
      charts.mcPos = new Chart(cv, {
        type: 'bar',
        data: { labels: cd.labels, datasets: [
          { label: 'Top-4 %',        data: cd.top4,       backgroundColor: 'rgba(16,185,129,0.7)', borderRadius: [4,4,0,0] },
          { label: 'Rebaixamento %', data: cd.relegation, backgroundColor: 'rgba(239,68,68,0.7)',  borderRadius: [4,4,0,0] },
        ] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: DARK.tick } }, tooltip: { ...tip() } },
          scales: {
            x: { title: { display: true, text: 'Probabilidade (%)', color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } },
          },
        }
      })
    }

    // ── Build: Zone feature importance ────────────────────────────────────────
    function buildZoneFeat() {
      destroy('zoneFeat'); const cv = zoneFeatCanvas.value
      if (!cv || !zoneData.value) return
      const fi = zoneData.value.chart_data.feature_importance
      charts.zoneFeat = new Chart(cv, {
        type: 'bar',
        data: { labels: fi.labels, datasets: [
          { label: 'RF Importance', data: fi.rf_values,   backgroundColor: 'rgba(59,130,246,0.75)',  borderRadius: 3 },
          { label: 'SHAP Global',   data: fi.shap_values, backgroundColor: 'rgba(16,185,129,0.75)', borderRadius: 3 },
        ]},
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: DARK.tick } }, tooltip: { ...tip() } },
          scales: {
            x: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } },
          },
        }
      })
    }

    // ── Build: Zone distribution doughnut ─────────────────────────────────────
    function buildZoneDist() {
      destroy('zoneDist'); const cv = zoneDistCanvas.value
      if (!cv || !zoneData.value) return
      const zd = zoneData.value.chart_data.zone_distribution
      charts.zoneDist = new Chart(cv, {
        type: 'doughnut',
        data: { labels: zd.labels, datasets: [{ data: zd.counts, backgroundColor: zd.colors.map(c => c + 'cc'), borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: {
            legend: { position: 'right', labels: { color: DARK.tick, font: { size: 11 }, boxWidth: 12, padding: 8 } },
            tooltip: { ...tip(), callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} times` } },
          }
        }
      })
    }

    // ── Build: Zone SHAP per team ──────────────────────────────────────────────
    function buildZoneShap() {
      destroy('zoneShap'); const cv = zoneShapCanvas.value
      if (!cv || !selectedZoneItem.value?.shap) return
      const shap  = selectedZoneItem.value.shap
      const feats = Object.keys(shap)
      if (!feats.length) return
      const vals   = feats.map(f => shap[f])
      const labels = feats.map(f => featLabelMap[f] || f)
      const colors = vals.map(v => v >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)')
      charts.zoneShap = new Chart(cv, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'SHAP', data: vals, backgroundColor: colors, borderRadius: 3 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `SHAP: ${ctx.parsed.x >= 0 ? '+' : ''}${ctx.parsed.x.toFixed(4)}` } } },
          scales: {
            x: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 11 } }, grid: { display: false } },
          }
        }
      })
    }

    // ── Build: Archetype feature importance ───────────────────────────────────
    function buildArchFeat() {
      destroy('archFeat'); const cv = archFeatCanvas.value
      if (!cv || !archetypeData.value) return
      const fi = archetypeData.value.chart_data.feature_importance
      charts.archFeat = new Chart(cv, {
        type: 'bar',
        data: { labels: fi.labels, datasets: [
          { label: 'RF Importance', data: fi.rf_values,   backgroundColor: 'rgba(59,130,246,0.75)',  borderRadius: 3 },
          { label: 'SHAP Global',   data: fi.shap_values, backgroundColor: 'rgba(16,185,129,0.75)', borderRadius: 3 },
        ]},
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: DARK.tick } }, tooltip: { ...tip() } },
          scales: {
            x: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 10 } }, grid: { display: false } },
          },
        }
      })
    }

    // ── Build: Archetype scatter gpg vs apg ───────────────────────────────────
    function buildArchScatter() {
      destroy('archScatter'); const cv = archScatterCanvas.value
      if (!cv || !archetypeData.value) return
      const pts = archetypeData.value.chart_data.scatter
      const AC  = ['rgba(239,68,68,0.85)', 'rgba(16,185,129,0.85)', 'rgba(59,130,246,0.85)', 'rgba(107,114,128,0.75)']
      charts.archScatter = new Chart(cv, {
        type: 'scatter',
        data: { datasets: [{ label: 'Jogadores',
          data:            pts.map(p => ({ x: p.x, y: p.y })),
          backgroundColor: pts.map(p => AC[p.archetype] ?? AC[3]),
          borderColor:     pts.map(p => AC[p.archetype] ?? AC[3]),
          pointRadius: 8, pointHoverRadius: 12,
        }] },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: {
            title: ctx => pts[ctx[0].dataIndex]?.label ?? '',
            label: ctx => [`Arquétipo: ${pts[ctx[0].dataIndex]?.archetype_label}`, `Gols/J: ${ctx.parsed.x}`, `Assist./J: ${ctx.parsed.y}`],
          }}},
          scales: scales('Gols/Jogo', 'Assistências/Jogo'),
        }
      })
    }

    // ── Build: Archetype SHAP per player ──────────────────────────────────────
    function buildArchShap() {
      destroy('archShap'); const cv = archShapCanvas.value
      if (!cv || !selectedArchItem.value?.shap) return
      const shap  = selectedArchItem.value.shap
      const feats = Object.keys(shap)
      if (!feats.length) return
      const vals   = feats.map(f => shap[f])
      const labels = feats.map(f => featLabelMap[f] || f)
      const colors = vals.map(v => v >= 0 ? 'rgba(16,185,129,0.8)' : 'rgba(239,68,68,0.8)')
      charts.archShap = new Chart(cv, {
        type: 'bar',
        data: { labels, datasets: [{ label: 'SHAP', data: vals, backgroundColor: colors, borderRadius: 3 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false }, tooltip: { ...tip(), callbacks: { label: ctx => `SHAP: ${ctx.parsed.x >= 0 ? '+' : ''}${ctx.parsed.x.toFixed(4)}` } } },
          scales: {
            x: { ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
            y: { ticks: { color: DARK.tick, font: { size: 11 } }, grid: { display: false } },
          }
        }
      })
    }

    // ── Chart dispatch per sub-tab ────────────────────────────────────────────
    const rebuildChartsForTab = {
      standings:   () => { buildStandingsScatter(); buildStandingsZScore() },
      topscorers:  () => { buildScorersBubble();    buildScorersEff() },
      injuries:    () => { buildInjuriesTeam();      buildInjuriesType() },
      multiliga:   () => { buildMultiligaRadar();    buildMultiligaBars() },
      predictions: () => { buildPredictScatter();    buildPredictBar() },
      clusters:    () => { buildClustersScatter();   buildClustersBar() },
      montecarlo:  () => { buildMCChampionship();    buildMCPositions() },
      zonas:       () => { buildZoneFeat();          buildZoneDist() },
      arquetipos:  () => { buildArchFeat();          buildArchScatter() },
    }

    // ── Sub-tab switch ────────────────────────────────────────────────────────
    function switchSubTab(tab) {
      activeSubTab.value = tab
      nextTick(() => {
        const hasData = {
          standings:   standingsData.value,
          topscorers:  scorersData.value,
          injuries:    injuriesData.value,
          multiliga:   multiligaData.value,
          predictions: predictionsData.value,
          clusters:    clustersData.value,
          montecarlo:  mcData.value,
          zonas:       zoneData.value,
          arquetipos:  archetypeData.value,
        }
        if (hasData[tab]) rebuildChartsForTab[tab]?.()
      })
    }

    // ── Main action (depends on active tab) ───────────────────────────────────
    async function handleMainAction() {
      if (!selectedLeague.value || !selectedSeason.value) return
      error.value = ''
      phaseLoading.value = true
      try {
        if (activeSubTab.value === 'standings' || activeSubTab.value === 'topscorers') {
          await runPhase1()
        } else if (activeSubTab.value === 'injuries') {
          await runInjuries()
        } else if (activeSubTab.value === 'predictions') {
          await runPredictions()
        } else if (activeSubTab.value === 'clusters') {
          await runClusters()
        } else if (activeSubTab.value === 'montecarlo') {
          await runMonteCarlo()
        } else if (activeSubTab.value === 'zonas') {
          await runZones()
        } else if (activeSubTab.value === 'arquetipos') {
          await runArchetypes()
        }
      } finally {
        phaseLoading.value = false
      }
    }

    // ── Phase 1: standings + scorers ──────────────────────────────────────────
    async function runPhase1() {
      standingsData.value = null
      scorersData.value   = null
      destroyAll()
      const [sd, td] = await Promise.allSettled([
        api(`/analysis/standings/${selectedLeague.value}/${selectedSeason.value}`),
        api(`/analysis/topscorers/${selectedLeague.value}/${selectedSeason.value}`),
      ])
      if (sd.status === 'fulfilled' && !sd.value?.error) standingsData.value = sd.value
      else appendError(sd)
      if (td.status === 'fulfilled' && !td.value?.error) scorersData.value = td.value
      else appendError(td)

      await nextTick()
      rebuildChartsForTab[activeSubTab.value]?.()
    }

    // ── Phase 2: injuries ─────────────────────────────────────────────────────
    async function runInjuries() {
      injuriesData.value = null
      const result = await api(`/analysis/injuries/${selectedLeague.value}/${selectedSeason.value}`)
      if (result?.error) { error.value = result.error; return }
      injuriesData.value = result
      await nextTick()
      buildInjuriesTeam(); buildInjuriesType()
    }

    // ── Phase 2: compare leagues ──────────────────────────────────────────────
    async function runCompare() {
      if (selectedLeagues.value.length < 2) return
      error.value    = ''
      compareLoading.value = true
      multiligaData.value  = null
      destroyAll()
      try {
        const leaguesPayload = selectedLeagues.value.map(id => {
          const found = leagues.value.find(l => l.id === id)
          return { id, name: found?.name ?? `Liga ${id}`, season: multiligaSeason.value }
        })
        const result = await fetch(`${API_URL}/analysis/compare-leagues`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ leagues: leaguesPayload }),
        }).then(r => r.json())

        if (result?.error) { error.value = result.error; return }
        multiligaData.value = result
        await nextTick()
        buildMultiligaRadar(); buildMultiligaBars()
      } catch (e) {
        error.value = `Erro: ${e.message}`
      } finally {
        compareLoading.value = false
      }
    }

    // ── Phase 2: predictions ──────────────────────────────────────────────────
    async function runPredictions() {
      predictionsData.value = null
      const result = await api(`/analysis/predictions/${selectedLeague.value}/${selectedSeason.value}`)
      if (result?.error) { error.value = result.error; return }
      predictionsData.value = result
      await nextTick()
      buildPredictScatter(); buildPredictBar()
    }

    // ── Phase 3: clusters ─────────────────────────────────────────────────────
    async function runClusters() {
      clustersData.value = null
      const result = await api(`/analysis/clusters/${selectedLeague.value}/${selectedSeason.value}`)
      if (result?.error) { error.value = result.error; return }
      clustersData.value = result
      await nextTick()
      buildClustersScatter(); buildClustersBar()
    }

    // ── Phase 3: monte carlo ──────────────────────────────────────────────────
    async function runMonteCarlo() {
      mcData.value = null
      const result = await api(`/analysis/monte-carlo/${selectedLeague.value}/${selectedSeason.value}`)
      if (result?.error) { error.value = result.error; return }
      mcData.value = result
      await nextTick()
      buildMCChampionship(); buildMCPositions()
    }

    // ── RF + LR + SHAP: zones ─────────────────────────────────────────────────
    async function runZones() {
      zoneData.value = null; selectedZoneItem.value = null
      const result = await api(`/analysis/zone-classifier/${selectedLeague.value}/${selectedSeason.value}`)
      if (result?.error) { error.value = result.error; return }
      zoneData.value = result
      await nextTick()
      buildZoneFeat(); buildZoneDist()
    }

    function selectZoneItem(item) {
      selectedZoneItem.value = item
      nextTick(buildZoneShap)
    }

    // ── RF + LR + SHAP: archetypes ────────────────────────────────────────────
    async function runArchetypes() {
      archetypeData.value = null; selectedArchItem.value = null
      const result = await api(`/analysis/player-archetypes/${selectedLeague.value}/${selectedSeason.value}`)
      if (result?.error) { error.value = result.error; return }
      archetypeData.value = result
      await nextTick()
      buildArchFeat(); buildArchScatter()
    }

    function selectArchItem(item) {
      selectedArchItem.value = item
      nextTick(buildArchShap)
    }

    // ── Utils ─────────────────────────────────────────────────────────────────
    async function api(endpoint) {
      const r = await fetch(`${API_URL}${endpoint}`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      return r.json()
    }
    function appendError(settled) {
      const msg = settled.value?.error || settled.reason?.message || 'Erro desconhecido'
      error.value = error.value ? error.value + ' | ' + msg : msg
    }
    async function loadLeagues() {
      try {
        const d = await api('/leagues')
        leagues.value = d.leagues || []
      } catch { leagues.value = [] }
    }

    loadLeagues()

    return {
      leagues, selectedLeague, selectedSeason, seasons,
      activeSubTab, subTabs, activeAction,
      phaseLoading, compareLoading, error,
      standingsData, scorersData, injuriesData, multiligaData, predictionsData,
      selectedLeagues, multiligaSeason,
      hasAnyData, summaryCards,
      switchSubTab, handleMainAction, runCompare,
      standingsScatterCanvas, standingsZScoreCanvas,
      scorersBubbleCanvas,    scorersEffCanvas,
      injuriesTeamCanvas,     injuriesTypeCanvas,
      multiligaRadarCanvas,   multiligaBarsCanvas,
      predictScatterCanvas,   predictBarCanvas,
      clustersScatterCanvas,  clustersBarCanvas,
      mcChampCanvas,          mcPositionsCanvas,
      clustersData, mcData, runClusters, runMonteCarlo,
      zoneData, archetypeData, selectedZoneItem, selectedArchItem,
      zoneFeatCanvas, zoneDistCanvas, zoneShapCanvas,
      archFeatCanvas, archScatterCanvas, archShapCanvas,
      runZones, runArchetypes, selectZoneItem, selectArchItem,
      zoneBadgeCls, archBadgeCls, zoneColors, featLabelMap,
    }
  }
}
</script>

<style scoped>
.empty-state {
  @apply bg-white rounded-xl border border-dashed border-gray-300 p-14 text-center text-gray-500;
}
.empty-state strong {
  @apply text-gray-700;
}
</style>
