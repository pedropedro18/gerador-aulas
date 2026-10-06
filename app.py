import streamlit as st

st.set_page_config(page_title="Gerador de Aulas", page_icon="📚")
st.title("📚 Gerador de Aulas - Teacher Pedro")

NIVEIS = ["A1", "A2", "B1", "B2", "C1", "C2"]
FOCOS = ["Vocabulary", "Grammar", "Speaking", "Listening", "Reading", "Writing"]

nivel = st.selectbox("Nível", NIVEIS)
tema = st.text_input("Tema da aula", placeholder="Ex: Daily routines")
foco = st.selectbox("Foco principal", FOCOS)
duracao = st.slider("Duração (minutos)", 30, 120, 60, step=15)
alunos = st.text_input("Turma / alunos (opcional)")

ATIVIDADES = {
    "Vocabulary": "Flashcards, matching words/pictures, gap-fill with the new words.",
    "Grammar": "Examples on the board, rule discovery, controlled practice, sentence building.",
    "Speaking": "Pair work, role-play, short presentations, class discussion.",
    "Listening": "Pre-listening questions, listen twice, true/false, discuss answers.",
    "Reading": "Skim for gist, scan for details, vocabulary from context, comprehension questions.",
    "Writing": "Model text, guided planning, write a short text, peer correction.",
}

def gerar_aula(nivel, tema, foco, duracao, alunos):
    t = max(duracao, 30)
    aquecimento = round(t * 0.10)
    apresentacao = round(t * 0.25)
    pratica = round(t * 0.30)
    producao = round(t * 0.25)
    fecho = t - aquecimento - apresentacao - pratica - producao

    return f"""PLANO DE AULA
Nível: {nivel} | Tema: {tema} | Foco: {foco} | Duração: {t} min
{"Turma: " + alunos if alunos else ""}

OBJETIVOS
- No final da aula, os alunos conseguem usar {foco.lower()} relacionado com "{tema}" ao nível {nivel}.

1. WARM-UP ({aquecimento} min)
- Perguntas rápidas e jogo curto sobre "{tema}".

2. PRESENTATION ({apresentacao} min)
- Introduzir o conteúdo novo: {ATIVIDADES[foco]}

3. PRACTICE ({pratica} min)
- Exercícios controlados (individual e em pares) sobre "{tema}".

4. PRODUCTION ({producao} min)
- Atividade livre: os alunos usam a língua em situação real ou simulada.

5. WRAP-UP ({fecho} min)
- Revisão, correção de erros comuns e feedback.

TPC (HOMEWORK)
- 5 frases ou um pequeno texto sobre "{tema}" ({nivel}).
"""

if st.button("Gerar aula", type="primary"):
    if not tema.strip():
        st.warning("Escreve o tema da aula.")
    else:
        aula = gerar_aula(nivel, tema.strip(), foco, duracao, alunos.strip())
        st.text_area("Plano gerado", aula, height=450)
        st.download_button("⬇️ Descarregar (.txt)", aula,
                           file_name=f"aula_{nivel}{tema.strip().replace(' ', '')}.txt")