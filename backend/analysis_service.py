"""
Football Analytics Service
Outlier detection using Isolation Forest, Z-Score, and Local Outlier Factor.
"""

import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple


# ============================================================================
# OUTLIER DETECTOR
# ============================================================================

class OutlierDetector:
    def __init__(self, contamination: float = 0.15):
        self.contamination = contamination

    def zscore(self, values: np.ndarray, threshold: float = 2.0) -> Tuple[np.ndarray, np.ndarray]:
        if len(values) < 2:
            return np.zeros(len(values)), np.zeros(len(values), dtype=bool)
        z = np.abs(stats.zscore(values, nan_policy='omit'))
        z = np.nan_to_num(z, nan=0.0)
        return z, z > threshold

    def iqr_bounds(self, values: np.ndarray) -> Tuple[float, float, float, float]:
        q1, q3 = float(np.percentile(values, 25)), float(np.percentile(values, 75))
        iqr = q3 - q1
        return q1, q3, q1 - 1.5 * iqr, q3 + 1.5 * iqr

    def isolation_forest(self, X: np.ndarray) -> np.ndarray:
        n = len(X)
        if n < 5:
            return np.zeros(n)
        scaler = StandardScaler()
        X_s = scaler.fit_transform(X)
        clf = IsolationForest(contamination=self.contamination, n_estimators=100, random_state=42)
        clf.fit(X_s)
        raw = clf.score_samples(X_s)
        mn, mx = raw.min(), raw.max()
        if mx == mn:
            return np.zeros(n)
        return 1.0 - (raw - mn) / (mx - mn)

    def lof(self, X: np.ndarray) -> np.ndarray:
        n = len(X)
        if n < 5:
            return np.zeros(n)
        k = min(5, n - 1)
        scaler = StandardScaler()
        X_s = scaler.fit_transform(X)
        clf = LocalOutlierFactor(n_neighbors=k, contamination=self.contamination)
        clf.fit_predict(X_s)
        raw = -clf.negative_outlier_factor_
        mn, mx = raw.min(), raw.max()
        if mx == mn:
            return np.zeros(n)
        return (raw - mn) / (mx - mn)

    def combined(self, X: np.ndarray) -> np.ndarray:
        return (self.isolation_forest(X) + self.lof(X)) / 2.0


# ============================================================================
# STATISTICAL ANALYZER
# ============================================================================

class StatisticalAnalyzer:
    def describe(self, values: np.ndarray, name: str = "") -> Dict:
        v = values[~np.isnan(values)]
        if len(v) == 0:
            return {"metric": name}
        q1, median, q3 = np.percentile(v, [25, 50, 75])
        iqr = q3 - q1
        return {
            "metric": name,
            "count": int(len(v)),
            "mean":   round(float(np.mean(v)), 2),
            "median": round(float(median), 2),
            "std":    round(float(np.std(v)), 2),
            "min":    round(float(np.min(v)), 2),
            "max":    round(float(np.max(v)), 2),
            "q1":     round(float(q1), 2),
            "q3":     round(float(q3), 2),
            "iqr":    round(float(iqr), 2),
            "lower_fence": round(float(q1 - 1.5 * iqr), 2),
            "upper_fence": round(float(q3 + 1.5 * iqr), 2),
        }


# ============================================================================
# STANDINGS ANALYSIS
# ============================================================================

