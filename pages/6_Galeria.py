import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

st.title("📸 Galeria")
st.caption("Alguns dos nossos trabalhos")

GALERIA_DIR = Path(__file__).resolve().parent.parent / "assets" / "galeria"
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VID_EXT = {".mp4", ".webm", ".mov"}

if not GALERIA_DIR.exists():
    GALERIA_DIR.mkdir(parents=True, exist_ok=True)

arquivos = sorted(
    [f for f in GALERIA_DIR.iterdir() if f.is_file() and f.suffix.lower() in (IMG_EXT | VID_EXT)],
    key=lambda f: f.stat().st_mtime,
    reverse=True,
)

if not arquivos:
    st.info("📷 Ainda não há trabalhos na galeria. Volte em breve!")
    st.stop()

filtro = st.radio(
    "Filtrar",
    ["Todos", "Imagens", "Vídeos"],
    horizontal=True,
    label_visibility="collapsed",
)

if filtro == "Imagens":
    arquivos = [f for f in arquivos if f.suffix.lower() in IMG_EXT]
elif filtro == "Vídeos":
    arquivos = [f for f in arquivos if f.suffix.lower() in VID_EXT]

if not arquivos:
    st.info("Sem ficheiros para o filtro escolhido.")
    st.stop()

COLS = 3
cols = st.columns(COLS, gap="medium")
for i, f in enumerate(arquivos):
    with cols[i % COLS]:
        try:
            if f.suffix.lower() in IMG_EXT:
                st.image(str(f), use_container_width=True)
            else:
                st.video(str(f))
        except Exception as e:
            st.warning(f"Não foi possível mostrar {f.name}: {e}")
            continue
        nome_limpo = f.stem.replace("_", " ").replace("-", " ").title()
        st.caption(f"✂️ {nome_limpo}")

st.divider()
st.caption(f"Total: {len(arquivos)} trabalho(s)")
