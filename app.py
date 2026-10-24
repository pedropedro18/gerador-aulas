import time
import requests
import streamlit as st

st.set_page_config(page_title="Gerador de Aulas")
st.title("Gerador de Aulas - Teacher Pedro")

NIVEIS = ["A1", "A2", "B1", "B2", "C1", "C2"]
FOCOS = ["Vocabulary", "Grammar", "Speaking", "Listening", "Reading", "Writing"]

MODELOS = [
    st.secrets.get("GEMINI_MODEL", "gemini-3.8-flash"),
    st.secrets.get("GEMINI_MODEL_RESERVA", "gemini-3.5-flash-lite"),
]
TEMPORARIOS = (429, 500, 503, 504)


def montar_prompt(nivel, tema, foco, alunos):
    turma = f"Turma: {alunos}\n" if alunos else ""
    return f"""Escreve uma aula de inglês completa e pronta a usar.
É o conteúdo da aula, não um plano de aula: não incluas durações, minutos nem fases como warm-up.

Nível CEFR: {nivel}
Tema: {tema}
Foco: {foco}
{turma}
Estrutura:
1. Título da aula
2. Conteúdo principal (vocabulário, regra ou texto, conforme o foco), com explicação clara.
   Se o nível for A1 ou A2, explica em português.
3. Exemplos (8 frases)
4. Exercícios (10 exercícios variados)
5. Soluções dos exercícios (para o professor)

Usa linguagem adequada ao nível {nivel} e não inventes factos."""


def chamar_gemini(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        raise RuntimeError("GEMINI_API_KEY não está nos Secrets")
    chave = st.secrets["GEMINI_API_KEY"]
    ultimo_erro = None

    for modelo in MODELOS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        for t in range(3):
            try:
                r = requests.post(
                    url,
                    headers={"x-goog-api-key": chave},
                    json={
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": {"maxOutputTokens": 4000},
                    },
                    timeout=60,
                )
                if r.ok:
                    partes = r.json()["candidates"][0]["content"]["parts"]
                    texto = "".join(p.get("text", "") for p in partes).strip()
                    if texto:
                        return texto
                    ultimo_erro = RuntimeError("Resposta vazia")
                else:
                    ultimo_erro = RuntimeError(f"{modelo} devolveu {r.status_code}")
                    if r.status_code not in TEMPORARIOS:
                        break
            except (requests.RequestException, KeyError, IndexError) as e:
                ultimo_erro = e
            if t < 2:
                time.sleep(3 * (t + 1))
    raise ultimo_erro


nivel = st.selectbox("Nível", NIVEIS)
tema = st.text_input("Tema da aula", placeholder="Ex: Verb to be")
foco = st.selectbox("Foco principal", FOCOS)
alunos = st.text_input("Turma / alunos (opcional)")

if st.button("Gerar aula", type="primary"):
    if not tema.strip():
        st.warning("Escreve o tema da aula.")
    else:
        try:
            with st.spinner("A preparar a aula..."):
                aula = chamar_gemini(montar_prompt(nivel, tema.strip(), foco, alunos.strip()))
            st.markdown(aula)
            st.download_button(
                "Descarregar (.txt)",
                aula,
                file_name=f"aula_{nivel}{tema.strip().replace(' ', '')}.txt",
            )
        except Exception as e:
            print(e)
            st.error("Não consegui gerar a aula agora. Tenta outra vez daqui a pouco.")