def analyze_standings(standings: List[Dict]) -> Dict:
    if not standings or len(standings) < 3:
        return {"error": "Dados insuficientes (mínimo 3 times)"}

    detector = OutlierDetector(contamination=0.15)
    analyzer = StatisticalAnalyzer()

    names, pts, gf, ga, gd, wins, played_list = [], [], [], [], [], [], []

    for s in standings:
        team = s.get("team", {})
        all_s = s.get("all", {})
        goals = all_s.get("goals", {}) if isinstance(all_s, dict) else {}

        names.append(team.get("name", "?") if isinstance(team, dict) else str(team))
        p = float(s.get("points", 0) or 0)
        g_f = float(goals.get("for", 0) or 0)
        g_a = float(goals.get("against", 0) or 0)
        g_d = float(s.get("goalsDiff", 0) or (g_f - g_a))
        w = float(all_s.get("win", 0) or 0) if isinstance(all_s, dict) else 0.0
        pl = float(all_s.get("played", 1) or 1) if isinstance(all_s, dict) else 1.0

        pts.append(p); gf.append(g_f); ga.append(g_a)
        gd.append(g_d); wins.append(w); played_list.append(pl)

    pts_a  = np.array(pts)
    gf_a   = np.array(gf)
    ga_a   = np.array(ga)
    gd_a   = np.array(gd)
    pl_a   = np.array(played_list)
    wr_a   = np.where(pl_a > 0, wins / pl_a * 100, 0.0)

    X = np.column_stack([pts_a, gf_a, ga_a, gd_a, wr_a])
    combined_s = detector.combined(X)
    if_scores  = detector.isolation_forest(X)
    lof_scores = detector.lof(X)

    pts_z, pts_z_flag = detector.zscore(pts_a)
    gf_z,  gf_z_flag  = detector.zscore(gf_a)
    ga_z,  ga_z_flag  = detector.zscore(ga_a)

    _, _, pts_lo, pts_hi = detector.iqr_bounds(pts_a)
    _, _, gf_lo,  gf_hi  = detector.iqr_bounds(gf_a)
    _, _, ga_lo,  ga_hi  = detector.iqr_bounds(ga_a)

    is_outlier = (combined_s > 0.55) | pts_z_flag | gf_z_flag | ga_z_flag

    items = []
    for i, s in enumerate(standings):
        mean_pts = float(np.mean(pts_a))
        direction = "normal"
        if pts_a[i] > pts_hi or gd_a[i] > float(np.percentile(gd_a, 75)) + float(np.std(gd_a)):
            direction = "above"
        elif pts_a[i] < pts_lo or gd_a[i] < float(np.percentile(gd_a, 25)) - float(np.std(gd_a)):
            direction = "below"
        elif bool(is_outlier[i]):
            direction = "above" if pts_a[i] > mean_pts else "below"

        reasons = []
        if pts_a[i] > pts_hi:
            reasons.append(f"{int(pts_a[i])} pts acima do IQR (fence={int(pts_hi)})")
        elif pts_a[i] < pts_lo:
            reasons.append(f"{int(pts_a[i])} pts abaixo do IQR (fence={int(pts_lo)})")
        if gf_a[i] > gf_hi:
            reasons.append(f"{int(gf_a[i])} gols marcados (alto)")
        if ga_a[i] > ga_hi:
            reasons.append(f"{int(ga_a[i])} gols sofridos (alto)")
        if pts_z[i] > 2.0:
            reasons.append(f"Z-score pontos: {pts_z[i]:.1f}σ")

        items.append({
            **s,
            "analysis": {
                "team_name":            names[i],
                "is_outlier":           bool(is_outlier[i]),
                "outlier_score":        round(float(combined_s[i]), 3),
                "outlier_direction":    direction,
                "isolation_score":      round(float(if_scores[i]), 3),
                "lof_score":            round(float(lof_scores[i]), 3),
                "z_score_points":       round(float(pts_z[i]), 2),
                "z_score_goals_for":    round(float(gf_z[i]), 2),
                "z_score_goals_against":round(float(ga_z[i]), 2),
                "win_rate":             round(float(wr_a[i]), 1),
                "goals_for":            int(gf_a[i]),
                "goals_against":        int(ga_a[i]),
                "goals_diff":           int(gd_a[i]),
                "reasons":              reasons,
            }
        })

    items_by_score = sorted(items, key=lambda x: x["analysis"]["outlier_score"], reverse=True)
    outliers = [t for t in items if t["analysis"]["is_outlier"]]

    statistics = {
        "pontos":       analyzer.describe(pts_a, "Pontos"),
        "gols_marcados":analyzer.describe(gf_a,  "Gols Marcados"),
        "gols_sofridos":analyzer.describe(ga_a,  "Gols Sofridos"),
        "saldo_gols":   analyzer.describe(gd_a,  "Saldo de Gols"),
        "aproveitamento":analyzer.describe(wr_a, "Aproveitamento %"),
    }

    return {
        "summary": {
            "total":   len(items),
            "outliers":len(outliers),
            "above":   len([t for t in outliers if t["analysis"]["outlier_direction"] == "above"]),
            "below":   len([t for t in outliers if t["analysis"]["outlier_direction"] == "below"]),
        },
        "items":      items_by_score,
        "statistics": statistics,
        "insights":   _standings_insights(items, outliers, pts_a, gf_a, ga_a, gd_a),
        "chart_data": {
            "scatter": [
                {
                    "x":          s.get("rank", i + 1),
                    "y":          int(pts_a[i]),
                    "label":      names[i],
                    "is_outlier": items[i]["analysis"]["is_outlier"],
                    "score":      items[i]["analysis"]["outlier_score"],
                }
                for i, s in enumerate(standings)
            ],
            "z_scores": {
                "labels":     names,
                "values":     [round(float(pts_z[i]), 2) for i in range(len(names))],
                "is_outlier": [bool(is_outlier[i]) for i in range(len(names))],
            },
        },
    }


def _standings_insights(items, outliers, pts, gf, ga, gd) -> List[str]:
    insights = []
    mean_pts = float(np.mean(pts))

    leader = max(items, key=lambda x: x.get("points", 0) or 0)
    lname  = leader["analysis"]["team_name"]
    lpts   = leader.get("points", 0) or 0
    pct    = ((lpts - mean_pts) / mean_pts * 100) if mean_pts > 0 else 0
    tag    = "Forte candidato ao título." if leader["analysis"]["is_outlier"] else "Desempenho destaque da liga."
    insights.append(f"{lname} lidera com {lpts} pts — {pct:.0f}% acima da média ({mean_pts:.1f}). {tag}")

    if len(pts) > 3:
        corr_gf = float(np.corrcoef(gf, pts)[0, 1])
        corr_ga = float(np.corrcoef(ga, pts)[0, 1])
        if abs(corr_gf) > 0.6:
            insights.append(
                f"Correlação forte ({corr_gf:.2f}) entre gols marcados e pontos — "
                "times que atacam bem conquistam mais pontos."
            )
        if abs(corr_ga) > 0.6:
            dir_ga = "negativa" if corr_ga < 0 else "positiva"
            insights.append(
                f"Correlação {dir_ga} ({corr_ga:.2f}) entre gols sofridos e pontos — "
                "defesa sólida é fundamental para o sucesso."
            )

    above = [t for t in outliers if t["analysis"]["outlier_direction"] == "above"]
    below = [t for t in outliers if t["analysis"]["outlier_direction"] == "below"]

    if above:
        ns = ", ".join(t["analysis"]["team_name"] for t in above[:2])
        insights.append(f"{len(above)} time(s) com desempenho anômalo acima da média: {ns}.")
    if below:
        ns = ", ".join(t["analysis"]["team_name"] for t in below[:2])
        insights.append(
            f"{len(below)} time(s) em situação crítica abaixo da curva: {ns}. "
            "Risco de rebaixamento ou crise de desempenho."
        )

    insights.append(
        f"{len(outliers)} de {len(items)} times identificados como outliers "
        f"(Isolation Forest + Z-Score + LOF combinados)."
    )
    return insights


# ============================================================================
# TOPSCORERS ANALYSIS
# ============================================================================

