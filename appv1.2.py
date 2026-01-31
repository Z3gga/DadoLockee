import streamlit as st
import requests
import random
import json
import os
SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)


def get_save_data():
    return {
        "vidas": st.session_state.vidas,
        "equipo": st.session_state.equipo,
        "muertos": list(st.session_state.muertos),
        "efectos_guardados": st.session_state.efectos_guardados
    }

def guardar_partida(nombre):
    os.makedirs("saves", exist_ok=True)

    equipo = st.session_state.equipo[:6]
    while len(equipo) < 6:
        equipo.append("")

    data = {
        "vidas": st.session_state.vidas,
        "equipo": equipo,
        "muertos": list(st.session_state.muertos),
        "efectos_guardados": st.session_state.efectos_guardados
    }

    with open(f"saves/{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def cargar_partida(nombre):
    with open(f"saves/{nombre}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def restaurar_estado(data):
    if not data:
        return

    st.session_state.vidas = data.get("vidas", 20)

    equipo = data.get("equipo", [""] * 6)
    equipo = (equipo + [""] * 6)[:6]
    st.session_state.equipo = equipo

    st.session_state.muertos = set(data.get("muertos", []))
    st.session_state.efectos_guardados = data.get("efectos_guardados", [])

    st.session_state.partida_recien_cargada = True
    st.rerun()



st.set_page_config(page_title="Pokeinador DadoLocke", layout="wide")

# =========================
# SESSION STATE
# =========================
if "vidas" not in st.session_state:
    st.session_state.vidas = 20

if "equipo" not in st.session_state:
    st.session_state.equipo = [""] * 6

if "muertos" not in st.session_state:
    st.session_state.muertos = set()

if "evento" not in st.session_state:
    st.session_state.evento = None

if "evento_pendiente" not in st.session_state:
    st.session_state.evento_pendiente = False

if "confirmando" not in st.session_state:
    st.session_state.confirmando = None

# Eventos
if "evento_ruta" not in st.session_state:
    st.session_state.evento_ruta = None

if "evento_gimnasio" not in st.session_state:
    st.session_state.evento_gimnasio = None

if "evento_medalla" not in st.session_state:
    st.session_state.evento_medalla = None

# Buffs y control
if "control_destino" not in st.session_state:
    st.session_state.control_destino = False

if "esperando_destino" not in st.session_state:
    st.session_state.esperando_destino = None  # ruta | gimnasio | medalla | muerte

if "dado_elegido" not in st.session_state:
    st.session_state.dado_elegido = None

if "muerte_pendiente" not in st.session_state:
    st.session_state.muerte_pendiente = None

if "efectos_guardados" not in st.session_state:
    st.session_state.efectos_guardados = []

if "ultimo_dado" not in st.session_state:
    st.session_state.ultimo_dado = None

if "ruleta_divina_pendiente" not in st.session_state:
    st.session_state.ruleta_divina_pendiente = False

if "ruleta_divina_usos" not in st.session_state:
    st.session_state.ruleta_divina_usos = 0

if "ruleta_divina_resultado" not in st.session_state:
    st.session_state.ruleta_divina_resultado = None

# Historial
if "historial_eventos" not in st.session_state:
    st.session_state.historial_eventos = []
EFECTOS_GUARDABLES_POR_EVENTO = {
    "medalla": {1,4,5},        # Revivir Caído, Captura Extra, Control del Destino
    "gimnasio": {4},             # Revivir Pokémon
    "ruleta_divina": {1,4,5,6} # Resurrección Doble, Cosecha Final, Escape Abismo, Juicio Absoluto
}


EFECTOS_GUARDABLES = {
    "Revivir Caído",
    "Revivir Pokémon",
    "Captura Extra",
    "Control del Destino",
    "Resurrección Doble",
    "Cosecha Final",
    "Escape del Abismo",
    "Juicio Absoluto",
}



# =========================
# EFECTOS
# =========================
EFECTOS = {
    1: ("Sacrificio Encadenado", "Otro Pokémon también muere.", 0),
    2: ("Luto de Tipo", "No puedes usar ese tipo hasta el próximo gimnasio.", 0),
    3: ("Muerte Agónica", "Pierdes 2 vidas.", -1),
    4: ("Resurrección Dolorosa", "Revive, pero pierdes 1 vida.", -1),
    5: ("Condena al Abismo", "El Pokémon va al Abismo.", 0),
    6: ("Legado del Caído", "Ganas 1 vida adicional.", 1),
}

EFECTOS_RUTA = {
    1: ("Captura Normal", "Puedes capturar normalmente el Pokémon."),
    2: ("Una sola PokéBall", "Solo puedes usar UNA PokéBall."),
    3: ("Bloqueo de Captura", "No puedes capturar este Pokémon."),
    4: ("Caja Forzada", "Capturas, pero va directo a la caja hasta el próximo gimnasio."),
    5: ("Elección Doble", "Puedes capturar este o el siguiente Pokémon de la ruta."),
    6: ("Anulación de Muertes", "Se anulan todas las muertes de este combate."),
}

EFECTOS_GIMNASIO = {
    1: ("Equipo Reducido", "Usa solo la MITAD de tu equipo Pokémon."),
    2: ("Sin Ítems", "Prohibido usar ítems en combate."),
    3: ("Segundo Intento", "Si pierdes, puedes intentar nuevamente."),
    4: ("Revivir Pokémon", "Puedes revivir 1 Pokémon del cementerio."),
    5: ("Bloqueo de Pokémon", "Un Pokémon del equipo queda bloqueado este y el siguiente combate."),
    6: ("Combate Normal", "Combate sin efectos especiales."),
}

EFECTOS_MEDALLA = {
    1: ("Revivir Caído", "Puedes revivir un Pokémon del cementerio."),
    2: ("Bendición Vital", "Ganas +2 vidas."),
    3: ("Curaciones", "Compra 4 curaciones."),
    4: ("Captura Extra", "Obtienes una captura extra para usar cuando quieras."),
    5: ("Control del Destino", "Puedes elegir el efecto de tu siguiente evento."),
    6: ("Castigo del Campeón", "Debes mandar a tu Pokémon más fuerte a la caja hasta el próximo gimnasio."),
}
RULETA_DIVINA = {
    1: ("Resurrección Doble", "Revive dos Pokémon muertos."),
    2: ("Bendición Suprema", "Ganas 3 vidas adicionales."),
    3: ("Bancarrota Instantánea", "Debes gastar todo tu dinero actual en Pokeballs"),
    4: ("Cosecha Final", "Puedes capturar 2 Pokémon extra en la última ruta visitada."),
    5: ("Escape del Abismo", "Saca a 1 Pokémon del abismo."),
    6: ("Juicio Absoluto", "Puedes anular todas las muertes de el combate que quieras."),
}


# =========================
# UTILIDADES
# =========================
@st.cache_data
def get_lista_pokemon():
    r = requests.get("https://pokeapi.co/api/v2/pokemon?limit=10000")
    if r.status_code != 200:
        return []
    data = r.json()
    return sorted([p["name"] for p in data["results"]])

@st.cache_data
def get_pokemon_full(name):
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower().strip()}")
        if r.status_code != 200:
            return None
        data = r.json()

        tipos = [t["type"]["name"].capitalize() for t in data["types"]]
        stats = {s["stat"]["name"].upper(): s["base_stat"] for s in data["stats"]}

        return {
            "name": name.capitalize(),
            "sprite": data["sprites"]["front_default"],
            "types": tipos,
            "stats": stats
        }
    except:
        return None

def registrar_dado(dado):
    if (
        st.session_state.ultimo_dado == 6
        and dado == 6
        and st.session_state.ruleta_divina_usos < 2
    ):
        st.session_state.ruleta_divina_pendiente = True

    st.session_state.ultimo_dado = dado

def registrar_evento(texto):
    st.session_state.historial_eventos.append(texto)
    if len(st.session_state.historial_eventos) > 3:
        st.session_state.historial_eventos = st.session_state.historial_eventos[-3:]


@st.cache_data
def get_pokemon(name):
    try:
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower().strip()}")
        if r.status_code != 200:
            return None
        data = r.json()
        return {
            "name": name.capitalize(),
            "sprite": data["sprites"]["front_default"]
        }
    except:
        return None


