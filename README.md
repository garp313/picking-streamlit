---
title: Picking & Arrumação Hub
emoji: 📦
colorFrom: purple
colorTo: blue
sdk: streamlit
app_file: app.py
pinned: false
---

# 📦 Picking & Arrumação Hub

Este projeto é uma ferramenta de sincronização, exportação de inventário e analytics para operações de picking. Ele contém uma interface web interativa desenvolvida em **Streamlit** e um script CLI para automatização rápida.

---

## 🚀 Como hospedar no Hugging Face Spaces

O Hugging Face Spaces suporta Streamlit de forma nativa. Siga as instruções abaixo para hospedar seu app de graça:

### Método 1: Pela Interface Web (Mais Fácil)
1. Crie uma conta em [Hugging Face](https://huggingface.co/) (se já não tiver).
2. Vá em **Spaces** e clique em **Create new Space**.
3. Defina um nome para seu Space (ex: `picking-hub`).
4. Selecione **Streamlit** como o SDK.
5. Escolha a licença e clique em **Create Space**.
6. Na aba **Files**, clique em **Add file** -> **Upload files**.
7. Envie os arquivos essenciais do projeto:
   - `app.py`
   - `requirements.txt`
   - `README.md`
8. Salve e commit. O Hugging Face irá compilar e abrir seu app em poucos instantes!

---

## 💻 Como Rodar Localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o Dashboard Web:
   ```bash
   streamlit run app.py
   ```

3. Execute o script CLI:
   ```bash
   python automatizacao_picking_arrumacao.py
   ```