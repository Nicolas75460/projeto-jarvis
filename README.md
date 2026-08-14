# 🤖 J.A.R.V.I.S. — Assistente de Voz & Texto para Windows

Software desktop nativo em Python inspirado no assistente **J.A.R.V.I.S.** do Homem de Ferro. Controla o seu notebook através de **comandos de voz** e **comandos digitados** em Português do Brasil com interface gráfica futurista.

---

## 🚀 Como Iniciar

1. **Pelo arquivo executável rápido**:
   - Dê um duplo clique no arquivo [`start.bat`](file:///c:/Users/nicol/OneDrive/Documentos/C%C3%B3digos(Variados)/jarvis/start.bat)

2. **Pelo terminal / PowerShell**:
   ```powershell
   cd "c:\Users\nicol\OneDrive\Documentos\Códigos(Variados)\jarvis"
   python main.py
   ```

---

## ⌨️ Como Usar (Voz ou Texto)

- **Por Voz**: Clique no botão `🎤 Ativar Voz` e fale naturalmente. O Jarvis detectará quando você terminar de falar.
- **Por Texto**: Digite seu comando na barra de entrada inferior e pressione **Enter** (ou clique no botão `Enviar ➔`).

---

## 🎙️ Exemplos de Comandos Suportados (Voz ou Texto)

| Categoria | Exemplo de Frase / Digitação | O que o Jarvis faz |
| :--- | :--- | :--- |
| **💡 Possibilidades & Ajuda** | *"quais possibilidades você tem?"*<br>*"o que você pode fazer?"*<br>*"quais são as opções?"* | Lista detalhadamente todas as categorias, comandos e exemplos suportados |
| **❓ Perguntas Abrangentes** | *"abra um navegador"*<br>➔ Jarvis: *"Prefere Chrome, Edge ou Firefox?"*<br>➔ Você: *"o Chrome"* | Identifica comandos com múltiplas escolhas e pergunta qual opção você deseja |
| **🖱️ Rolagem (Scroll)** | *"rolar para baixo"* (ou *"descer a página"*...)<br>*"rolar para cima"* (ou *"subir a tela"*...) | Move o scroll do mouse para cima ou para baixo |
| **❌ Fechar Aplicativos** | *"feche o bloco de notas"*<br>*"fechar o chrome"*<br>*"fechar janela atual"* | Encerra o aplicativo especificado ou fecha a janela ativa |
| **⌨️ Teclas & Confirmação** | *"enter"* ou *"dar enter"*<br>*"esc"* ou *"cancelar"*<br>*"tab"*<br>*"espaço"* | Pressiona a respectiva tecla no teclado |
| **✂️ Apagar & Corrigir Texto** | *"apagar"* ou *"apague o caractere"*<br>*"apagar última palavra"*<br>*"apagar 5 caracteres"* (ou *"apague dez letras"*...)<br>*"apagar tudo"* | Apaga 1 caractere, a última palavra inteira, N caracteres específicos ou todo o texto |
| **📋 Atalhos Úteis** | *"selecionar tudo"*<br>*"copiar"*<br>*"colar"*<br>*"desfazer"*<br>*"salvar"* | Executa atalhos `Ctrl+A`, `Ctrl+C`, `Ctrl+V`, `Ctrl+Z`, `Ctrl+S` |
| **✍️ Digitação Autônoma** | *"escreva Olá, este é um relatório importante"* | Digita o texto automaticamente no aplicativo que estiver focado na tela |
| **🌐 Navegação & Sites** | *"abra o YouTube"*<br>*"abra o ChatGPT"*<br>*"entre no GitHub"* | Abre o site diretamente no seu navegador padrão |
| **🔍 Pesquisa na Web** | *"pesquise sobre inteligência artificial"*<br>*"busque notícias de hoje"* | Pesquisa no Google e exibe os resultados |
| **💻 Aplicativos** | *"abra o Bloco de Notas"*<br>*"abra o Google Chrome"*<br>*"abra a Calculadora"*<br>*"abra o VS Code"* | Abre programas instalados no Windows |
| **📁 Gerenciamento de Arquivos** | *"liste meus documentos"*<br>*"liste os arquivos da área de trabalho"*<br>*"abra o arquivo teste.py"* | Lista arquivos e pastas locais e abre arquivos solicitados |
| **📸 Captura de Tela** | *"tire um print da tela"* | Tira um print do desktop e salva em `Imagens/Screenshots_Jarvis/` |
| **🕒 Data e Hora** | *"que horas são?"*<br>*"que dia é hoje?"* | Fala as horas e a data formatada em português |
| **⚡ Status do Sistema** | *"como está o sistema?"* | Informa uso de CPU, memória RAM, disco e bateria |
| **🔊 Controle de Volume** | *"aumente o volume"*<br>*"diminua o volume"*<br>*"mutar o som"* | Ajusta o volume do Windows |
| **🔌 Energia** | *"desligar o computador"*<br>*"reiniciar o computador"* | Executa contagem de 30s de segurança antes de desligar/reiniciar |

---

## 🛠️ Tecnologias Utilizadas

- **Interface Gráfica**: `CustomTkinter` + `tkinter.Canvas` com tema dark futurista e animações inspiradas no reator ARC.
- **Captura de Voz (STT)**: `sounddevice` + `SpeechRecognition` (Google Speech API em PT-BR) sem depender de compiladores C++.
- **Síntese de Voz (TTS)**: `pyttsx3` com voz nativa do Windows (Microsoft Maria / Daniel PT-BR).
- **Automação do Windows**: `pyautogui`, `subprocess`, `psutil`, `webbrowser`, `os`.
