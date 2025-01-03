__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import tempfile
import os
import streamlit as st
from loaders import carrega_pdf
from crew import cria_agente_e_tarefa, executar_crew
from dotenv import find_dotenv, load_dotenv

# Configuração de variáveis do ambiente
#st.session_state['api_key_openai'] = os.environ['OPENAI_API_KEY']
#api_key = os.environ['OPENAI_API_KEY']

_ = load_dotenv(find_dotenv())
st.session_state['GEMINI_MODEL_NAME'] = 'gemini-1.5-pro'
st.session_state['api_key'] = os.environ['GEMINI_API_KEY']

if not st.session_state['api_key']:
    st.warning("A chave de API (GOOGLE_API_KEY) não está configurada!")
    
def carrega_arquivos(arquivo):
    """Carrega o conteúdo do PDF usando loaders.py"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
        temp.write(arquivo.read())
        nome_temp = temp.name
    documento = carrega_pdf(nome_temp)  # Extrai o conteúdo do PDF
    return documento

def sidebar():
    """Configura a barra lateral para upload de arquivos e descrição da vaga"""
    st.title("📝 Currículo Turbinado - versão para PC / tablet")
    st.write("É necessário estar de acordo com os [termos de uso](https://docs.google.com/document/d/1OnjIfC-qA5z30is8OgmNp149IxMW2xs3QJglKZx9knY/edit?usp=sharing) para continuar")
    agree = st.radio("Você concorda com os termos de uso?", options=["Não", "Sim"])        
    
    #st.markdown("\n\n")
    #st.markdown("Estamos revisando o app para fazer algumas melhorias. Se quiser falar com a gente, mande um email para bernardo@iafacil.tech. Obrigado!")

    if agree == "Sim":
        st.subheader("Preencha aqui suas informações profissionais e da vaga")
        curriculo = st.file_uploader('Faça o upload do currículo em PDF', type=['pdf'])
        linkedin = st.file_uploader('Faça o upload do perfil do LinkedIn em PDF', type=['pdf'])
        st.markdown("[Instruções para baixar pdf do LinkedIn](https://www.youtube.com/watch?v=elBUCn_TRzY)")
        descricao_vaga = st.text_area('Insira a descrição da vaga desejada e aperte ctrl+enter:', height=300)
        
        st.session_state['uploaded_curriculo'] = curriculo
        st.session_state['uploaded_linkedin'] = linkedin
        st.session_state['descricao_vaga'] = descricao_vaga
        st.markdown("<h1 style='font-size: 12px'>Desenvolvido por</h1>", unsafe_allow_html=True)
        st.image('https://media.licdn.com/dms/image/v2/D4D0BAQELTl5xA91RHg/company-logo_100_100/company-logo_100_100/0/1727325533304?e=1738195200&v=beta&t=KjuBnUerdDgR1tBShcdpP_PSXiKyT9ju3fUW4n5yGQM', width=100)
        st.markdown("<h6 style='font-size: 12px'>Nos siga nas redes!</h1>", unsafe_allow_html=True)
        st.markdown("""
        <a href="https://www.instagram.com/facilit.ai_/" target="_blank">
            <img src="https://cdn.icon-icons.com/icons2/2845/PNG/512/instagram_logo_icon_181283.png" 
                style="width: 50px; 
                    height: auto; 
                    cursor: pointer;
                    border-radius: 10px;"
                />
            </a>
        """, unsafe_allow_html=True)
        st.markdown("""
        <a href="https://www.linkedin.com/company/105124305/" target="_blank">
            <img src="https://img.icons8.com/win10/512/linkedin.png" 
                style="width: 50px; 
                    height: auto; 
                    cursor: pointer;
                    border-radius: 10px;"
                />
            </a>
        """, unsafe_allow_html=True)
    else:
        st.warning("Você precisa aceitar os termos de uso para acessar o app.")

def pagina_principal():

    curriculo = st.session_state.get('uploaded_curriculo', None)
    linkedin = st.session_state.get('uploaded_linkedin', None)
    vaga = st.session_state.get('descricao_vaga', "").strip()
    
    if curriculo and linkedin and vaga:
        if st.button(f'Turbinar currículo! Clique 1x e aguarde 1 minuto', type="primary"):
            curriculo_texto = carrega_arquivos(curriculo)
            linkedin_texto = carrega_arquivos(linkedin)
            #researcher, profiler, resume_strategist, interview_preparer, research_task, profile_task, resume_strategy_task, interview_preparation_task = cria_agente_e_tarefa(curriculo_texto, linkedin_texto, vaga)
            researcher, profiler, resume_strategist, research_task, profile_task, resume_strategy_task = cria_agente_e_tarefa(curriculo_texto, linkedin_texto, vaga)
            #agentes = [researcher, profiler, resume_strategist, interview_preparer]
            agentes = [researcher, profiler, resume_strategist]
            #tarefas = [research_task, profile_task, resume_strategy_task, interview_preparation_task]
            tarefas = [research_task, profile_task, resume_strategy_task]
            resultado = executar_crew(agentes, tarefas)
            exibir_resultados(resultado)              
            
    else:
        st.info("A interface é melhor no PC ou tablet. Se for usar no celular, clique na seta > para abrir o menu lateral", icon=":material/computer:")
        st.info("Faça o upload dos arquivos pdf e cole a descrição da vaga para iniciar a análise.", icon=":material/download:")
        st.info("Não se esqueça de apertar ctrl+enter para salvar a descrição da vaga, depois de colar o texto.",icon=":material/keyboard:")

def exibir_resultados(resultado):
    """Função para formatar e exibir o resultado no Streamlit."""
    st.markdown("### Sugestões de Melhorias no Currículo")
    st.divider()

    # Dividir o texto em seções
    sugestoes = resultado.raw.split("\n\n")  # Dividir por quebras de linha duplas
    for sugestao in sugestoes:
        linhas = sugestao.splitlines()
        if linhas:
            # Exibir a seção como título (sem numeração)
            titulo = linhas[0].replace("#", "").strip()  # Remove os `#` do título
            st.markdown(f"**{titulo}**")

            # Exibir os detalhes (remover bullets duplicados e ajustar formato)
            for linha in linhas[1:]:
                if "Melhoria Sugerida:" in linha or "Texto Revisto:" in linha:
                    st.markdown(f"- {linha.strip()}")  # Um único bullet
                elif linha.strip():  # Outras linhas de texto
                    st.markdown(f"  {linha.strip()}")
    st.divider()

def main():
    """Função principal do aplicativo Streamlit"""
    with st.sidebar:
        sidebar()
    pagina_principal()

if __name__ == '__main__':
    main()
