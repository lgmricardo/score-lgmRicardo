<template>
  <div class="space-y-6">

    <!-- HEADER -->
    <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
      <div class="flex items-center gap-3 mb-5">
        <span class="text-3xl">🧠</span>
        <div>
          <h2 class="text-2xl font-bold text-white">Análise ML</h2>
          <p class="text-slate-400 text-sm">Isolation Forest · Z-Score · LOF · Regressão Linear</p>
        </div>
      </div>

      <!-- Seletores principais (compartilhados exceto multi-liga) -->
      <div v-if="activeSubTab !== 'multiliga'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-slate-400 text-xs uppercase tracking-wider mb-1">Liga</label>
          <select v-model="selectedLeague" class="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-blue-500 focus:outline-none">
            <option value="">Selecione uma liga</option>
            <option v-for="l in leagues" :key="l.id" :value="l.id">{{ l.name }} ({{ l.country }})</option>
          </select>
        </div>
        <div>
          <label class="block text-slate-400 text-xs uppercase tracking-wider mb-1">Temporada</label>
          <select v-model="selectedSeason" class="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-blue-500 focus:outline-none">
            <option value="">Selecione</option>
            <option v-for="y in seasons" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="handleMainAction"
            :disabled="!selectedLeague || !selectedSeason || phaseLoading"
            class="w-full px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition flex items-center justify-center gap-2"
          >
            <span v-if="phaseLoading" class="animate-spin">⏳</span>
            <span v-else>{{ activeAction.icon }}</span>
            {{ phaseLoading ? 'Carregando...' : activeAction.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- ERRO -->
    <div v-if="error" class="bg-red-900/20 border border-red-700 text-red-400 px-4 py-3 rounded-lg">
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
          'px-4 py-2 rounded-lg font-medium transition text-sm',
          activeSubTab === tab.id
            ? 'bg-blue-600 text-white'
            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
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
        <p class="text-xs text-slate-500 mt-2">Disponibilidade depende da cobertura da API para a liga/temporada.</p>
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
        <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="text-white font-semibold">Times com mais lesões</h3>
            <span class="text-slate-400 text-sm">{{ injuriesData.summary.teams_affected }} times afetados</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-700/50">
                <tr>
                  <th class="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Lesões</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Z-Score</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="t in injuriesData.by_team.slice(0, 15)"
                  :key="t.team"
                  class="border-t border-slate-700/50 hover:bg-slate-700/30"
                >
                  <td class="px-4 py-3 text-white font-medium">{{ t.team }}</td>
                  <td class="px-4 py-3 text-center text-white">{{ t.count }}</td>
                  <td class="px-4 py-3 text-center text-blue-300">{{ t.z_score }}σ</td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="t.is_outlier" class="px-2 py-0.5 rounded text-xs font-medium bg-red-900/50 text-red-400 border border-red-700">
                      ⚠️ Anômalo
                    </span>
                    <span v-else class="px-2 py-0.5 rounded text-xs text-slate-400">Normal</span>
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
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6">
        <h3 class="text-white font-semibold mb-4">Selecione as ligas para comparar (2–5)</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-slate-400 text-xs uppercase tracking-wider mb-2">Ligas</label>
            <div class="space-y-2 max-h-52 overflow-y-auto pr-1">
              <label
                v-for="l in leagues"
                :key="l.id"
                class="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-700 cursor-pointer"
                :class="{ 'bg-slate-700/60': selectedLeagues.includes(l.id) }"
              >
                <input
                  type="checkbox"
                  :value="l.id"
                  v-model="selectedLeagues"
                  :disabled="!selectedLeagues.includes(l.id) && selectedLeagues.length >= 5"
                  class="w-4 h-4 accent-blue-500"
                />
                <span class="text-white text-sm">{{ l.name }}</span>
                <span class="text-slate-400 text-xs ml-auto">{{ l.country }}</span>
              </label>
            </div>
            <p class="text-slate-500 text-xs mt-2">{{ selectedLeagues.length }} / 5 selecionadas</p>
          </div>
          <div class="flex flex-col gap-4">
            <div>
              <label class="block text-slate-400 text-xs uppercase tracking-wider mb-1">Temporada</label>
              <select v-model="multiligaSeason" class="w-full px-4 py-2 bg-slate-700 text-white rounded-lg border border-slate-600 focus:border-blue-500 focus:outline-none">
                <option v-for="y in seasons" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <button
              @click="runCompare"
              :disabled="selectedLeagues.length < 2 || compareLoading"
              class="w-full px-6 py-3 bg-violet-600 hover:bg-violet-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition flex items-center justify-center gap-2 mt-auto"
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
        <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-700">
            <h3 class="text-white font-semibold">Comparativo Detalhado</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-700/50">
                <tr>
                  <th class="px-4 py-3 text-left text-slate-400 font-medium">Liga</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Times</th>
                  <th class="px-4 py-3 text-left text-slate-400 font-medium">Líder</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Pts Líder</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Média Pts</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Gols/Jogo</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Equilíbrio</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="lg in multiligaData.leagues"
                  :key="lg.id"
                  class="border-t border-slate-700/50 hover:bg-slate-700/30"
                >
                  <td class="px-4 py-3 text-white font-semibold">{{ lg.name }}</td>
                  <td class="px-4 py-3 text-center text-slate-300">{{ lg.teams }}</td>
                  <td class="px-4 py-3 text-slate-300">{{ lg.leader }}</td>
                  <td class="px-4 py-3 text-center font-bold text-white">{{ lg.leader_pts }}</td>
                  <td class="px-4 py-3 text-center text-blue-300">{{ lg.avg_pts }}</td>
                  <td class="px-4 py-3 text-center text-emerald-400">{{ lg.goals_per_game }}</td>
                  <td class="px-4 py-3 text-center">
                    <div class="flex items-center gap-2">
                      <div class="flex-1 bg-slate-600 rounded-full h-1.5">
                        <div class="bg-violet-500 h-1.5 rounded-full" :style="{width: lg.competitive_balance + '%'}"></div>
                      </div>
                      <span class="text-slate-300 text-xs w-8">{{ lg.competitive_balance }}</span>
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
        <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="text-white font-semibold">Previsão de Classificação Final</h3>
            <span class="text-slate-400 text-sm">
              R²={{ predictionsData.summary.regression_r2 }} · ±{{ predictionsData.summary.residual_std }} pts
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-700/50">
                <tr>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Pos. Atual</th>
                  <th class="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Pts Atual</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Pts Proj.</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Intervalo</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Pts/Jogo</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Pos. Final</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Var.</th>
                  <th class="px-4 py-3 text-center text-slate-400 font-medium">Forma</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in predictionsData.predictions"
                  :key="p.name"
                  class="border-t border-slate-700/50 hover:bg-slate-700/30"
                >
                  <td class="px-4 py-3 text-center text-slate-300 font-bold">{{ p.current_rank }}</td>
                  <td class="px-4 py-3 text-white font-medium">{{ p.name }}</td>
                  <td class="px-4 py-3 text-center text-white">{{ p.current_pts }}</td>
                  <td class="px-4 py-3 text-center font-bold text-blue-300">{{ p.projected_pts }}</td>
                  <td class="px-4 py-3 text-center text-slate-400 text-xs">
                    {{ p.proj_pts_low }}–{{ p.proj_pts_high }}
                  </td>
                  <td class="px-4 py-3 text-center text-slate-300">{{ p.points_rate }}</td>
                  <td class="px-4 py-3 text-center font-bold text-white">{{ p.predicted_rank }}</td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="p.rank_change > 0" class="text-emerald-400 font-semibold">↑{{ p.rank_change }}</span>
                    <span v-else-if="p.rank_change < 0" class="text-red-400 font-semibold">↓{{ Math.abs(p.rank_change) }}</span>
                    <span v-else class="text-slate-500">—</span>
                  </td>
                  <td class="px-4 py-3 text-center">
                    <span v-if="p.overperforming" class="px-2 py-0.5 rounded text-xs bg-emerald-900/50 text-emerald-400 border border-emerald-700">Acima</span>
                    <span v-else-if="p.underperforming" class="px-2 py-0.5 rounded text-xs bg-red-900/50 text-red-400 border border-red-700">Abaixo</span>
                    <span v-else class="text-slate-500 text-xs">—</span>
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
          <div v-for="c in clustersData.clusters" :key="c.id" class="bg-slate-800 rounded-xl border border-slate-700 p-4">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-3 h-3 rounded-full flex-shrink-0" :style="{ backgroundColor: c.color }"></div>
              <h4 class="text-white font-semibold text-sm truncate">{{ c.name }}</h4>
              <span class="ml-auto text-slate-400 text-xs flex-shrink-0">{{ c.size }} times</span>
            </div>
            <div class="flex flex-wrap gap-1 mb-3">
              <span v-for="t in c.teams" :key="t" class="px-1.5 py-0.5 rounded text-xs bg-slate-700 text-slate-300">{{ t }}</span>
            </div>
            <div class="grid grid-cols-2 gap-x-2 gap-y-1 text-xs border-t border-slate-700 pt-3">
              <span class="text-slate-400">Ataque/j</span><span class="text-right text-white">{{ c.centroid.attack_rate }}</span>
              <span class="text-slate-400">Defesa/j</span><span class="text-right text-white">{{ c.centroid.defense_rate }}</span>
              <span class="text-slate-400">Pts/j</span><span class="text-right font-medium text-blue-300">{{ c.centroid.pts_rate }}</span>
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
        <p class="text-xs text-slate-500 mt-2">10.000 simulações baseadas em taxas de V/E/D de cada time.</p>
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
        <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div class="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="text-white font-semibold">Probabilidades por Time</h3>
            <span class="text-slate-400 text-sm">
              {{ mcData.summary?.season_complete ? 'Temporada encerrada' : (mcData.summary?.n_simulations || 0).toLocaleString('pt-BR') + ' simulações' }}
            </span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="bg-slate-700/50">
                <tr>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Pos</th>
                  <th class="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Pts</th>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Rest.</th>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Título%</th>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Top-4%</th>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Rebai.%</th>
                  <th class="px-3 py-3 text-center text-slate-400 font-medium">Pts Final</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="r in mcData.results" :key="r.name" class="border-t border-slate-700/50 hover:bg-slate-700/30">
                  <td class="px-3 py-2 text-center font-bold text-slate-300">{{ r.current_rank }}</td>
                  <td class="px-4 py-2 text-white font-medium">{{ r.name }}</td>
                  <td class="px-3 py-2 text-center text-white">{{ r.current_pts }}</td>
                  <td class="px-3 py-2 text-center text-slate-400">{{ r.games_remaining }}</td>
                  <td class="px-3 py-2 text-center">
                    <span :class="r.championship_prob > 0.5 ? 'text-yellow-400 font-bold' : r.championship_prob > 0.1 ? 'text-amber-400' : 'text-slate-500'">
                      {{ (r.championship_prob * 100).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center">
                    <span :class="r.top4_prob > 0.5 ? 'text-emerald-400' : r.top4_prob > 0.2 ? 'text-emerald-500/70' : 'text-slate-500'">
                      {{ (r.top4_prob * 100).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center">
                    <span :class="r.relegation_prob > 0.3 ? 'text-red-400 font-semibold' : r.relegation_prob > 0.05 ? 'text-orange-400' : 'text-slate-500'">
                      {{ (r.relegation_prob * 100).toFixed(1) }}%
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center text-blue-300">{{ r.avg_final_pts }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <InsightPanel :insights="mcData.insights" />
      </template>
    </div>

    <!-- PLACEHOLDER INICIAL -->
    <div v-if="!hasAnyData && !phaseLoading && !compareLoading" class="bg-slate-800 rounded-xl border border-dashed border-slate-600 p-16 text-center">
      <div class="text-5xl mb-4">🧠</div>
      <p class="text-slate-300 text-lg font-medium">Selecione uma liga e temporada para iniciar</p>
      <p class="text-slate-500 mt-2 text-sm">Fase 1: Outliers | Fase 2: Lesões · Multi-Liga · Previsões por ML</p>
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
    <div class="bg-slate-800 rounded-xl border border-slate-700 p-5">
      <h3 class="text-white font-semibold mb-4 text-sm">{{ title }}</h3>
      <div class="relative" style="height:280px"><slot /></div>
    </div>
  `
}

const StatsCard = {
  name: 'StatsCard',
  props: { stat: Object },
  template: `
    <div class="bg-slate-700/60 rounded-xl border border-slate-600 p-4">
      <p class="text-slate-400 text-xs uppercase tracking-wider mb-3">{{ stat.metric }}</p>
      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
        <span class="text-slate-400">Média</span>    <span class="text-white font-medium text-right">{{ stat.mean }}</span>
        <span class="text-slate-400">Mediana</span>  <span class="text-white font-medium text-right">{{ stat.median }}</span>
        <span class="text-slate-400">Desvio σ</span> <span class="text-white font-medium text-right">{{ stat.std }}</span>
        <span class="text-slate-400">Mín / Máx</span><span class="text-white font-medium text-right">{{ stat.min }} / {{ stat.max }}</span>
        <span class="text-slate-400">Q1 / Q3</span>  <span class="text-white font-medium text-right">{{ stat.q1 }} / {{ stat.q3 }}</span>
        <span class="text-slate-400">IQR</span>       <span class="text-white font-medium text-right">{{ stat.iqr }}</span>
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
      if (dir === 'above') return 'bg-emerald-900/50 text-emerald-400 border border-emerald-700'
      if (dir === 'below') return 'bg-red-900/50 text-red-400 border border-red-700'
      return 'bg-slate-600 text-slate-300'
    },
    badgeTxt(dir) { return dir === 'above' ? '↑ Acima' : dir === 'below' ? '↓ Abaixo' : 'Normal' },
    scorePct(item) { return ((item.analysis?.outlier_score ?? 0) * 100).toFixed(0) + '%' },
    barCls(item) {
      const s = item.analysis?.outlier_score ?? 0
      return s > 0.75 ? 'bg-red-500' : s > 0.55 ? 'bg-amber-500' : 'bg-slate-500'
    },
  },
  template: `
    <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-700 flex items-center justify-between">
        <h3 class="text-white font-semibold">⚠️ Outliers Detectados</h3>
        <span class="text-slate-400 text-sm">{{ outliers.length }} de {{ (items||[]).length }}</span>
      </div>
      <div v-if="!outliers.length" class="px-5 py-8 text-center text-slate-400">
        Nenhum outlier significativo detectado nesta análise.
      </div>
      <div v-else class="overflow-x-auto">
        <table v-if="type === 'standings'" class="w-full text-sm">
          <thead class="bg-slate-700/50">
            <tr>
              <th class="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Pts</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">GF</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">GA</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Z-Score</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Score ML</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Status</th>
              <th class="px-4 py-3 text-left text-slate-400 font-medium">Razão</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in outliers" :key="item.analysis.team_name" class="border-t border-slate-700/50 hover:bg-slate-700/30">
              <td class="px-4 py-3 text-white font-medium">{{ item.analysis.team_name }}</td>
              <td class="px-4 py-3 text-center text-white">{{ item.points }}</td>
              <td class="px-4 py-3 text-center text-emerald-400">{{ item.analysis.goals_for }}</td>
              <td class="px-4 py-3 text-center text-red-400">{{ item.analysis.goals_against }}</td>
              <td class="px-4 py-3 text-center text-blue-300">{{ item.analysis.z_score_points }}σ</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-slate-600 rounded-full h-1.5">
                    <div :class="barCls(item)" class="h-1.5 rounded-full" :style="{width: scorePct(item)}"></div>
                  </div>
                  <span class="text-slate-300 text-xs w-8">{{ scorePct(item) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span :class="['px-2 py-0.5 rounded text-xs font-medium', badgeCls(item.analysis.outlier_direction)]">
                  {{ badgeTxt(item.analysis.outlier_direction) }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-300 text-xs max-w-xs">{{ (item.analysis.reasons||[]).join(' · ') }}</td>
            </tr>
          </tbody>
        </table>
        <table v-else class="w-full text-sm">
          <thead class="bg-slate-700/50">
            <tr>
              <th class="px-4 py-3 text-left text-slate-400 font-medium">Jogador</th>
              <th class="px-4 py-3 text-left text-slate-400 font-medium">Time</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Gols</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Assist</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">G/J</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Z-Score</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Score ML</th>
              <th class="px-4 py-3 text-center text-slate-400 font-medium">Status</th>
              <th class="px-4 py-3 text-left text-slate-400 font-medium">Razão</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in outliers" :key="item.name" class="border-t border-slate-700/50 hover:bg-slate-700/30">
              <td class="px-4 py-3 text-white font-medium">{{ item.name }}</td>
              <td class="px-4 py-3 text-slate-300">{{ item.team }}</td>
              <td class="px-4 py-3 text-center text-white font-bold">{{ item.goals }}</td>
              <td class="px-4 py-3 text-center text-blue-300">{{ item.assists }}</td>
              <td class="px-4 py-3 text-center text-emerald-400">{{ item.goals_per_game }}</td>
              <td class="px-4 py-3 text-center text-blue-300">{{ item.analysis.z_score_goals }}σ</td>
              <td class="px-4 py-3 text-center">
                <div class="flex items-center gap-2">
                  <div class="flex-1 bg-slate-600 rounded-full h-1.5">
                    <div :class="barCls(item)" class="h-1.5 rounded-full" :style="{width: scorePct(item)}"></div>
                  </div>
                  <span class="text-slate-300 text-xs w-8">{{ scorePct(item) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center">
                <span :class="['px-2 py-0.5 rounded text-xs font-medium', badgeCls(item.analysis.outlier_direction)]">
                  {{ badgeTxt(item.analysis.outlier_direction) }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-300 text-xs max-w-xs">{{ (item.analysis.reasons||[]).join(' · ') }}</td>
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
    <div v-if="insights && insights.length" class="bg-slate-800 rounded-xl border border-blue-900/40 p-5">
      <h3 class="text-white font-semibold mb-4">💡 Insights Automáticos</h3>
      <ul class="space-y-3">
        <li v-for="(insight, i) in insights" :key="i" class="flex gap-3 text-slate-300 text-sm leading-relaxed">
          <span class="text-blue-400 font-bold flex-shrink-0 mt-0.5">{{ i + 1 }}.</span>
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
    ]

    const activeAction = computed(() => {
      const map = {
        standings:   { icon: '🔍', label: 'Analisar' },
        topscorers:  { icon: '🔍', label: 'Analisar' },
        injuries:    { icon: '🏥', label: 'Analisar Lesões' },
        predictions: { icon: '📈', label: 'Prever Temporada' },
        clusters:    { icon: '🔵', label: 'Agrupar Times' },
        montecarlo:  { icon: '🎲', label: 'Simular Temporada' },
      }
      return map[activeSubTab.value] || { icon: '🔍', label: 'Carregar' }
    })

    const hasAnyData = computed(() =>
      standingsData.value || scorersData.value || injuriesData.value ||
      multiligaData.value  || predictionsData.value ||
      clustersData.value   || mcData.value
    )

    const summaryCards = computed(() => {
      const tab = activeSubTab.value
      if (tab === 'standings' && standingsData.value) {
        const s = standingsData.value.summary
        return [
          { label: 'Times',    value: s.total,    cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400', valCls: 'text-white'      },
          { label: 'Outliers', value: s.outliers,  cls: 'bg-slate-800 border-amber-800/40',   labelCls: 'text-amber-400', valCls: 'text-amber-400'  },
          { label: 'Acima',    value: s.above,     cls: 'bg-slate-800 border-emerald-800/40', labelCls: 'text-emerald-400', valCls: 'text-emerald-400'},
          { label: 'Abaixo',   value: s.below,     cls: 'bg-slate-800 border-red-800/40',     labelCls: 'text-red-400',   valCls: 'text-red-400'   },
        ]
      }
      if (tab === 'topscorers' && scorersData.value) {
        const s = scorersData.value.summary
        return [
          { label: 'Jogadores', value: s.total,   cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400', valCls: 'text-white'      },
          { label: 'Outliers',  value: s.outliers, cls: 'bg-slate-800 border-amber-800/40',   labelCls: 'text-amber-400', valCls: 'text-amber-400'  },
          { label: 'Acima',     value: s.above,    cls: 'bg-slate-800 border-emerald-800/40', labelCls: 'text-emerald-400', valCls: 'text-emerald-400'},
          { label: 'Abaixo',    value: s.below,    cls: 'bg-slate-800 border-red-800/40',     labelCls: 'text-red-400',   valCls: 'text-red-400'   },
        ]
      }
      if (tab === 'injuries' && injuriesData.value) {
        const s = injuriesData.value.summary
        return [
          { label: 'Lesões',   value: s.total,          cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400',   valCls: 'text-white'      },
          { label: 'Times',    value: s.teams_affected,  cls: 'bg-slate-800 border-blue-800/40',    labelCls: 'text-blue-400',    valCls: 'text-blue-400'   },
          { label: 'Tipos',    value: s.injury_types,   cls: 'bg-slate-800 border-violet-800/40',  labelCls: 'text-violet-400',  valCls: 'text-violet-400' },
          { label: 'Anômalos', value: s.outlier_teams,  cls: 'bg-slate-800 border-red-800/40',     labelCls: 'text-red-400',     valCls: 'text-red-400'    },
        ]
      }
      if (tab === 'multiliga' && multiligaData.value) {
        const s = multiligaData.value.leagues
        const offens = s.reduce((a, b) => b.goals_per_game > a.goals_per_game ? b : a, s[0])
        const balanc = s.reduce((a, b) => b.competitive_balance > a.competitive_balance ? b : a, s[0])
        return [
          { label: 'Ligas',      value: s.length,             cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400',   valCls: 'text-white'      },
          { label: 'Mais gols',  value: offens?.goals_per_game, cls: 'bg-slate-800 border-emerald-800/40', labelCls: 'text-emerald-400', valCls: 'text-emerald-400'},
          { label: 'Mais equil.', value: balanc?.competitive_balance, cls: 'bg-slate-800 border-blue-800/40', labelCls: 'text-blue-400', valCls: 'text-blue-400' },
          { label: 'Temporada',  value: multiligaSeason.value,  cls: 'bg-slate-800 border-violet-800/40', labelCls: 'text-violet-400',  valCls: 'text-violet-400' },
        ]
      }
      if (tab === 'predictions' && predictionsData.value) {
        const s = predictionsData.value.summary
        return [
          { label: 'Jogos Total',  value: s.total_games,          cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400', valCls: 'text-white'     },
          { label: 'Sobem',        value: s.risers,               cls: 'bg-slate-800 border-emerald-800/40', labelCls: 'text-emerald-400', valCls: 'text-emerald-400'},
          { label: 'Caem',         value: s.fallers,              cls: 'bg-slate-800 border-red-800/40',     labelCls: 'text-red-400',   valCls: 'text-red-400'   },
          { label: 'R² modelo',    value: s.regression_r2,        cls: 'bg-slate-800 border-blue-800/40',    labelCls: 'text-blue-400',  valCls: 'text-blue-400'  },
        ]
      }
      if (tab === 'clusters' && clustersData.value) {
        const d   = clustersData.value
        const dom = d.clusters?.[0]
        return [
          { label: 'Times',     value: d.total_teams,                    cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400',   valCls: 'text-white'                  },
          { label: 'Clusters',  value: d.n_clusters,                     cls: 'bg-slate-800 border-blue-800/40',    labelCls: 'text-blue-400',    valCls: 'text-blue-400'               },
          { label: 'Dominante', value: dom?.name ?? '—',                  cls: 'bg-slate-800 border-emerald-800/40', labelCls: 'text-emerald-400', valCls: 'text-emerald-400 text-sm'    },
          { label: 'Pts/jogo',  value: dom?.centroid?.pts_rate ?? '—',    cls: 'bg-slate-800 border-violet-800/40', labelCls: 'text-violet-400',  valCls: 'text-violet-400'             },
        ]
      }
      if (tab === 'montecarlo' && mcData.value) {
        const rs    = [...(mcData.value.results || [])].sort((a, b) => b.championship_prob - a.championship_prob)
        const champ = rs[0]
        const risk  = (mcData.value.results || []).filter(r => r.relegation_prob > 0.1).length
        return [
          { label: 'Simulações',   value: (mcData.value.summary?.n_simulations || 0).toLocaleString('pt-BR'), cls: 'bg-slate-800 border-slate-700',      labelCls: 'text-slate-400',   valCls: 'text-white text-lg'          },
          { label: 'Favorito',     value: champ?.name ?? '—',                                                  cls: 'bg-slate-800 border-yellow-800/40',  labelCls: 'text-yellow-400',  valCls: 'text-yellow-400 text-sm'     },
          { label: 'Prob. Título', value: champ ? (champ.championship_prob * 100).toFixed(1) + '%' : '—',      cls: 'bg-slate-800 border-emerald-800/40', labelCls: 'text-emerald-400', valCls: 'text-emerald-400'            },
          { label: 'Risco Rebai.', value: risk,                                                                cls: 'bg-slate-800 border-red-800/40',     labelCls: 'text-red-400',     valCls: 'text-red-400'                },
        ]
      }
      return null
    })

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

    const charts = {}
    const destroy = (k) => { if (charts[k]) { charts[k].destroy(); delete charts[k] } }
    const destroyAll = () => Object.keys(charts).forEach(destroy)
    onUnmounted(destroyAll)

    // ── Chart helpers ──────────────────────────────────────────────────────────
    const DARK = { grid: 'rgba(148,163,184,0.1)', tick: '#94a3b8', title: '#cbd5e1' }
    const scales = (xl, yl) => ({
      x: { title: { display: true, text: xl, color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
      y: { title: { display: true, text: yl, color: DARK.title }, ticks: { color: DARK.tick }, grid: { color: DARK.grid } },
    })
    const tip = (bg = '#1e293b') => ({
      backgroundColor: bg, borderColor: '#334155', borderWidth: 1, titleColor: '#f1f5f9', bodyColor: '#94a3b8'
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

    // ── Chart dispatch per sub-tab ────────────────────────────────────────────
    const rebuildChartsForTab = {
      standings:   () => { buildStandingsScatter(); buildStandingsZScore() },
      topscorers:  () => { buildScorersBubble();    buildScorersEff() },
      injuries:    () => { buildInjuriesTeam();      buildInjuriesType() },
      multiliga:   () => { buildMultiligaRadar();    buildMultiligaBars() },
      predictions: () => { buildPredictScatter();    buildPredictBar() },
      clusters:    () => { buildClustersScatter();   buildClustersBar() },
      montecarlo:  () => { buildMCChampionship();    buildMCPositions() },
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
    }
  }
}
</script>

<style scoped>
.empty-state {
  @apply bg-slate-800 rounded-xl border border-dashed border-slate-600 p-14 text-center text-slate-400;
}
.empty-state strong {
  @apply text-slate-200;
}
</style>
