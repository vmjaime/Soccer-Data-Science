# ⚽ Soccer Data Science – Ecuador en las Eliminatorias CONMEBOL

Este proyecto aplica **Ciencia de Datos** al análisis del rendimiento de Ecuador en las Eliminatorias Sudamericanas rumbo al Mundial 2026.  

Combina métricas avanzadas, estandarización estadística (Z-Score) y visualizaciones para entender por qué Ecuador ocupa su posición actual en la tabla a pesar de registrar pocos goles.

---

## 📊 Objetivos del análisis
- Identificar **KPIs clave** (goles, posesión, xG, tiros, defensa, disciplina).
- Analizar la relación de cada métrica con los **puntos obtenidos**.
- Comparar el rendimiento de Ecuador frente a otras selecciones de CONMEBOL.
- Detectar **equipos sobrevalorados y subvalorados** según su desempeño esperado vs real.
- Medir la **similitud entre selecciones** (qué equipos juegan más parecido).

---

## 🔑 Principales hallazgos
- 🇪🇨 **Ecuador** destaca por su **solidez defensiva** como principal fortaleza.  
- Su **producción ofensiva es baja**: pocos goles, bajo xG y escasos tiros al arco.  
- El **rendimiento cae cuando aumentan las tarjetas amarillas**, reflejando un juego muy físico.  
- El equipo **depende más de individualidades que del juego colectivo**.  
- Comparado con otras selecciones, Ecuador acumula **más puntos de los esperados** según sus KPIs.  
- 📌 El equipo más parecido en métricas a Ecuador es **Paraguay**, su próximo rival.

---

## 🛠️ Metodología
1. **Limpieza de datos** → Exclusión de partidos no jugados o con posesión inválida.  
2. **Feature Engineering** → Cálculo de KPIs como goles, posesión, xG, tiros y tarjetas.  
3. **Estandarización (Z-Score)** → Para comparar métricas en diferentes escalas.  
4. **Correlación** → Identificación de las variables más influyentes en los puntos.  
5. **Ponderación de métricas** → Construcción de un índice de rendimiento (*Performance Index*).  
6. **Comparación inter-equipos** → Ranking de sobrevalorados/subvalorados.  

---

## 📂 Estructura del repositorio