def analyze_topscorers(scorers: List[Dict]) -> Dict:
    if not scorers or len(scorers) < 3:
        return {"error": "Dados insuficientes (mínimo 3 jogadores)"}

    detector = OutlierDetector(contamination=0.15)
    analyzer = StatisticalAnalyzer()

    names, teams, goals_l, assists_l, apps_l = [], [], [], [], []

    for s in scorers:
        player = s.get("player", {})
        stat   = s.get("statistics", [{}])[0] if s.get("statistics") else {}
        g_stat = stat.get("goals", {})
        gm_stat= stat.get("games", {})
        t_stat = stat.get("team", {})

        names.append(player.get("name", "?") if isinstance(player, dict) else str(player))
        teams.append(t_stat.get("name", "?") if isinstance(t_stat, dict) else str(t_stat))
        goals_l.append(float(g_stat.get("total", 0) or 0))
        assists_l.append(float(g_stat.get("assists", 0) or 0))
        apps_l.append(float(gm_stat.get("appearences", 0) or 0))

    goals_a   = np.array(goals_l)
    assists_a = np.array(assists_l)
    apps_a    = np.array(apps_l)
    gpg_a     = np.where(apps_a > 0, goals_a / apps_a, 0.0)
    apg_a     = np.where(apps_a > 0, assists_a / apps_a, 0.0)
    contrib_a = goals_a + assists_a

    X = np.column_stack([goals_a, assists_a, gpg_a, apg_a])
    combined_s = detector.combined(X)
    if_scores  = detector.isolation_forest(X)
    lof_scores = detector.lof(X)

    goals_z,   goals_z_flag   = detector.zscore(goals_a)
    assists_z, _               = detector.zscore(assists_a)
    gpg_z,     gpg_z_flag      = detector.zscore(gpg_a)

    _, _, goals_lo, goals_hi = detector.iqr_bounds(goals_a)
    _, _, gpg_lo,   gpg_hi   = detector.iqr_bounds(gpg_a)

    is_outlier = (combined_s > 0.55) | goals_z_flag | gpg_z_flag

    items = []
    for i in range(len(scorers)):
        mean_goals = float(np.mean(goals_a))
        direction  = "normal"
        if goals_a[i] > goals_hi or gpg_a[i] > gpg_hi:
            direction = "above"
        elif goals_a[i] < goals_lo:
            direction = "below"
        elif bool(is_outlier[i]):
            direction = "above" if goals_a[i] > mean_goals else "below"

        reasons = []
        if goals_a[i] > goals_hi:
            reasons.append(f"{int(goals_a[i])} gols acima do IQR (fence={int(goals_hi)})")
        if gpg_a[i] > gpg_hi:
            reasons.append(f"{gpg_a[i]:.2f} gols/jogo — eficiência alta")
        if goals_z[i] > 2.0:
            reasons.append(f"Z-score gols: {goals_z[i]:.1f}σ")
        if assists_a[i] > float(np.percentile(assists_a, 75)) + 1.5 * float(np.std(assists_a)):
            reasons.append(f"{int(assists_a[i])} assistências (alto)")

        items.append({
            "rank":             i + 1,
            "name":             names[i],
            "team":             teams[i],
            "goals":            int(goals_a[i]),
            "assists":          int(assists_a[i]),
            "appearances":      int(apps_a[i]),
            "goals_per_game":   round(float(gpg_a[i]), 3),
            "assists_per_game": round(float(apg_a[i]), 3),
            "contribution":     int(contrib_a[i]),
            "analysis": {
                "is_outlier":       bool(is_outlier[i]),
                "outlier_score":    round(float(combined_s[i]), 3),
                "outlier_direction":direction,
                "isolation_score":  round(float(if_scores[i]), 3),
                "lof_score":        round(float(lof_scores[i]), 3),
                "z_score_goals":    round(float(goals_z[i]), 2),
                "z_score_assists":  round(float(assists_z[i]), 2),
                "z_score_gpg":      round(float(gpg_z[i]), 2),
                "reasons":          reasons,
            },
        })

    items_by_score = sorted(items, key=lambda x: x["analysis"]["outlier_score"], reverse=True)
    outliers = [p for p in items if p["analysis"]["is_outlier"]]

    statistics = {
        "gols":         analyzer.describe(goals_a,   "Gols"),
        "assistencias": analyzer.describe(assists_a,  "Assistências"),
        "aparicoes":    analyzer.describe(apps_a,     "Aparições"),
        "gols_por_jogo":analyzer.describe(gpg_a,     "Gols por Jogo"),
        "contribuicao": analyzer.describe(contrib_a,  "Contribuição"),
    }

    return {
        "summary": {
            "total":   len(items),
            "outliers":len(outliers),
            "above":   len([p for p in outliers if p["analysis"]["outlier_direction"] == "above"]),
            "below":   len([p for p in outliers if p["analysis"]["outlier_direction"] == "below"]),
        },
        "items":      items_by_score,
        "statistics": statistics,
        "insights":   _scorers_insights(items, outliers, goals_a, gpg_a, assists_a),
        "chart_data": {
            "scatter": [
                {
                    "x":          int(goals_a[i]),
                    "y":          int(assists_a[i]),
                    "r":          max(6, int(apps_a[i] / 5)),
                    "label":      names[i],
                    "is_outlier": items[i]["analysis"]["is_outlier"],
                    "score":      items[i]["analysis"]["outlier_score"],
                    "appearances":int(apps_a[i]),
                }
                for i in range(len(items))
            ],
            "efficiency": {
                "labels":     names,
                "values":     [round(float(gpg_a[i]), 3) for i in range(len(names))],
                "is_outlier": [bool(is_outlier[i]) for i in range(len(names))],
            },
        },
    }


