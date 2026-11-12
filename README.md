# DadoLocke Engine

Aplicación web para llevar el control de una partida de **DadoLocke**, una variante de Nuzlocke de Pokémon donde los dados y las ruletas deciden qué pasa en cada momento clave: capturas, gimnasios, medallas y muertes de Pokémon. Hecha con Python y [Streamlit](https://streamlit.io).

## Qué hace

- **Vidas:** empiezas con 20 y la app las va actualizando según los efectos.
- **Equipo Pokémon:** registra hasta 6 Pokémon y márcalos como muertos.
- **Eventos con dado (1 a 6)**, cada uno con su propia ruleta de efectos:
  - 🌿 **Pokémon de ruta:** cómo capturar (o no) el Pokémon de la ruta.
  - 🏟️ **Antes del gimnasio:** condiciones para el combate.
  - 🏅 **Después de medalla:** recompensas y castigos.
  - ☠️ **Muerte Pokémon:** se lanza al confirmar una muerte y puede costar o devolver vidas.
  - ✨ **Ruleta Divina:** efectos especiales de uso limitado.
- **Efectos guardados:** algunos efectos se guardan para usarlos después.
- **Dado trucado:** efecto que permite elegir el número del dado.
- **Buscador Pokémon:** muestra tipos y stats base usando [PokéAPI](https://pokeapi.co).
- **Historial** de los últimos eventos del destino.
- **Guardado de partida:** descarga y carga tu partida en un archivo `.json`.

En total hay 5 ruletas con 6 efectos cada una (30 efectos), descritos en `efectos_ruleta.csv`.

## Requisitos

- Python 3.9 o superior
- Streamlit 1.37 o superior (usa `st.dialog`)
- Conexión a internet (para el buscador de Pokémon)

## Instalación y ejecución

```bash
git clone https://github.com/Z3gga/DadoLockee.git
cd DadoLockee

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run appv1.2.py
```

La app se abre en http://localhost:8501.

## Archivos

```
appv1.2.py           # Aplicación principal (Streamlit)
efectos_ruleta.csv   # Tabla de efectos de cada ruleta (ruleta, dado, nombre, descripción, vidas)
tiradas_dado.csv     # Registro de tiradas de una partida (la app actual no lo usa)
estado_run.csv       # Estado guardado de una partida (la app actual no lo usa)
requirements.txt
```

## Créditos

Pokémon es marca de Nintendo / Creatures Inc. / GAME FREAK inc. Este es un proyecto de fans sin fines de lucro y no está afiliado a ellos. Los datos de Pokémon vienen de [PokéAPI](https://pokeapi.co).