# =========================
# LÓGICA
# =========================
def aplicar_muerte_directa(nombre, dado):
    registrar_dado(dado)
    efecto, desc, cambio = EFECTOS[dado]

    if dado == 4:
        st.session_state.vidas = max(0, st.session_state.vidas - 1)
    else:
        st.session_state.muertos.add(nombre)
        st.session_state.vidas = max(0, st.session_state.vidas - 1 + cambio)

        if dado == 1:
            vivos = [
                p.capitalize()
                for p in st.session_state.equipo
                if p and p.capitalize() not in st.session_state.muertos
            ]
            if vivos:
                segundo = random.choice(vivos)
                st.session_state.muertos.add(segundo)

    st.session_state.evento = {
        "pokemon": nombre,
        "dado": dado,
        "efecto": efecto,
        "descripcion": desc,
        "cambio": cambio
    }

    registrar_evento(f"☠️ Muerte → {efecto}")
    st.session_state.evento_pendiente = True


def aplicar_muerte_random(nombre):
    dado = random.randint(1, 6)
    aplicar_muerte_directa(nombre, dado)


def activar_evento_ruta():
    dado = random.randint(1, 6)
    registrar_dado(dado)
    efecto, desc = EFECTOS_RUTA[dado]
    st.session_state.evento_ruta = {"dado": dado, "efecto": efecto, "descripcion": desc}
    registrar_evento(f"🌿 Ruta → {efecto}")