def _scorers_insights(items, outliers, goals, gpg, assists) -> List[str]:
    insights = []
    mean_goals = float(np.mean(goals))

    top = max(items, key=lambda x: x["goals"])
    pct = ((top["goals"] - mean_goals) / mean_goals * 100) if mean_goals > 0 else 0
    insights.append(
        f"{top['name']} lidera com {top['goals']} gols — {pct:.0f}% acima da média ({mean_goals:.1f}). "
        f"Taxa de {top['goals_per_game']:.2f} gols/jogo."
    )

    eff = [p for p in outliers if any("eficiência" in r.lower() for r in p["analysis"]["reasons"])]
    if eff:
        p = eff[0]
        insights.append(
            f"{p['name']} tem eficiência excepcional: {p['goals_per_game']:.2f} gols/jogo "
            f"em {p['appearances']} aparições. Jogador excepcional."
        )

    if len(goals) > 3:
        corr = float(np.corrcoef(goals, assists)[0, 1])
        if not np.isnan(corr) and abs(corr) > 0.4:
            insights.append(
                f"Correlação {corr:.2f} entre gols e assistências — "
                "artilheiros também criam jogadas para o time."
            )

    insights.append(
        f"{len(outliers)} de {len(items)} jogadores identificados como outliers. "
        f"Média: {mean_goals:.1f} gols, desvio padrão: {float(np.std(goals)):.1f}."
    )
    return insights


# ============================================================================
# INJURIES ANALYSIS
# ============================================================================

def analyze_injuries(injuries: List[Dict]) -> Dict:
    if not injuries:
        return {"error": "Nenhuma lesão encontrada para esta liga/temporada"}

    team_counts: Dict[str, int] = {}
    type_counts: Dict[str, int] = {}
    items = []

    for inj in injuries:
        player  = inj.get("player", {})
        team    = inj.get("team", {})
        fixture = inj.get("fixture", {})

        p_name = player.get("name", "?") if isinstance(player, dict) else str(player)
        t_name = team.get("name", "?")   if isinstance(team, dict) else str(team)
        reason = (player.get("reason") if isinstance(player, dict) else None) or "Não especificado"

        team_counts[t_name] = team_counts.get(t_name, 0) + 1
        type_counts[reason] = type_counts.get(reason, 0) + 1

        items.append({
            "player":       p_name,
            "team":         t_name,
            "reason":       reason,
            "fixture_date": fixture.get("date", "") if isinstance(fixture, dict) else "",
        })

    teams_sorted = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)
    types_sorted = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

    counts_arr = np.array([c for _, c in teams_sorted], dtype=float)
    by_team = []
    outlier_teams: List[str] = []

    if len(counts_arr) >= 3:
        detector = OutlierDetector(contamination=0.15)
        z, z_flag = detector.zscore(counts_arr)
        _, _, _, hi = detector.iqr_bounds(counts_arr)
        is_out = z_flag | (counts_arr > hi)
        for i, (name, count) in enumerate(teams_sorted):
            if bool(is_out[i]):
                outlier_teams.append(name)
            by_team.append({
                "team":       name,
                "count":      int(counts_arr[i]),
                "is_outlier": bool(is_out[i]),
                "z_score":    round(float(z[i]), 2),
            })
    else:
        for name, count in teams_sorted:
            by_team.append({"team": name, "count": count, "is_outlier": False, "z_score": 0.0})

    total = len(injuries)
    avg   = float(np.mean(counts_arr)) if len(counts_arr) > 0 else 0.0

    insights: List[str] = []
    if teams_sorted:
        m = teams_sorted[0]
        insights.append(
            f"{m[0]} é o time com mais lesões: {m[1]} registros "
            f"({(m[1]/total*100):.0f}% do total da liga)."
        )
    if types_sorted:
        top_t, top_c = types_sorted[0]
        insights.append(
            f"Tipo mais comum: '{top_t}' com {top_c} casos ({(top_c/total*100):.0f}% das lesões)."
        )
    if outlier_teams:
        insights.append(
            f"{len(outlier_teams)} time(s) com taxa de lesões anômala detectada: "
            f"{', '.join(outlier_teams[:3])}."
        )
    insights.append(
        f"Total de {total} lesões em {len(team_counts)} times — média de {avg:.1f} lesões por time."
    )

    return {
        "summary": {
            "total":          total,
            "teams_affected": len(team_counts),
            "injury_types":   len(type_counts),
            "outlier_teams":  len(outlier_teams),
        },
        "by_team":  by_team,
        "by_type":  [{"reason": r, "count": c} for r, c in types_sorted],
        "items":    items,
        "insights": insights,
        "chart_data": {
            "teams": {
                "labels":     [b["team"]       for b in by_team],
                "values":     [b["count"]      for b in by_team],
                "is_outlier": [b["is_outlier"] for b in by_team],
            },
            "types": {
                "labels": [t[0] for t in types_sorted[:10]],
                "values": [t[1] for t in types_sorted[:10]],
            },
        },
    }


# ============================================================================
# MULTI-LEAGUE COMPARISON
# ============================================================================

