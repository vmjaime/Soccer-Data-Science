import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ruta base (sube un nivel desde /src/)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "international-wc-qualification-south-america-matches-2023-to-2026-stats.csv")

# Leer dataset
df = pd.read_csv(DATA_PATH)

# 🔧 Limpiamos: quitamos partidos no jugados (posesión = -1 o status distinto de complete)
df_clean = df[(df["home_team_possession"] != -1) & (df["away_team_possession"] != -1)]
df_clean = df_clean[df_clean["status"] == "complete"]

# 📊 Creamos tabla de estadísticas por equipo
equipos = []

for team in pd.concat([df_clean["home_team_name"], df_clean["away_team_name"]]).unique():
    team_matches = df_clean[(df_clean["home_team_name"] == team) | (df_clean["away_team_name"] == team)]
    
    goals_for = team_matches.apply(
        lambda row: row["home_team_goal_count"] if row["home_team_name"] == team else row["away_team_goal_count"],
        axis=1
    ).mean()
    goals_against = team_matches.apply(
        lambda row: row["away_team_goal_count"] if row["home_team_name"] == team else row["home_team_goal_count"],
        axis=1
    ).mean()
    possession = team_matches.apply(
        lambda row: row["home_team_possession"] if row["home_team_name"] == team else row["away_team_possession"],
        axis=1
    ).mean()
    shots = team_matches.apply(
        lambda row: row["home_team_shots"] if row["home_team_name"] == team else row["away_team_shots"],
        axis=1
    ).mean()
    shots_on_target = team_matches.apply(
        lambda row: row["home_team_shots_on_target"] if row["home_team_name"] == team else row["away_team_shots_on_target"],
        axis=1
    ).mean()
    xg = team_matches.apply(
        lambda row: row["team_a_xg"] if row["home_team_name"] == team else row["team_b_xg"],
        axis=1
    ).mean()
    points = team_matches.apply(
        lambda row: 3 if (
            (row["home_team_name"] == team and row["home_team_goal_count"] > row["away_team_goal_count"]) or
            (row["away_team_name"] == team and row["away_team_goal_count"] > row["home_team_goal_count"])
        ) else (1 if row["home_team_goal_count"] == row["away_team_goal_count"] else 0),
        axis=1
    ).mean()

    equipos.append([team, goals_for, goals_against, possession, shots, shots_on_target, xg, points])

# DataFrame final con estadísticas de todos los equipos
df_equipos = pd.DataFrame(equipos, columns=[
    "team", "goals_for", "goals_against", "possession", "shots", "shots_on_target", "xG", "points"
])

# Ordenamos por puntos promedio
df_equipos = df_equipos.sort_values("points", ascending=False).reset_index(drop=True)

# --- Ajustar posesión antes de Z-Score ---
df_equipos["possession"] = df_equipos["possession"] / 100

# --- Paso 1: Estandarización con Z-Score ---
cols = ["goals_for", "goals_against", "possession", "shots", "shots_on_target", "xG", "points"]

df_zscore = df_equipos.copy()
for col in cols:
    mean = df_equipos[col].mean()
    std = df_equipos[col].std()
    df_zscore[col] = (df_equipos[col] - mean) / std

# ✅ Invertimos goles en contra para que alto = mejor defensa
df_zscore["defense_strength"] = -df_zscore["goals_against"]

# --- Paso 2: Reordenar columnas finales ---
final_cols = ["team", "goals_for", "defense_strength", "possession", "shots", "shots_on_target", "xG", "points"]
df_stats = df_zscore[final_cols].round(2)

# --- Paso 3: Medias y desviaciones originales ---
means = df_equipos[["goals_for", "goals_against", "possession", "shots", "shots_on_target", "xG", "points"]].mean().round(2)
stds = df_equipos[["goals_for", "goals_against", "possession", "shots", "shots_on_target", "xG", "points"]].std().round(2)

df_stats.loc["Media"] = ["-"] + [means["goals_for"], "-", means["possession"], means["shots"], means["shots_on_target"], means["xG"], means["points"]]
df_stats.loc["Desv.Std"] = ["-"] + [stds["goals_for"], "-", stds["possession"], stds["shots"], stds["shots_on_target"], stds["xG"], stds["points"]]

# --- Paso 4: Matriz de correlación y ponderaciones ---
corr_vars = ["goals_for", "defense_strength", "possession", 
             "shots", "shots_on_target", "xG", "points"]

# ⚠️ Excluir filas de resumen ("Media" y "Desv.Std")
df_corr = df_stats.drop(index=["Media", "Desv.Std"], errors="ignore")

corr_matrix = df_corr[corr_vars].astype(float).corr()

# --- Pesos basados en correlación con points ---
corr_with_points = corr_matrix["points"].drop("points").abs()
weights = corr_with_points / corr_with_points.sum()


# --- Paso 5: Índice ponderado de rendimiento ---
# Usamos los Z-scores de cada métrica multiplicados por su peso
df_eval = df_corr.copy()  # solo equipos reales, sin Media ni Desv.Std
df_eval["performance_index"] = sum(
    df_eval[var] * weights[var] for var in weights.index
)

# --- Paso 6: Ranking esperado vs puntos reales ---
df_ranking = df_eval[["team", "performance_index", "points"]].sort_values("performance_index", ascending=False)



# Calcular diferencia
df_ranking["delta"] = df_ranking["performance_index"] - df_ranking["points"]

# Ordenar por delta
df_ranking = df_ranking.sort_values("delta", ascending=False)

# Graficar
plt.figure(figsize=(10,6))
colors = df_ranking["delta"].apply(lambda x: "green" if x > 0 else "red")

plt.barh(df_ranking["team"], df_ranking["delta"], color=colors)
plt.axvline(0, color="black", linewidth=0.8)

plt.title("Índice de eficiencia competitiva: rendimiento medido vs puntos logrados", fontsize=14, weight="bold")
plt.xlabel("Diferencia (Z-score)")
plt.ylabel("Selección")
plt.tight_layout()
plt.show()


