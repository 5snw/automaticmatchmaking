<div align="center">

# Snow Emporium Matchmaking

O próximo ciclo começa no lobby.

![Beta](https://img.shields.io/badge/status-beta-d3f875?style=flat-square&labelColor=171c18)
![Windows](https://img.shields.io/badge/plataforma-Windows-8cbcff?style=flat-square&labelColor=171c18)
![Languages](https://img.shields.io/badge/languages-PT%20%7C%20EN-d3f875?style=flat-square&labelColor=171c18)

[Português](#português) · [English](#english) · [Discord](https://discord.gg/446EYkTUJh)

</div>

---

## Português

Automação de matchmaking para Fortnite no Windows. Reconhece os botões na tela e repete os cliques de Jogar, Continuar, Pular e Voltar ao lobby.

O aplicativo está em **beta**, abre em **português** e também oferece **inglês**. Recomendamos inglês no aplicativo e no Fortnite para melhorar o reconhecimento. O idioma selecionado no app deve acompanhar o idioma do jogo.

### Começar

Com o executável, basta abrir `snow-emporium-matchmaking.exe`. Não é necessário instalar Python.

1. Abra o Fortnite e fique no lobby.
2. Escolha o idioma e o modo no aplicativo.
3. Clique em **Iniciar**.
4. Para encerrar o ciclo, clique em **Parar** ou pressione **F8**.

### Escolha o modo

| | Modo A | Modo B |
|:--|:--|:--|
| Ciclo | Aguarda o fim da partida e passa pelas telas de resultado | Espera na ilha e retorna pelo menu Esc |
| Próxima partida | Após voltar ao lobby | Após voltar ao lobby |
| WASD | Opcional, com intervalo e duração ajustáveis | Desativado |
| Espera na ilha | Não se aplica | 90 segundos por padrão, ajustável de 10 a 600 |

### Ajustes

- **Limiar:** controla o rigor do reconhecimento. Diminua um pouco se o botão não for detectado; aumente se houver cliques errados.
- **Recortar imagem:** captura um botão da sua tela. A imagem fica na pasta `assets`, ao lado do executável, e substitui o modelo incluído.
- **Sempre visível:** mantém a janela do aplicativo sobre as outras.
- **WASD:** no modo A, o padrão é segurar uma tecla aleatória por 3 segundos a cada 10 segundos.

Se os cliques não acontecerem, confira o idioma do jogo, desconecte o controle e aguarde cerca de um minuto depois de iniciar. Se necessário, tente executar como administrador ou recapture os botões. A aba **Guia** traz as instruções completas.

### Novidades da 1.2

- **Segundo plano:** captura a janela do jogo e devolve o foco ao aplicativo anterior depois de cada comando.
- **Ghost:** deixa o jogo invisível durante a automação. Use **Mostrar o jogo por 5 segundos** para conferir.
- **Espaço automático:** no modo A, escolha o intervalo e a quantidade de toques por vez, independentemente de WASD.
- **Atualizações:** consulta as Releases deste repositório, manualmente ou ao abrir. A preferência fica salva no PC; o download é manual.
- **Diagnóstico:** salva um JSON local com versões, configurações e disponibilidade dos modelos. Não inclui chave do Discord, screenshots ou histórico de atividade.
- **DM de teste:** confira sua chave e as permissões de mensagens sem iniciar uma sessão.

Segundo plano e Ghost são experimentais. Use janela ou tela cheia sem bordas, sem minimizar. Os comandos ainda alternam o foco; WASD o mantém durante o tempo de tecla pressionada. A compatibilidade precisa ser conferida no Fortnite. Se a captura falhar, a automação para e restaura a janela. Fechar o app à força pode exigir reiniciar o jogo.

[Baixar a versão publicada](https://github.com/5snw/automaticmatchmaking/releases/latest)

### Discord opcional

O aplicativo tem suporte a relatórios por DM e configurações remotas pelo **ss :)**. Essas funções dependem de o serviço estar ativo; a automação local funciona sem vínculo com o Discord.

1. Entre no [servidor](https://discord.gg/446EYkTUJh) e use `/link`, ou `/panel` e o botão **Link key**.
2. Cole sua chave privada na aba **Controle**. A URL do serviço já vem preenchida.
3. Ative o envio de resumos e, se quiser, as configurações remotas.

O resumo inclui tempo de sessão, ações, pico APM e voltas. Defina **DM a cada** para receber atualizações em minutos; `0` envia só ao parar ou sair. Permita mensagens diretas do servidor para receber os relatórios.

Use `/settings` para ajustar modo, idioma, espera, intervalo de DM e WASD. As alterações são consultadas a cada minuto enquanto o app roda e a opção está habilitada. Iniciar e parar continuam sendo ações locais. `/unlink` revoga a chave.

As opções começam desligadas. Sem chave, o programa não faz requisições ao serviço. Os relatórios não incluem screenshots ou arquivos pessoais. Para entregar as DMs, o serviço associa o ID do Discord a um hash da chave e às configurações escolhidas. A chave fica salva localmente, protegida pela sua conta do Windows. Use Apagar chave salva para remover a cópia local.

Este repositório contém o aplicativo Windows e o cliente de integração. O código do bot, do painel e da API não faz parte dele.

### Rodar pelo código

É necessário Python com suporte a Tkinter. A versão atual foi validada com Python 3.14 no Windows.

```powershell
git clone https://github.com/5snw/automaticmatchmaking.git
cd automaticmatchmaking
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

### Compilar e testar

```powershell
.\build_exe.bat
```

O executável é gerado em `dist/snow-emporium-matchmaking.exe`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Contato

**Discord: 5snw** · [Snow Emporium](https://discord.gg/446EYkTUJh)

---

## English

Matchmaking automation for Fortnite on Windows. It recognizes buttons on screen and repeats the Play, Continue, Skip and Return to Lobby clicks.

The app is in **beta**, starts in **Portuguese** and also supports **English**. English is recommended for both the app and Fortnite to improve button recognition. Match the app language to your game language.

### Get started

Open `snow-emporium-matchmaking.exe` if you have the executable. Python is not required.

1. Open Fortnite and stay in the lobby.
2. Choose your language and mode in the app.
3. Click **Start**.
4. Click **Stop** or press **F8** to stop the loop.

### Pick a mode

| | Mode A | Mode B |
|:--|:--|:--|
| Loop | Waits for the match to end and goes through the results screens | Waits on the island and leaves through the Esc menu |
| Next match | After returning to the lobby | After returning to the lobby |
| WASD | Optional, with adjustable interval and duration | Disabled |
| Island wait | Not applicable | 90 seconds by default, adjustable from 10 to 600 |

### Settings

- **Threshold:** sets how strict button recognition is. Lower it slightly if buttons are missed; raise it if clicks land on the wrong targets.
- **Crop image:** captures a button from your screen. Images are saved in `assets` next to the executable and override the bundled templates.
- **Always on top:** keeps the app window above other windows.
- **WASD:** in mode A, the default is to hold a random key for 3 seconds every 10 seconds.

If clicks are not detected, check the game language, disconnect your controller and wait about a minute after starting. If needed, try running as administrator or capture your button images again. The **Guide** tab has the full instructions.

### New in 1.2

- **Background mode:** captures the game window and restores the previous app's focus after each input.
- **Ghost:** makes the game invisible during automation. Use **Show the game for 5 seconds** to check it.
- **Automatic Space:** in mode A, configure the interval and taps per burst independently of WASD.
- **Updates:** checks this repository's Releases manually or at startup. The preference is saved locally; downloads are manual.
- **Diagnostics:** saves local JSON with versions, settings and template availability. No Discord key, screenshots or activity history.
- **Test DM:** checks your key and direct message permissions without starting a session.

Background mode and Ghost are experimental. Use windowed or borderless mode without minimizing. Inputs still switch focus; WASD keeps focus for the configured hold time. Compatibility must be checked in Fortnite. A capture failure stops automation and restores the window. Force-closing the app may require restarting the game.

[Download the published version](https://github.com/5snw/automaticmatchmaking/releases/latest)

### Optional Discord integration

The app supports DM reports and remote settings through **ss :)**. These features require an active service. Local automation works without linking Discord.

1. Join the [server](https://discord.gg/446EYkTUJh) and run `/link`, or use `/panel` and its **Link key** button.
2. Paste your private key into the **Control** tab. The service URL is already filled in.
3. Enable session summaries and, optionally, remote settings.

Reports include elapsed time, actions, peak APM and rounds. Set **DM every** to receive progress reports in minutes; `0` sends reports only on stop or exit. Allow direct messages from the server to receive them.

Use `/settings` to adjust mode, language, wait time, DM interval and WASD. The app checks for changes every minute while running, when remote settings are enabled. Starting and stopping stay local. `/unlink` revokes your key.

Both options start disabled. Without a key, the app makes no requests to the service. Reports contain no screenshots or personal files. To deliver DMs, the service associates your Discord ID with a hash of the key and your chosen settings. The key is saved locally, protected by your Windows account. Use Remove saved key to delete the local copy.

This repository contains the Windows app and its integration client. The bot, panel and API source code are not included.

### Run from source

Python with Tkinter support is required. The current version was validated with Python 3.14 on Windows.

```powershell
git clone https://github.com/5snw/automaticmatchmaking.git
cd automaticmatchmaking
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

### Build and test

```powershell
.\build_exe.bat
```

The executable is created at `dist/snow-emporium-matchmaking.exe`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Contact

**Discord: 5snw** · [Snow Emporium](https://discord.gg/446EYkTUJh)