def compare_leagues(leagues_data: List[Dict]) -> Dict:
    """leagues_data: [{"id": 39, "name": "Premier League", "season": "2024", "standings": [...]}]"""
    if len(leagues_data) < 2:
        return {"error": "Selecione pelo menos 2 ligas para comparar"}

    league_stats = []

    for lg in leagues_data:
        standings = lg.get("standings", [])
        if not standings:
            continue

        all_s   = [s.get("all", {}) for s in standings]
        pts_arr = np.array([float(s.get("points", 0) or 0) for s in standings])
        gf_arr  = np.array([float((a.get("goals", {}) or {}).get("for",      0) or 0) for a in all_s])
        ga_arr  = np.array([float((a.get("goals", {}) or {}).get("against",  0) or 0) for a in all_s])
        pl_arr  = np.array([float(a.get("played", 38) or 38)                          for a in all_s])

        n = len(standings)
        leader_pts = float(np.max(pts_arr))
        avg_pts    = float(np.mean(pts_arr))
        pts_std    = float(np.std(pts_arr))
        balance    = max(0.0, 100.0 - (pts_std / max(leader_pts, 1) * 100))

        total_gf      = float(np.sum(gf_arr))
        total_played  = float(np.sum(pl_arr)) / 2.0
        gpg           = total_gf / max(total_played, 1)

        team_names = []
        for s in standings:
            t = s.get("team", {})
            team_names.append(t.get("name", "?") if isinstance(t, dict) else str(t))

        leader_idx  = int(np.argmax(pts_arr))
        leader_name = team_names[leader_idx] if leader_idx < len(team_names) else "?"

        league_stats.append({
            "id":                  lg.get("id"),
            "name":                lg.get("name", "?"),
            "season":              lg.get("season", ""),
            "teams":               n,
            "leader":              leader_name,
            "leader_pts":          round(leader_pts, 0),
            "avg_pts":             round(avg_pts, 1),
            "pts_std":             round(pts_std, 1),
            "competitive_balance": round(balance, 1),
            "goals_per_game":      round(gpg, 2),
            "total_goals":         int(total_gf),
            "avg_goals_for":       round(float(np.mean(gf_arr)), 1),
            "avg_goals_against":   round(float(np.mean(ga_arr)), 1),
        })

    if len(league_stats) < 2:
        return {"error": "Dados insuficientes — verifique as ligas selecionadas"}

    # Normalize metrics 0-100 for radar
    metrics = ["leader_pts", "avg_pts", "goals_per_game", "competitive_balance"]
    radar_norm: Dict[str, List[float]] = {}
    for m in metrics:
        vals = [lg[m] for lg in league_stats]
        mn, mx = min(vals), max(vals)
        radar_norm[m] = [round((v - mn) / (mx - mn) * 100, 1) if mx != mn else 50.0 for v in vals]

    insights: List[str] = []
    most_goals  = max(league_stats, key=lambda x: x["goals_per_game"])
    fewest_goals= min(league_stats, key=lambda x: x["goals_per_game"])
    insights.append(
        f"{most_goals['name']} é a liga mais ofensiva: {most_goals['goals_per_game']} gols/jogo. "
        f"{fewest_goals['name']} é a mais defensiva: {fewest_goals['goals_per_game']} gols/jogo."
    )
    most_bal  = max(league_stats, key=lambda x: x["competitive_balance"])
    least_bal = min(league_stats, key=lambda x: x["competitive_balance"])
    insights.append(
        f"Liga mais equilibrada: {most_bal['name']} (índice {most_bal['competitive_balance']}). "
        f"Mais dominada por um time: {least_bal['name']} (índice {least_bal['competitive_balance']})."
    )
    strongest = max(league_stats, key=lambda x: x["leader_pts"])
    insights.append(
        f"Líder mais dominante: {strongest['leader']} ({strongest['name']}) "
        f"com {int(strongest['leader_pts'])} pontos."
    )

    return {
        "leagues":  league_stats,
        "insights": insights,
        "chart_data": {
            "radar": {
                "labels": ["Pts Líder", "Média Pts", "Gols/Jogo", "Equilíbrio"],
                "datasets": [
                    {
                        "name":   lg["name"],
                        "values": [radar_norm[m][i] for m in metrics],
                    }
                    for i, lg in enumerate(league_stats)
                ],
            },
            "bars": {
                "labels":              [lg["name"] for lg in league_stats],
                "goals_per_game":      [lg["goals_per_game"]      for lg in league_stats],
                "avg_pts":             [lg["avg_pts"]             for lg in league_stats],
                "competitive_balance": [lg["competitive_balance"] for lg in league_stats],
            },
        },
    }


# ============================================================================
# SEASON PREDICTIONS (Linear Regression)
# ============================================================================

