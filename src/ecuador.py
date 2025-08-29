import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import euclidean_distances

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
    ).mean() / 100  # ✅ pasamos a proporción
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

# DataFrame con estadísticas
df_equipos = pd.DataFrame(equipos, columns=[
    "team", "goals_for", "goals_against", "possession", "shots", "shots_on_target", "xG", "points"
])

# --- Estandarización con Z-score ---
cols = ["goals_for", "goals_against", "possession", "shots", "shots_on_target", "xG", "points"]
df_zscore = df_equipos.copy()
for col in cols:
    mean = df_equipos[col].mean()
    std = df_equipos[col].std()
    df_zscore[col] = (df_equipos[col] - mean) / std

# ✅ Invertimos goles en contra (defensa fuerte = mejor valor)
df_zscore["defense_strength"] = -df_zscore["goals_against"]

# Variables finales
compare_vars = ["goals_for", "defense_strength", "possession", "shots", "shots_on_target", "xG", "points"]

# --- Similitud con Ecuador ---
ecuador_vector = df_zscore[df_zscore["team"] == "Ecuador"][compare_vars].values
others = df_zscore[df_zscore["team"] != "Ecuador"]

# Distancias euclídeas
distances = euclidean_distances(ecuador_vector, others[compare_vars].values)[0]

# Convertimos a similitud (0–1, donde 1 = idéntico a Ecuador)
similarity_df = others.copy()
similarity_df["similarity_to_ecuador"] = 1 / (1 + distances)

# Ordenamos de mayor a menor similitud
similarity_df = similarity_df.sort_values("similarity_to_ecuador", ascending=False)

print("=== Selecciones más parecidas a Ecuador (similitud 0–1) ===")
print(similarity_df[["team", "similarity_to_ecuador"]].round(3))

# --- Visualización ---
plt.figure(figsize=(8,5))
sns.barplot(
    data=similarity_df,
    x="similarity_to_ecuador",
    y="team",
    palette="viridis"
)
plt.title("Similitud con Ecuador", fontsize=14, weight="bold")
plt.xlabel("Similitud a Ecuador")
plt.ylabel("Selección")
plt.tight_layout()
plt.show()