def activar_evento_gimnasio():
    dado = random.randint(1, 6)
    registrar_dado(dado)
    efecto, desc = EFECTOS_GIMNASIO[dado]

    if dado in EFECTOS_GUARDABLES_POR_EVENTO["gimnasio"]:
        st.session_state.efectos_guardados.append(efecto)

    st.session_state.evento_gimnasio = {
        "dado": dado,
        "efecto": efecto,
        "descripcion": desc
    }
    registrar_evento(f"🏟️ Gimnasio → {efecto}")


def activar_evento_medalla():

    dado = random.randint(1, 6)
    registrar_dado(dado)
    efecto, desc = EFECTOS_MEDALLA[dado]

    if dado in EFECTOS_GUARDABLES_POR_EVENTO["medalla"]:
        st.session_state.efectos_guardados.append(efecto)
    elif dado == 2:  # Bendición Vital
        st.session_state.vidas += 2


    st.session_state.evento_medalla = {
        "dado": dado,
        "efecto": efecto,
        "descripcion": desc
    }
    registrar_evento(f"🏅 Medalla → {efecto}")



# =========================
# DIÁLOGOS
# =========================
@st.dialog("⚠️ Confirmar muerte")
def dialogo_confirmar():
    nombre = st.session_state.confirmando
    st.write(f"¿Confirmas que **{nombre}** ha muerto?")
    if st.button("Confirmar"):
        aplicar_muerte_random(nombre)
        st.session_state.confirmando = None
        st.rerun()


@st.dialog("🎲 Evento")
def dialogo_generico(tipo, titulo):
    e = st.session_state[tipo]
    st.subheader(titulo)
    st.write(f"🎲 **Dado:** {e['dado']}")
    st.write(f"✨ **{e['efecto']}**")
    st.write(e["descripcion"])
    st.divider()

    if st.button("✅ Confirmar"):
        st.session_state[tipo] = None
        st.rerun()

@st.dialog("✨ RULETA DIVINA ✨")
def dialogo_ruleta_divina():
    dado = st.session_state.ruleta_divina_resultado
    efecto, desc = RULETA_DIVINA[dado]

    st.subheader("🎰 El destino ha hablado")
    st.write(f"🎲 **Dado:** {dado}")
    st.write(f"✨ **{efecto}**")
    st.write(desc)
    st.divider()

    if st.button("Aceptar el Juicio"):
        print(dado)
        # GUARDABLES
        if dado in EFECTOS_GUARDABLES_POR_EVENTO["ruleta_divina"]:
            st.session_state.efectos_guardados.append(efecto)

        # INMEDIATOS
        elif dado == 2:
            st.session_state.vidas += 3

        elif dado == 3:
            pass  # Bancarrota (narrativo)

        # LIMPIEZA CRÍTICA
        st.session_state.ruleta_divina_usos += 1
        st.session_state.ruleta_divina_pendiente = False
        st.session_state.ruleta_divina_resultado = None
        st.rerun()