def predict_season(standings: List[Dict]) -> Dict:
    if not standings or len(standings) < 3:
        return {"error": "Dados insuficientes para previsão (mínimo 3 times)"}

    names, pts_l, rank_l, played_l, wins_l, draws_l = [], [], [], [], [], []

    for s in standings:
        team  = s.get("team", {})
        all_s = s.get("all", {}) if isinstance(s.get("all"), dict) else {}
        names.append(team.get("name", "?") if isinstance(team, dict) else str(team))
        pts_l.append(float(s.get("points", 0) or 0))
        rank_l.append(float(s.get("rank", 0) or 0))
        played_l.append(float(all_s.get("played", 0) or 0))
        wins_l.append(float(all_s.get("win", 0) or 0))
        draws_l.append(float(all_s.get("draw", 0) or 0))

    pts_a    = np.array(pts_l)
    rank_a   = np.array(rank_l)
    played_a = np.array(played_l)

    # Infer total games from number of teams
    n_teams     = len(standings)
    total_games = float((n_teams - 1) * 2)
    total_games = max(total_games, float(np.max(played_a)))

    games_remaining = np.maximum(total_games - played_a, 0.0)
    rate            = np.where(played_a > 0, pts_a / played_a, 0.0)
    projected_pts   = rate * total_games

    # Linear regression: rank → points (expected curve)
    X = rank_a.reshape(-1, 1)
    y = pts_a
    reg          = LinearRegression().fit(X, y)
    expected_pts = reg.predict(X)
    residuals    = pts_a - expected_pts
    residual_std = float(np.std(residuals))

    predictions = []
    for i in range(len(names)):
        predictions.append({
            "current_rank":    int(rank_a[i]),
            "name":            names[i],
            "current_pts":     int(pts_a[i]),
            "games_played":    int(played_a[i]),
            "games_remaining": int(games_remaining[i]),
            "points_rate":     round(float(rate[i]), 2),
            "projected_pts":   round(float(projected_pts[i]), 1),
            "proj_pts_low":    round(float(projected_pts[i] - residual_std), 1),
            "proj_pts_high":   round(float(projected_pts[i] + residual_std), 1),
            "expected_pts":    round(float(expected_pts[i]), 1),
            "residual":        round(float(residuals[i]), 1),
            "overperforming":  bool(residuals[i] >  2.0),
            "underperforming": bool(residuals[i] < -2.0),
        })

    sorted_idxs = sorted(range(len(predictions)), key=lambda i: predictions[i]["projected_pts"], reverse=True)
    for new_rank, idx in enumerate(sorted_idxs):
        predictions[idx]["predicted_rank"] = new_rank + 1
        predictions[idx]["rank_change"]    = predictions[idx]["current_rank"] - (new_rank + 1)

    by_current_rank = sorted(predictions, key=lambda x: x["current_rank"])

    x_range  = np.linspace(1, len(names), 60)
    reg_line = reg.predict(x_range.reshape(-1, 1))

    # Insights
    insights: List[str] = []
    champion = min(predictions, key=lambda x: x["predicted_rank"])
    if champion["current_rank"] != 1:
        insights.append(
            f"Previsão surpreendente: {champion['name']} pode terminar em 1º lugar "
            f"com {champion['projected_pts']} pontos projetados (atual: {champion['current_rank']}º)."
        )
    else:
        insights.append(
            f"{champion['name']} deve manter o 1º lugar com {champion['projected_pts']} pontos projetados "
            f"(taxa atual: {champion['points_rate']} pts/jogo)."
        )

    risers  = sorted(predictions, key=lambda x: x.get("rank_change", 0), reverse=True)
    fallers = sorted(predictions, key=lambda x: x.get("rank_change", 0))
    if risers[0].get("rank_change", 0) > 2:
        r = risers[0]
        insights.append(
            f"Maior subida projetada: {r['name']} +{r['rank_change']} posições "
            f"(de {r['current_rank']}º → {r['predicted_rank']}º)."
        )
    if fallers[0].get("rank_change", 0) < -2:
        f_ = fallers[0]
        insights.append(
            f"Maior queda projetada: {f_['name']} {f_['rank_change']} posições "
            f"(de {f_['current_rank']}º → {f_['predicted_rank']}º)."
        )

    over  = [p for p in predictions if p["overperforming"]]
    under = [p for p in predictions if p["underperforming"]]
    if over:
        ns = ", ".join(p["name"] for p in sorted(over, key=lambda x: x["residual"], reverse=True)[:2])
        insights.append(f"Times acima do esperado para sua posição: {ns}.")
    if under:
        ns = ", ".join(p["name"] for p in sorted(under, key=lambda x: x["residual"])[:2])
        insights.append(f"Times abaixo do esperado para sua posição: {ns}.")

    insights.append(
        f"Modelo R²={reg.score(X, y):.2f} | {int(total_games)} jogos por temporada | "
        f"Erro padrão ±{residual_std:.1f} pts."
    )

    proj_by_pred = sorted(predictions, key=lambda x: x["predicted_rank"])
    return {
        "summary": {
            "total_games":         int(total_games),
            "avg_games_remaining": round(float(np.mean(games_remaining)), 1),
            "regression_r2":       round(float(reg.score(X, y)), 3),
            "residual_std":        round(residual_std, 1),
            "risers":              len([p for p in predictions if p.get("rank_change", 0) > 0]),
            "fallers":             len([p for p in predictions if p.get("rank_change", 0) < 0]),
        },
        "predictions": by_current_rank,
        "insights":    insights,
        "chart_data": {
            "scatter": [
                {
                    "x":              p["current_rank"],
                    "y":              p["current_pts"],
                    "label":          p["name"],
                    "projected":      p["projected_pts"],
                    "overperforming": p["overperforming"],
                    "underperforming":p["underperforming"],
                }
                for p in by_current_rank
            ],
            "regression_line": {
                "x": [round(float(v), 2) for v in x_range],
                "y": [round(float(v), 2) for v in reg_line],
            },
            "projected_bar": {
                "labels":    [p["name"]           for p in proj_by_pred],
                "current":   [p["current_pts"]    for p in proj_by_pred],
                "projected": [p["projected_pts"]  for p in proj_by_pred],
            },
        },
    }


# ============================================================================
# K-MEANS CLUSTERING
# ============================================================================

