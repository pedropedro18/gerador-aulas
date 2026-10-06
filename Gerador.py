import json
import streamlit as st
from anthropic import Anthropic
from fpdf import FPDF

st.set_page_config(page_title="Gerador de aulas", page_icon="📘")
MODELO = "claude-sonnet-5-5"


def gerar_aula(nivel, tema):
    client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    prompt = f"""Cria uma aula de inglês para um aluno de nível CEFR {nivel} sobre o tema: "{tema}".
Responde SÓ com JSON válido, sem texto antes ou depois, neste formato:
{{"titulo": "...",
 "vocab": [{{"en": "...", "pt": "..."}}],
 "explicacao": "explicação em português de Angola, clara e curta",
 "exemplos": ["frase em inglês"],
 "dialogo": ["A: ...", "B: ..."],
 "exercicios": [{{"frase": "frase em inglês com _", "resposta": "..."}}],
 "fala": "tarefa de conversação em português"}}
Regras: 8 palavras de vocabulário, 4 exemplos, diálogo de 6 falas, 8 exercícios de completar.
O inglês deve ser adequado ao nível {nivel}. Usa só aspas rectas."""
    r = client.messages.create(
        model=MODELO,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = r.content[0].text.strip()
    texto = texto.replace("json", "").replace("", "").strip()
    return json.loads(texto)


def limpar(t):
    return str(t).encode("latin-1", "replace").decode("latin-1")


def criar_pdf(aula, nivel, solucoes):
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    def linha(txt, estilo="", tam=11):
        pdf.set_font("Helvetica", estilo, tam)
        pdf.multi_cell(0, 6, limpar(txt), new_x="LMARGIN", new_y="NEXT")

    linha(f"{aula['titulo']} ({nivel})", "B", 16)
    pdf.ln(3)
    linha("1. Vocabulary", "B", 13)
    for v in aula["vocab"]:
        linha(f"- {v['en']}  =  {v['pt']}")
    pdf.ln(3)
    linha("2. Explicacao", "B", 13)
    linha(aula["explicacao"])
    for e in aula["exemplos"]:
        linha(f"  * {e}")
    pdf.ln(3)
    linha("3. Dialogue", "B", 13)
    for d in aula["dialogo"]:
        linha(d)
    pdf.ln(3)
    linha("4. Exercises", "B", 13)
    for i, ex in enumerate(aula["exercicios"], 1):
        linha(f"{i}. {ex['frase']}")
    pdf.ln(3)
    linha("5. Speaking", "B", 13)
    linha(aula["fala"])
    if solucoes:
        pdf.add_page()
        linha("Solucoes (professor)", "B", 14)
        for i, ex in enumerate(aula["exercicios"], 1):
            linha(f"{i}. {ex['resposta']}")
    return bytes(pdf.output())


st.title("Gerador de aulas")
st.write("Escolhe o nível e escreve o tema que queres aprender. A aula é criada automaticamente.")

nivel = st.selectbox("Nível", ["A1", "A2", "B1", "B2", "C1", "C2"])
tema = st.text_input("Tema", placeholder="Ex.: futebol, no restaurante, Present perfect")
solucoes = st.checkbox("Incluir soluções", value=True)

if st.button("Gerar aula", type="primary"):
    if not tema.strip():
        st.warning("Escreve um tema.")
    else:
        with st.spinner("A criar a tua aula..."):
            try:
                st.session_state["aula"] = gerar_aula(nivel, tema.strip())
                st.session_state["nivel"] = nivel
            except Exception:
                st.error("Não foi possível gerar a aula. Tenta outra vez.")

aula = st.session_state.get("aula")
if aula:
    n = st.session_state["nivel"]
    st.header(f"{aula['titulo']} ({n})")
    st.subheader("1. Vocabulary")
    for v in aula["vocab"]:
        st.write(f"{v['en']} - {v['pt']}")
    st.subheader("2. Explicação")
    st.write(aula["explicacao"])
    for e in aula["exemplos"]:
        st.write(f"- {e}")
    st.subheader("3. Dialogue")
    for d in aula["dialogo"]:
        st.write(d)
    st.subheader("4. Exercises")
    for i, ex in enumerate(aula["exercicios"], 1):
        st.write(f"{i}. {ex['frase']}")
    st.subheader("5. Speaking")
    st.write(aula["fala"])
    if solucoes:
        with st.expander("Soluções"):
            for i, ex in enumerate(aula["exercicios"], 1):
                st.write(f"{i}. {ex['resposta']}")
    st.download_button(
        "Descarregar PDF",
        criar_pdf(aula, n, solucoes),
        file_name="aula.pdf",
        mime="application/pdf",
    )