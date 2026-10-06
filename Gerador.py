import streamlit as st
from ddgs import DDGS

st.set_page_config(page_title="Pesquisar Aulas - Teacher Pedro", page_icon="📚")

NIVEIS = ["Qualquer", "A1", "A2", "B1", "B2", "C1", "C2"]
TIPOS = {
    "Todas": "lesson",
    "Plano de aula": "lesson plan",
    "Ficha / exercícios": "worksheet exercises",
    "Vídeo": "video lesson",
}


def pesquisar(tema, nivel, tipo, n=10):
    partes = [tema, "English", TIPOS[tipo]]
    if nivel != "Qualquer":
        partes.append(nivel)
    consulta = " ".join(partes)
    with DDGS() as ddgs:
        return list(ddgs.text(consulta, max_results=n))


st.title("📚 Pesquisar Aulas - Teacher Pedro")
st.write("Escreve o título da aula que procuras e encontra aulas de inglês já feitas.")

tema = st.text_input("Título da aula", placeholder="Ex: verb to be")
col1, col2 = st.columns(2)
nivel = col1.selectbox("Nível", NIVEIS)
tipo = col2.selectbox("Tipo", list(TIPOS.keys()))

if st.button("Pesquisar aulas", type="primary"):
    if not tema.strip():
        st.warning("Escreve primeiro o título da aula.")
    else:
        with st.spinner("A pesquisar..."):
            try:
                st.session_state["res"] = pesquisar(tema.strip(), nivel, tipo)
            except Exception as e:
                st.session_state["res"] = []
                st.error(f"Não foi possível pesquisar agora: {e}")

if "res" in st.session_state:
    st.divider()
    if not st.session_state["res"]:
        st.info("Sem resultados. Tenta outro título.")
    for r in st.session_state["res"]:
        st.markdown(f"### [{r['title']}]({r['href']})")
        st.write(r["body"])
        st.caption(r["href"])