def cluster_teams(standings: List[Dict], n_clusters: int = 4) -> Dict:
    if not standings or len(standings) < 4:
        return {"error": "Dados insuficientes para clustering (mínimo 4 times)"}

    from sklearn.cluster import KMeans

    names: List[str] = []
    attack_rates: List[float] = []
    defense_rates: List[float] = []
    win_rates_list: List[float] = []
    pts_rates: List[float] = []

    for s in standings:
        team  = s.get("team", {})
        all_s = s.get("all", {}) if isinstance(s.get("all"), dict) else {}
        goals = all_s.get("goals", {}) if isinstance(all_s, dict) else {}
        played = max(float(all_s.get("played", 1) or 1) if isinstance(all_s, dict) else 1.0, 1.0)

        names.append(team.get("name", "?") if isinstance(team, dict) else str(team))
        attack_rates.append(float(goals.get("for",     0) or 0) / played)
        defense_rates.append(float(goals.get("against", 0) or 0) / played)
        win_rates_list.append(float(all_s.get("win", 0) or 0) / played if isinstance(all_s, dict) else 0.0)
        pts_rates.append(float(s.get("points", 0) or 0) / played)

    attack_a   = np.array(attack_rates)
    defense_a  = np.array(defense_rates)
    win_a      = np.array(win_rates_list)
    pts_rate_a = np.array(pts_rates)

    X = np.column_stack([attack_a, defense_a, win_a, pts_rate_a])

    k        = min(n_clusters, len(standings))
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km       = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels   = km.fit_predict(X_scaled)

    _names  = ["Dominante", "Competitivo", "Regular", "Em Dificuldade"]
    _colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

    cluster_mean_pts = {ci: float(np.mean(pts_rate_a[labels == ci])) for ci in range(k)}
    sorted_clusters  = sorted(cluster_mean_pts, key=lambda c: cluster_mean_pts[c], reverse=True)
    rank_map         = {old: new for new, old in enumerate(sorted_clusters)}
    ordered_labels   = np.array([rank_map[l] for l in labels])

    items: List[Dict] = [
        {
            "name":         names[i],
            "cluster_id":   int(ordered_labels[i]),
            "cluster_name": _names[int(ordered_labels[i])] if int(ordered_labels[i]) < len(_names) else f"Cluster {ordered_labels[i]}",
            "attack_rate":  round(float(attack_a[i]),   2),
            "defense_rate": round(float(defense_a[i]),  2),
            "win_rate":     round(float(win_a[i]),       3),
            "pts_rate":     round(float(pts_rate_a[i]), 2),
        }
        for i in range(len(names))
    ]

    clusters: List[Dict] = []
    for ci in range(k):
        mask    = ordered_labels == ci
        c_items = [items[i] for i in range(len(items)) if ordered_labels[i] == ci]
        clusters.append({
            "id":    ci,
            "name":  _names[ci] if ci < len(_names) else f"Cluster {ci}",
            "color": _colors[ci] if ci < len(_colors) else "#94a3b8",
            "size":  int(mask.sum()),
            "teams": [t["name"] for t in c_items],
            "centroid": {
                "attack_rate":  round(float(attack_a[mask].mean())   if mask.sum() else 0.0, 2),
                "defense_rate": round(float(defense_a[mask].mean())  if mask.sum() else 0.0, 2),
                "win_rate":     round(float(win_a[mask].mean())      if mask.sum() else 0.0, 3),
                "pts_rate":     round(float(pts_rate_a[mask].mean()) if mask.sum() else 0.0, 2),
            },
        })

    centroids_orig = np.array([
        X[ordered_labels == ci].mean(axis=0) if (ordered_labels == ci).sum() > 0 else np.zeros(4)
        for ci in range(k)
    ])
    max_dist, isolated = -1.0, ""
    for i in range(len(names)):
        ci   = int(ordered_labels[i])
        dist = float(np.linalg.norm(X[i] - centroids_orig[ci]))
        if dist > max_dist:
            max_dist, isolated = dist, names[i]

    insights: List[str] = []
    insights.append(
        f"Cluster '{clusters[0]['name']}': {clusters[0]['size']} time(s) com "
        f"{clusters[0]['centroid']['pts_rate']:.2f} pts/jogo e "
        f"{clusters[0]['centroid']['attack_rate']:.2f} gols marcados/jogo."
    )
    if k > 1:
        wk = clusters[-1]
        insights.append(f"Cluster '{wk['name']}': {wk['size']} time(s) com {wk['centroid']['pts_rate']:.2f} pts/jogo.")
    if isolated:
        insights.append(f"Time mais isolado do seu cluster: {isolated} (dist. centróide: {max_dist:.2f}).")
    biggest = max(clusters, key=lambda c: c["size"])
    insights.append(f"Cluster mais populoso: '{biggest['name']}' com {biggest['size']} time(s).")

    return {
        "n_clusters":  k,
        "total_teams": len(names),
        "clusters":    clusters,
        "items":       items,
        "insights":    insights,
        "chart_data": {
            "scatter": [
                {
                    "x":           item["attack_rate"],
                    "y":           item["defense_rate"],
                    "label":       item["name"],
                    "cluster_id":  item["cluster_id"],
                    "cluster_name":item["cluster_name"],
                    "pts_rate":    item["pts_rate"],
                }
                for item in items
            ],
            "bar": {
                "labels": [c["name"]  for c in clusters],
                "values": [c["size"]  for c in clusters],
                "colors": [c["color"] for c in clusters],
            },
        },
    }


# ============================================================================
# MONTE CARLO SIMULATION
# ============================================================================

