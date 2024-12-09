from crewai import Agent, Task, Crew

def cria_agente_e_tarefa(curriculo, linkedin, vaga):
    """Cria os agentes e as tarefas para análise, com base na descrição da vaga"""
    # Definir os agentes
    researcher = Agent(
        role="Pesquisador de Vagas de Emprego",
        goal="Certifique-se de realizar análises criteriosas em anúncios de vagas para ajudar candidatos a emprego",
        verbose=True,
        llm='gemini/gemini-1.5-pro',
        backstory=(
        "Como Pesquisador de Vagas, sua habilidade em "
        "extrair informações críticas "
        "de uma vaga de emprego de emprego é incomparável. "
        "Suas competências ajudam a identificar as qualificações "
        "e habilidades necessárias procuradas pelos empregadores, "
        "formando a base para a personalização eficaz de candidaturas."
        )
    )
    
    profiler = Agent(
    role="Especialista em criação de perfil profissional",
    goal="Realizar pesquisas sobre candidatos a emprego "
    "com o objetivo de ajudá-los a se destacar na seleção pra vaga de emprego",
    verbose=True,
    llm='gemini/gemini-1.5-pro',
    backstory=(
    "Equipado com habilidades analíticas, você "
    "sintetiza informações do CV e perfil do linkedin para criar "
    "um perfil profissional abrangente, estabelecendo "
    "a base para aprimoramentos personalizados de currículo."
        )
    )

    resume_strategist = Agent(
    role="Estrategista de Currículos",
    goal="Encontrar as melhores maneiras de fazer um "
    "currículo se destacar para a vaga de interesse do profissional.",
    verbose=True,
    llm='gpt-4o-mini',
    backstory=(
    "Com uma mente estratégica e atenção aos detalhes, você "
    "se destaca ao refinar currículos para destacar as habilidades "
    "e experiências mais relevantes, garantindo que eles "
    "atendam os requisitos da vaga. Use as informações disponíveis e faça sugestões práticas"
    "com base no que o usuário já tem no seu currículo e perfil profissional."
        )
    )

    #interview_preparer = Agent(  
    #role="Especialista de RH - Preparador de Entrevistas",  
    #goal="Criar perguntas de entrevista e pontos de discussão "  
    #     "com base no currículo, perfil do candidato e nos requisitos da vaga",  
    #verbose=True,  
    #backstory=(  
    #    "Seu papel é crucial para antecipar a dinâmica das entrevistas. "  
    #    "Com seu conhecimento do mundo de recrutamento e seleção, e habilidade de formular perguntas-chave e pontos de discussão, "  
    #    "você prepara o candidato para o sucesso, garantindo que eles "  
    #    "possam abordar com confiança todos os aspectos da vaga à qual estão se candidatando."  
    #    )  
    #)

    # Descrição das tarefas considerando os documentos e a vaga
    research_task = Task(
        description=(
            "Analise o texto da descrição de vaga fornecido, extraindo as principais habilidades, experiências e qualificações exigidas"
            f"\n\n"
            f"Descrição da Vaga: \n\n{vaga}\n\n"            
        ),
        llm='gemini/gemini-1.5-pro',
        expected_output=(
            "Uma lista estruturada de requisitos da vaga, incluindo as habilidades, qualificações e experiências necessárias."
        ),
        agent=researcher
    )

    profile_task = Task(
        description=(
            "Consolide um perfil profissional detalhado usando o CV e o perfil do LinkedIn fornecidos a seguir."
            f"\n\n"
            f"Currículo: \n\n{curriculo}\n\n"
            f"Perfil do LinkedIn: \n\n{linkedin}\n\n"        
            "Extrair e sintetizar as informações mais relevantes dessas fontes."
        ),
        llm='gemini/gemini-1.5-pro',
        expected_output=(
            "Um documento de perfil abrangente que inclua as habilidades do profissional, "
            "experiências e impacto das funções e projetos que participou, interesses de carreira e "
            "estilo de comunicação, de acordo com os dados fornecidos."
        ),
        agent=profiler,
        async_execution=False  # síncrono
    )
    
    resume_strategy_task = Task(
    description=(
        "Usando o perfil e os requisitos da vaga obtidos em "
        "tarefas anteriores, personalize o currículo para destacar as áreas "
        "mais relevantes. Utilize ferramentas para ajustar e aprimorar "
        "o conteúdo do currículo. Certifique-se de que este seja o melhor "
        "currículo possível, respeitando as fontes de informação fornecidas."
        "Deixe claras as sugestões de melhoria do currículo e o porquê dessa sugestão ter sido dada, "
        "apontando melhorias para todas as seções, incluindo o resumo inicial, experiência profissional, "
        "habilidades e educação, tudo para refletir melhor as habilidades "
        "do candidato e como elas se alinham ao anúncio da vaga."
    ),
    llm='gpt-4o-mini',
    expected_output=(
        "Uma lista em português, visual e clara, em tópicos, usando markdown, "
        "de melhorias de currículo sugeridas, com o objetivo de destacar de forma eficaz as qualificações "
        "e experiências do candidato mais relevantes para a vaga em questão. Para cada melhoria, explique sucintamente o racional"
        "e como essa melhoria está alinhada com a vaga desejada pelo profissional."
    ),
    context=[research_task, profile_task],  # declara tasks como contexto
    agent=resume_strategist,  # assíncrono, pois espera tasks 1 e 2
    async_execution=True
    )

    # interview_preparation_task = Task(
    # description=(
    #     "Crie um conjunto de possíveis perguntas de entrevista e pontos "
    #     "de discussão com base no currículo personalizado e nos requisitos "
    #     "da vaga. Gere perguntas e pontos de discussão "
    #     "relevantes. Certifique-se de que essas perguntas e pontos de discussão "
    #     "ajudem o candidato a destacar os principais pontos do currículo e como "
    #     "eles se alinham ao anúncio da vaga."
    # ),
    # expected_output=(
    #     "Um documento contendo as principais perguntas e pontos de discussão "
    #     "que o candidato deve preparar para a entrevista inicial."
    # ),
    # context=[research_task, profile_task, resume_strategy_task],
    # agent=interview_preparer
    # )        

    #return researcher, profiler, resume_strategist, interview_preparer, research_task, profile_task, resume_strategy_task, interview_preparation_task
    return researcher, profiler, resume_strategist, research_task, profile_task, resume_strategy_task

def executar_crew(agentes, tarefas):
    """Executa o Crew com os agentes e as tarefas configurados"""
    crew = Crew(
        agents=agentes,
        tasks=tarefas
        
    )
    resultado = crew.kickoff()
    return resultado