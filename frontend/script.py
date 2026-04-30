import os
import sys
import streamlit as st
import pandas as pd
import uuid
from redis import Redis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langgraph.checkpoint.redis import RedisSaver
from agents.finance_agent import agent
from tickers.models import Ticker


redis_client = Redis(host='redis', port=6379, db=0, decode_responses=True)


def get_all_sessions():
    # Busca todas as chaves de checkpoint no Redis
    keys = redis_client.keys("checkpoint:*")
    # Extrai o thread_id (ex: checkpoint:usuario_01 -> usuario_01)
    sessions = sorted(list(set([k.split(":")[1] for k in keys])))
    return sessions


st.set_page_config(page_title="Sentinel 2026", layout="wide")

# Sidebar: Gerenciamento de Sessões
with st.sidebar:
    st.title("📂 Sessões")

    if st.button("➕ Nova Conversa"):
        st.session_state.thread_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

    existing_sessions = get_all_sessions()
    selected_session = st.selectbox(
        "Histórico de Conversas",
        ["Selecione..."] + existing_sessions,
        index=0
    )

    if selected_session != "Selecione..." and "thread_id" not in st.session_state:
        st.session_state.thread_id = selected_session



if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "default_user"

st.title(f"🛡️ Sentinel AI - Sessão: {st.session_state.thread_id}")

# --- CHAT INTERFACE ---
# Exibe mensagens do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "chart_data" in msg:
            st.line_chart(msg["chart_data"])


if prompt := st.chat_input("Ex: Qual a tendência da NVDA e mostre o gráfico"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Agent Invoke
    with st.chat_message("assistant"):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        with st.spinner("Sentinel consultando Redis e APIs..."):
            response = agent.invoke({"messages": [("user", prompt)]}, config=config)
            answer = response["messages"][-1].content
            st.markdown(answer)


            chart_to_show = None
            for word in prompt.upper().split():
                ticker_obj = Ticker.objects.filter(symbol=word).first()
                if ticker_obj and ticker_obj.technical_metrics.get('monthly_history'):
                    history = ticker_obj.technical_metrics['monthly_history']
                    df = pd.DataFrame(history)
                    df['price'] = df['price'].astype(float)
                    df = df.set_index('month')
                    st.line_chart(df)
                    chart_to_show = df
                    break

            
            new_msg = {"role": "assistant", "content": answer}
            if chart_to_show is not None:
                new_msg["chart_data"] = chart_to_show
            st.session_state.messages.append(new_msg)