# =========================
# SINCRONIZAR INPUTS AL CARGAR
# =========================
if st.session_state.get("partida_recien_cargada"):
    for i in range(6):
        st.session_state[f"poke_{i}"] = st.session_state.equipo[i]
    st.session_state.partida_recien_cargada = False

# =========================
# UI
# =========================
st.title("DadoLocke Engine")

st.subheader(f"❤️ Vidas: {st.session_state.vidas}")
cols = st.columns(20)
for i in range(20):
    cols[i].markdown("❤️" if i < st.session_state.vidas else "🤍")

st.divider()

st.subheader("👥 Equipo Pokémon")
cols = st.columns(6)

for i in range(6):
    with cols[i]:
        name = st.text_input(
            f"Pokémon {i+1}",
            value=st.session_state.equipo[i],
            key=f"poke_{i}"
        )

        # 🔹 Estado único
        st.session_state.equipo[i] = name

        # 🔹 SIEMPRE mostrar sprite si hay nombre
        if name:
            poke = get_pokemon(name)
            if poke:
                st.image(poke["sprite"], width=120)

                if poke["name"] not in st.session_state.muertos:
                    if st.button("💀 Marcar como muerto", key=f"dead_{i}"):
                        if st.session_state.control_destino:
                            st.session_state.esperando_destino = "muerte"
                            st.session_state.muerte_pendiente = poke["name"]
                        else:
                            st.session_state.confirmando = poke["name"]
                        st.rerun()
                else:
                    st.markdown("☠️ **Muerto**")

# =========================
# EVENTOS
# =========================
st.divider()
st.subheader("🎲 Eventos DadoLocke")
c = st.columns(3)

with c[0]:
    if st.button("🌿 Pokémon de Ruta"):
        if st.session_state.control_destino:
            st.session_state.esperando_destino = "ruta"
        else:
            activar_evento_ruta()
        st.rerun()

with c[1]:
    if st.button("🏟️ Antes del Gimnasio"):
        if st.session_state.control_destino:
            st.session_state.esperando_destino = "gimnasio"
        else:
            activar_evento_gimnasio()
        st.rerun()

with c[2]:
    if st.button("🏅 Después de Medalla"):
        if st.session_state.control_destino:
            st.session_state.esperando_destino = "medalla"
        else:
            activar_evento_medalla()
        st.rerun()


# =========================
# CONTROL DEL DESTINO UI
# =========================
if st.session_state.esperando_destino:
    st.divider()
    st.subheader("🎯 Control del Destino Activo")
    st.markdown("Elige el número del dado:")

    st.session_state.dado_elegido = st.selectbox(
        "Número del dado",
        [1, 2, 3, 4, 5, 6],
        key="selector_destino"
    )

    if st.button("✨ Aplicar Destino"):
        tipo = st.session_state.esperando_destino
        dado = st.session_state.dado_elegido

        if tipo == "ruta":
            efecto, desc = EFECTOS_RUTA[dado]
            st.session_state.evento_ruta = {"dado": dado, "efecto": efecto, "descripcion": desc}
            registrar_evento(f"🌿 Ruta → {efecto}")

        elif tipo == "gimnasio":
            efecto, desc = EFECTOS_GIMNASIO[dado]
            st.session_state.evento_gimnasio = {"dado": dado, "efecto": efecto, "descripcion": desc}
            registrar_evento(f"🏟️ Gimnasio → {efecto}")

        elif tipo == "medalla":
            efecto, desc = EFECTOS_MEDALLA[dado]

            if efecto in EFECTOS_GUARDABLES:
                st.session_state.efectos_guardados.append(efecto)
            else:
                if dado == 2:
                    st.session_state.vidas += 2

            st.session_state.evento_medalla = {
                "dado": dado,
                "efecto": efecto,
                "descripcion": desc
            }
            registrar_evento(f"🏅 Medalla → {efecto}")

        elif tipo == "muerte":
            nombre = st.session_state.muerte_pendiente
            aplicar_muerte_directa(nombre, dado)

        # consumir buff
        st.session_state.control_destino = False
        st.session_state.esperando_destino = None
        st.session_state.dado_elegido = None
        st.session_state.muerte_pendiente = None
        st.rerun()


# =========================
# MODALES
# =========================
if (
    st.session_state.ruleta_divina_pendiente
    and st.session_state.ruleta_divina_resultado is None
):
    dado = random.randint(1, 6)
    st.session_state.ruleta_divina_resultado = dado


