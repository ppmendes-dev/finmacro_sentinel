# Sentinel 2026: AI Financial Intelligence Agent

O **Sentinel 2026** é um agente autônomo projetado para análise macroeconômica e monitoramento de ativos em tempo real. Diferente de chatbots convencionais, o Sentinel utiliza uma arquitetura de microserviços orquestrada via Docker, focada em persistência de dados de longo prazo (RAG) e otimização de custos operacionais.

---

##  Arquitetura e Fluxo de Dados

O sistema foi desenhado para ser resiliente e escalável, dividindo-se em três pilares fundamentais:

### 1. Ferramentas via MCP (Model Context Protocol)
O Sentinel utiliza o protocolo **MCP** para desacoplar a lógica de negócio das capacidades do LLM. Isso permite que o agente invoque ferramentas externas de forma padronizada:
* **Market Data Tool:** Acesso a tickers, preços históricos e métricas técnicas via Finnhub e Alpha Vantage.
* **Search Tool:** Integração com Tavily/Exa para varredura de notícias macroeconômicas e sentimentos de mercado.
* **Vantagem:** O LLM não precisa "adivinhar" dados; ele requisita informações precisas através de uma interface de controle rigorosa.

### 2. Memória de Longo Prazo e RAG (Retrieval-Augmented Generation)
Para evitar a dependência exclusiva de dados em tempo real (que consomem APIs externas), o Sentinel implementa uma camada de **RAG**:
* **Persistência:** Todos os dados relevantes obtidos durante as consultas são processados e armazenados em um banco **PostgreSQL** com a extensão **PGVector**.
* **Recuperação Semântica:** Antes de realizar uma nova busca paga na web, o agente consulta sua própria base de conhecimentos vetorial para verificar se já possui informações históricas ou análises prévias sobre o ativo solicitado.

### 3. Gestão de Sessão e Eficiência de Custos (Redis Stack)
Um dos maiores desafios de agentes de IA é o custo do "Context Window". O Sentinel resolve isso utilizando **Redis Stack**:
* **Checkpoints de Estado:** Através do `RedisSaver` (LangGraph), o estado completo da conversa é persistido em formato JSON no Redis.
* **Economia de Créditos:** Ao manter a sessão ativa no Redis, o agente não precisa reenviar todo o histórico da conversa a cada nova interação. Ele recupera o `thread_id`, carrega o contexto localmente e envia apenas o diferencial para a API do Gemini, reduzindo drasticamente o consumo de tokens e evitando chamadas redundantes.

---

##  Stack Tecnológica

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **LLM** | Google Gemini 1.5 Flash | Cérebro e raciocínio lógico |
| **Orquestração de IA** | LangChain & LangGraph | Grafo de estados e controle de fluxo |
| **Banco de Dados** | PostgreSQL + PGVector | Armazenamento de dados e busca vetorial |
| **Cache & Memória** | Redis Stack | Persistência de sessão e checkpoints |
| **Interface** | Streamlit | Dashboard interativo e chat |
| **Infraestrutura** | Docker & Docker Compose | Containerização e padronização de ambiente |

---

##  Como Executar

### Pré-requisitos
* Docker e Docker Compose instalados.
* Chave de API do Google Gemini e Tavily (configuradas no arquivo `.env`).

### Inicialização
1.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/fin_macro_sentinel.git
    cd fin_macro_sentinel
    ```
2.  **Configurar Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz com suas chaves de API.
3.  **Subir os containers:**
    ```bash
    docker compose up --build -d
    ```
4.  **Configurar o Banco de Dados (Primeira execução):**
    ```bash
    docker exec -it sentinel-app python manage.py migrate
    ```
5.  **Acessar a Plataforma:**
    Abra o navegador em `http://localhost:8501`.

---

##  Diferenciais de Engenharia
* **Resiliência:** Tratamento de erros de API (429/503) com políticas de retry via `tenacity`.
* **Observabilidade:** Interface visual via **RedisInsight** (porta 8001) para monitorar o estado dos checkpoints em tempo real.
* **Hot-Reload:** Desenvolvimento facilitado com volumes Docker que permitem alteração no código sem reiniciar os containers.