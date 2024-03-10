# Tale Genius

Tale Genius é um aplicativo Streamlit que gera um vídeo educacional baseado em texto ou imagem fornecida pelo usuário. O aplicativo usa várias APIs, incluindo a API Gemini para geração de texto, a API Eleven Labs para geração de áudio e a API OpenAI para geração de imagens.

## Como usar

1. Clone este repositório para sua máquina local.
2. Instale as dependências necessárias usando `pip install -r requirements.txt`.
3. Execute o aplicativo Streamlit usando `streamlit run streamlit_app.py`.
4. No aplicativo Streamlit, você pode selecionar o estilo de imagem, a quantidade de cenas, a opção de entrada e fornecer as chaves da API necessárias.
5. O aplicativo irá gerar um vídeo educacional baseado nas opções selecionadas.

## Opções de entrada

- Texto: Você pode fornecer um texto para gerar um vídeo educacional.
- Câmera: Você pode tirar uma foto para gerar um vídeo educacional.
- Arquivo de imagem: Você pode fazer upload de um arquivo de imagem para gerar um vídeo educacional.

## Dependências

- google.generativeai
- streamlit
- json
- os
- requests
- io
- PIL
- openai
- elevenlabs
- IPython

## Chaves da API

Você precisará fornecer suas próprias chaves da API para as seguintes APIs:

- Gemini
- Eleven Labs
- OpenAI

Por favor, obtenha suas chaves da API dos respectivos provedores de API.

## Contribuindo

Contribuições são bem-vindas! Por favor, sinta-se à vontade para abrir um problema ou solicitação pull.