if st.session_state.confirmando:
    dialogo_confirmar()

if st.session_state.evento_pendiente:
    dialogo_generico("evento", f"☠️ {st.session_state.evento['pokemon']} ha caído")
    st.session_state.evento_pendiente = False

if st.session_state.evento_ruta:
    dialogo_generico("evento_ruta", "🌿 Evento Pokémon de Ruta")

if st.session_state.evento_gimnasio:
    dialogo_generico("evento_gimnasio", "🏟️ Evento Antes del Gimnasio")

if st.session_state.evento_medalla:
    dialogo_generico("evento_medalla", "🏅 Evento Después de Medalla")

if st.session_state.ruleta_divina_pendiente:
    dialogo_ruleta_divina()

# =========================
# EFECTOS GUARDADOS
# =========================
st.divider()
st.subheader("📦 Efectos Guardados")

if not st.session_state.efectos_guardados:
    st.markdown("_No tienes efectos guardados_")
else:
    for i, efecto in enumerate(st.session_state.efectos_guardados):
        cols = st.columns([3, 1])
        cols[0].markdown(f"✨ **{efecto}**")

        if cols[1].button("Usar", key=f"usar_efecto_{i}"):
            if efecto == "Control del Destino":
                st.session_state.control_destino = True



            st.session_state.efectos_guardados.pop(i)
            st.rerun()

# =========================
# SIDEBAR – REFERENCIA DE DADOS
# =========================
with st.sidebar:
    st.subheader("💾 Guardado")

    nombre = st.text_input("Nombre de la partida", "run_principal")

    st.subheader("💾 Guardado por Archivo")

    data = get_save_data()
    json_str = json.dumps(data, indent=4, ensure_ascii=False)

    st.download_button(
        label="⬇️ Descargar partida",
        data=json_str,
        file_name="pokeinador_save.json",
        mime="application/json"
    )
    uploaded_file = st.file_uploader(
        "📂 Cargar partida",
        type=["json"]
    )

    if uploaded_file is not None:
        data = json.load(uploaded_file)
        restaurar_estado(data)
        st.success("Partida cargada correctamente")

    st.subheader("☠️ Muerte")
    for k, v in EFECTOS.items():
        st.markdown(f"**{k} – {v[0]}**")
        st.markdown(f"_{v[1]}_")

    st.divider()

    st.subheader("🌿 Ruta")
    for k, v in EFECTOS_RUTA.items():
        st.markdown(f"**{k} – {v[0]}**")
        st.markdown(f"_{v[1]}_")

    st.divider()

    st.subheader("🏟️ Gimnasio")
    for k, v in EFECTOS_GIMNASIO.items():
        st.markdown(f"**{k} – {v[0]}**")
        st.markdown(f"_{v[1]}_")

    st.divider()

    st.subheader("🏅 Medalla")
    for k, v in EFECTOS_MEDALLA.items():
        st.markdown(f"**{k} – {v[0]}**")
        st.markdown(f"_{v[1]}_")

    st.divider()

    st.subheader("✨ Ruleta Divina")
    for k, v in RULETA_DIVINA.items():
        st.markdown(f"**{k} – {v[0]}**")
        st.markdown(f"_{v[1]}_")
    st.divider()
    st.subheader("🔎 Buscador Pokémon")

    lista_pokemon = get_lista_pokemon()

    pokemon_elegido = st.selectbox(
        "Busca un Pokémon",
        options=lista_pokemon,
        index=None,
        placeholder="Empieza a escribir…"
    )

    if pokemon_elegido:
        poke = get_pokemon_full(pokemon_elegido)

        if poke:
            st.markdown(f"### {poke['name']}")
            st.image(poke["sprite"], width=120)

            st.markdown("**Tipos**")
            st.markdown(" / ".join(poke["types"]))

            st.markdown("**Stats Base**")
            for stat, val in poke["stats"].items():
                st.markdown(f"- **{stat}**: {val}")

# =========================
# HISTORIAL
# =========================
st.divider()
st.subheader("📜 Últimos eventos del destino")

if not st.session_state.historial_eventos:
    st.markdown("_Aún no hay eventos registrados_")
else:
    for e in reversed(st.session_state.historial_eventos):
        st.markdown(f"• {e}")