def monte_carlo_season(standings: List[Dict], n_simulations: int = 10_000) -> Dict:
    if not standings or len(standings) < 3:
        return {"error": "Dados insuficientes para simulação (mínimo 3 times)"}

    names: List[str] = []
    current_pts_l: List[float] = []
    wins_l: List[float] = []
    draws_l: List[float] = []
    played_l: List[float] = []

    for s in standings:
        team  = s.get("team", {})
        all_s = s.get("all", {}) if isinstance(s.get("all"), dict) else {}
        names.append(team.get("name", "?") if isinstance(team, dict) else str(team))
        current_pts_l.append(float(s.get("points", 0) or 0))
        wins_l.append(float(all_s.get("win",    0) or 0) if isinstance(all_s, dict) else 0.0)
        draws_l.append(float(all_s.get("draw",   0) or 0) if isinstance(all_s, dict) else 0.0)
        played_l.append(float(all_s.get("played", 0) or 0) if isinstance(all_s, dict) else 0.0)

    n_teams     = len(names)
    current_pts = np.array(current_pts_l)
    wins        = np.array(wins_l)
    draws       = np.array(draws_l)
    played      = np.array(played_l)

    total_games = max(float((n_teams - 1) * 2), float(np.max(played)))
    games_rem   = np.maximum(total_games - played, 0.0).astype(int)
    n_bottom    = max(1, n_teams // 6)
    season_done = bool(np.all(games_rem == 0))

    if season_done:
        final_order = np.argsort(-current_pts)
        rank_of     = {int(final_order[r]): r + 1 for r in range(n_teams)}
        results: List[Dict] = []
        for i in range(n_teams):
            r = rank_of[i]
            results.append({
                "current_rank":    int(standings[i].get("rank", i + 1)),
                "name":            names[i],
                "current_pts":     int(current_pts[i]),
                "games_remaining": 0,
                "championship_prob": 1.0 if r == 1 else 0.0,
                "top4_prob":         1.0 if r <= 4 else 0.0,
                "relegation_prob":   1.0 if r > n_teams - n_bottom else 0.0,
                "avg_final_pts":     float(current_pts[i]),
                "most_likely_rank":  r,
            })
        results_sorted = sorted(results, key=lambda x: x["most_likely_rank"])
        champion = results_sorted[0]
        insights = [
            f"Temporada encerrada. Campeão: {champion['name']} com {champion['current_pts']} pts.",
            f"Top 4: {', '.join(r['name'] for r in results_sorted[:4])}.",
            f"Rebaixados: {', '.join(r['name'] for r in results_sorted[-n_bottom:])}.",
            "Esta simulação é mais útil durante temporadas em andamento.",
        ]
        return {
            "summary":  {"n_simulations": 0, "season_complete": True,  "total_games": int(total_games), "n_bottom": n_bottom},
            "results":  results_sorted,
            "insights": insights,
            "chart_data": {
                "championship": {"labels": [r["name"] for r in results_sorted[:10]], "probs": [r["championship_prob"] * 100 for r in results_sorted[:10]]},
                "positions":    {"labels": [r["name"] for r in results_sorted], "top4": [r["top4_prob"] * 100 for r in results_sorted], "relegation": [r["relegation_prob"] * 100 for r in results_sorted]},
            },
        }

    safe_played = np.maximum(played, 1.0)
    win_r  = wins  / safe_played
    draw_r = draws / safe_played
    loss_r = np.maximum(1.0 - win_r - draw_r, 0.0)
    totals = win_r + draw_r + loss_r
    win_r  = win_r  / totals
    draw_r = draw_r / totals
    loss_r = loss_r / totals

    projected = np.tile(current_pts.astype(float), (n_simulations, 1))
    for i in range(n_teams):
        rem = int(games_rem[i])
        if rem > 0:
            p   = [float(win_r[i]), float(draw_r[i]), float(loss_r[i])]
            sim = np.random.multinomial(rem, p, n_simulations)
            projected[:, i] += sim[:, 0] * 3 + sim[:, 1]

    sorted_idx     = np.argsort(-projected, axis=1)
    team_sim_rank  = np.empty_like(sorted_idx)
    rows           = np.arange(n_simulations)[:, None]
    team_sim_rank[rows, sorted_idx] = np.arange(n_teams)

    results_list: List[Dict] = []
    for i in range(n_teams):
        r_arr = team_sim_rank[:, i]
        results_list.append({
            "current_rank":      int(standings[i].get("rank", i + 1)),
            "name":              names[i],
            "current_pts":       int(current_pts[i]),
            "games_remaining":   int(games_rem[i]),
            "championship_prob": round(float((r_arr == 0).mean()), 4),
            "top4_prob":         round(float((r_arr < 4).mean()),  4),
            "relegation_prob":   round(float((r_arr >= n_teams - n_bottom).mean()), 4),
            "avg_final_pts":     round(float(projected[:, i].mean()), 1),
            "most_likely_rank":  int(np.bincount(r_arr).argmax()) + 1,
        })

    sorted_results  = sorted(results_list, key=lambda x: x["current_rank"])
    by_championship = sorted(results_list, key=lambda x: x["championship_prob"], reverse=True)

    champion   = by_championship[0]
    contenders = [r for r in results_list if r["championship_prob"] > 0.05]
    risk_teams = sorted([r for r in results_list if r["relegation_prob"] > 0.10],
                        key=lambda x: x["relegation_prob"], reverse=True)
    top4_fav   = sorted(results_list, key=lambda x: x["top4_prob"], reverse=True)[:4]

    mc_insights: List[str] = []
    mc_insights.append(
        f"{champion['name']} é favorito ao título: {champion['championship_prob']*100:.1f}% "
        f"({n_simulations:,} simulações)."
    )
    if len(contenders) > 1:
        oth = [r for r in contenders if r["name"] != champion["name"]]
        mc_insights.append(
            "Outros contendores: " + ", ".join(f"{r['name']} ({r['championship_prob']*100:.1f}%)" for r in oth[:3]) + "."
        )
    if risk_teams:
        mc_insights.append(
            "Risco de rebaixamento: " + ", ".join(f"{r['name']} ({r['relegation_prob']*100:.1f}%)" for r in risk_teams[:4]) + "."
        )
    mc_insights.append(f"Top 4 mais provável: {', '.join(r['name'] for r in top4_fav)}.")

    return {
        "summary": {
            "n_simulations":       n_simulations,
            "season_complete":     False,
            "total_games":         int(total_games),
            "n_bottom":            n_bottom,
            "avg_games_remaining": round(float(np.mean(games_rem)), 1),
        },
        "results":  sorted_results,
        "insights": mc_insights,
        "chart_data": {
            "championship": {
                "labels": [r["name"] for r in by_championship[:10]],
                "probs":  [round(r["championship_prob"] * 100, 1) for r in by_championship[:10]],
            },
            "positions": {
                "labels":     [r["name"] for r in sorted_results],
                "top4":       [round(r["top4_prob"]       * 100, 1) for r in sorted_results],
                "relegation": [round(r["relegation_prob"] * 100, 1) for r in sorted_results],
            },
        },
    }
