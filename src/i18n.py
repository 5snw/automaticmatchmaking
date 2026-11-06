LANG_CODES = ("pt", "en")
DEFAULT_LANG = "en"

UI = {'en': {'crop_help': 'Only use this if the app is not clicking the game buttons.\n'
                     '\n'
                     'If clicks are working, leave the images as they are. Otherwise, stop automation, show '
                     'the button in the game, select it in the list and use Crop image to capture it again.',
        'dm_title': 'DISCORD  /  ss :)',
        'service_url': 'Service URL',
        'link_key': 'Link key',
        'dm_send': 'Send a DM summary on stop or exit',
        'dm_remote': 'Allow changes through /settings',
        'dm_every': 'DM every',
        'dm_minutes': 'min · 0 = only on stop',
        'dm_privacy': 'Without a key, nothing is sent. The key is kept only until you close the app.',
        'dm_ok': 'Discord: summary sent by DM.',
        'dm_error': 'Discord: DM failed. Check service URL, key and DM permissions.',
        'remote_error': 'Discord: could not fetch remote settings. Local controls remain available.',
        'remote_ok': 'Discord: remote settings applied. Match the game language manually.',
        'beta_notice': 'BETA version. English is recommended for the app and Fortnite.',
        'discord_server': 'Join the Discord server',
        'tab_control': 'Control',
        'tab_guide': 'Guide',
        'start': 'Start',
        'stop': 'Stop',
        'topmost': 'Always on top',
        'lang_label': 'App & game language',
        'mode_A': 'A · Results-screen loop',
        'mode_B': 'B · Wait and leave through the menu',
        'b_pre': 'Mode B wait',
        'b_post': 'seconds',
        'afk_check': 'Hold random WASD key during match',
        'afk_pre': 'Every',
        'afk_mid': 's / hold',
        'afk_post': 's',
        'threshold': 'Threshold',
        'crop': 'Crop image',
        'info': '{state}   similarity: {score:.2f}   loops: {loops}',
        'log_started': 'started',
        'log_stopped': 'stopped',
        'log_language': 'language: {name}',
        'log_mode': 'mode: {name}',
        'log_saved': 'saved {path}',
        'log_cancelled': 'capture cancelled',
        'log_capture_error': 'capture error: {error}',
        'log_too_large': 'selection too large - drag only around the button',
        'session_status': 'STATUS',
        'session_similarity': 'SIMILARITY',
        'session_loops': 'LOOPS',
        'stop_hint': 'F8 to stop',
        'section_mode': '01  /  GAME MODE',
        'section_movement': '02  /  MOVEMENT & WINDOW',
        'section_recognition': '03  /  RECOGNITION',
        'section_activity': 'ACTIVITY',
        'activity_hint': 'Follow clicks and messages from this session.',
        'recognition_hint': 'Only adjust this if the app is not clicking the game buttons.',
        'discord_setup': 'Join the server and run /link. Then paste your key below to set up your reports.',
        'service_options': 'Service options',
        'state_IDLE': 'Ready to start',
        'state_SEARCHING_PLAY': 'Looking for Play',
        'state_IN_MATCH': 'Waiting for results',
        'state_SKIPPING_RESULT': 'Results screen',
        'state_RETURNING_LOBBY': 'Returning to lobby',
        'state_B:LOBBY': 'Looking for Play',
        'state_B:LOADING': 'Loading match',
        'state_B:WAITING': 'Waiting to leave',
        'state_B:MENU': 'Leaving via menu'},
 'pt': {'crop_help': 'Só mexa aqui se o aplicativo não estiver clicando nos botões do jogo.\n'
                     '\n'
                     'Se os cliques estão funcionando, não precisa alterar as imagens. Caso contrário, pare '
                     'a automação, deixe o botão visível no jogo, escolha o botão na lista e use Recortar '
                     'imagem para capturá-lo novamente.',
        'dm_title': 'DISCORD  /  ss :)',
        'service_url': 'URL do serviço',
        'link_key': 'Chave de vínculo',
        'dm_send': 'Enviar resumo por DM ao parar ou sair',
        'dm_remote': 'Permitir ajustes pelo /settings',
        'dm_every': 'DM a cada',
        'dm_minutes': 'min · 0 = só ao parar',
        'dm_privacy': 'Sem chave, nada é enviado. A chave vale só nesta abertura do app.',
        'dm_ok': 'Discord: resumo enviado por DM.',
        'dm_error': 'Discord: falha na DM. Confira URL, chave e permissão de mensagens diretas.',
        'remote_error': 'Discord: não foi possível consultar as configurações. Os controles locais continuam '
                        'disponíveis.',
        'remote_ok': 'Discord: configurações remotas aplicadas. Ajuste o idioma do jogo manualmente.',
        'beta_notice': 'Versão BETA. Recomendamos usar o app e o Fortnite em inglês.',
        'discord_server': 'Entrar no servidor do Discord',
        'tab_control': 'Controle',
        'tab_guide': 'Guia',
        'start': 'Iniciar',
        'stop': 'Parar',
        'topmost': 'Sempre visível',
        'lang_label': 'Idioma do app e jogo',
        'mode_A': 'A · Ciclo pelas telas de resultado',
        'mode_B': 'B · Esperar e sair pelo menu',
        'b_pre': 'Espera no modo B',
        'b_post': 'segundos',
        'afk_check': 'Segurar WASD aleatório na partida',
        'afk_pre': 'A cada',
        'afk_mid': 's / segurar',
        'afk_post': 's',
        'threshold': 'Limiar',
        'crop': 'Recortar imagem',
        'info': '{state}   similaridade: {score:.2f}   voltas: {loops}',
        'log_started': 'iniciado',
        'log_stopped': 'parado',
        'log_language': 'idioma: {name}',
        'log_mode': 'modo: {name}',
        'log_saved': 'salvo: {path}',
        'log_cancelled': 'recorte cancelado',
        'log_capture_error': 'erro de recorte: {error}',
        'log_too_large': 'seleção grande demais: arraste só em volta do botão',
        'session_status': 'STATUS',
        'session_similarity': 'SIMILARIDADE',
        'session_loops': 'VOLTAS',
        'stop_hint': 'F8 para parar',
        'section_mode': '01  /  MODO DE JOGO',
        'section_movement': '02  /  MOVIMENTO E JANELA',
        'section_recognition': '03  /  RECONHECIMENTO',
        'section_activity': 'ATIVIDADE',
        'activity_hint': 'Acompanhe os cliques e as mensagens da sessão.',
        'recognition_hint': 'Só ajuste se o aplicativo não estiver clicando nos botões do jogo.',
        'discord_setup': 'Entre no servidor e use /link. Depois, cole a chave abaixo para configurar seus '
                         'relatórios.',
        'service_options': 'Opções do serviço',
        'state_IDLE': 'Pronto para iniciar',
        'state_SEARCHING_PLAY': 'Procurando Jogar',
        'state_IN_MATCH': 'Aguardando partida',
        'state_SKIPPING_RESULT': 'Tela de resultado',
        'state_RETURNING_LOBBY': 'Voltando ao lobby',
        'state_B:LOBBY': 'Procurando Jogar',
        'state_B:LOADING': 'Carregando partida',
        'state_B:WAITING': 'Contando a espera',
        'state_B:MENU': 'Saindo pelo menu'}}

GUIDE = {'en': [('h1', 'Getting started'),
        ('n', '1. Open Fortnite and keep the lobby visible on screen.'),
        ('n',
         '2. Select the same language in the app and the game. English is recommended; Portuguese is also '
         'available in this beta.'),
        ('n', '3. Choose mode A or B and adjust the options before starting.'),
        ('n', '4. Click Start. The app looks for buttons on screen and clicks when it recognizes them.'),
        ('n',
         '5. Click Stop or press F8 to stop automation. This does not close Fortnite or leave the match.'),
        ('h1', 'What the app does'),
        ('p',
         'Snow Emporium Matchmaking automates clicks to enter and leave matches. It recognizes screen images '
         'and sends mouse and keyboard input. It does not handle combat, aiming or match objectives.'),
        ('h1', 'How the modes work'),
        ('h2', 'Mode A: results-screen loop'),
        ('p',
         'Clicks Play in the lobby and waits for the next buttons. When they appear, it attempts to click '
         'Continue, Skip and Return to Lobby, then looks for Play again. The duration depends on the match '
         'and the screens displayed.'),
        ('li',
         'The WASD option holds a randomly selected W, A, S or D key during the match stage. By default, a '
         'hold lasts 3 seconds, with 10 seconds between the starts of successive holds.'),
        ('li',
         'The app does not play the match for you. WASD only produces movement; you can disable it in the '
         'Control tab.'),
        ('h2', 'Mode B: leave after a waiting period'),
        ('p',
         'Clicks Play and looks for the visual indicator used to detect the island. Recognizing that '
         'indicator starts the countdown. Once the wait ends, it attempts to open the menu with Esc and '
         'click Return to Lobby.'),
        ('li',
         'The default wait is 90 seconds, adjustable from 10 to 600 seconds. Loading time is separate, so a '
         'full cycle takes longer than the configured wait.'),
        ('li',
         'This mode does not guarantee leaving before the match begins. Image detection, loading and your '
         'chosen wait affect when it leaves.'),
        ('li',
         'Automatic WASD holds do not run in mode B. Recognition still requires the game interface to match '
         'the image templates.'),
        ('h1', 'Understanding the controls'),
        ('li',
         'Always on top: keeps the app window above other windows. Place it where it does not cover the game '
         'buttons the app needs to recognize.'),
        ('li',
         'Threshold: for conventional templates, a higher value requires a closer image match. Lower it '
         'gradually if a button is missed; raise it if clicks are incorrect. Some shape-based templates use '
         'their own limits.'),
        ('li',
         'The displayed state is the automation stage. Similarity is an image-recognition score, not '
         'Fortnite XP, level or points. Loops counts lobby returns recorded by the mode.'),
        ('h2', 'Capture a button from your screen'),
        ('n', '1. Stop automation and make the desired button visible in the game.'),
        ('n',
         '2. Select the button in the list beside Crop image. For example: play for Play and return_lobby '
         'for Return to Lobby.'),
        ('n', '3. Click Crop image and drag a close selection around the button. Press Esc to cancel.'),
        ('n',
         '4. The image is saved in assets next to the executable and overrides the bundled template. Start '
         'again to test it.'),
        ('h1', 'If clicks do not work'),
        ('li',
         'Check the language and keep the game visible. Menus, overlays and the app window itself can hide '
         'the buttons.'),
        ('li',
         'Before starting, disconnect any controller connected to your PC, including Bluetooth controllers. If input does not reach the game, try '
         'running the app as administrator.'),
        ('li',
         'In mode B, allow for loading and the configured wait. The app is not supposed to leave immediately '
         'after you click Start.'),
        ('li',
         'Check the message log. If recognition fails, capture the correct button before lowering the '
         'threshold too far.'),
        ('h1', 'Discord: optional reports'),
        ('p',
         'Join our Discord server to set up reports. The ss :) bot provides the private key you need to '
         'connect the app. Local automation also works without Discord.'),
        ('n',
         '1. Click Join the Discord server. In the server, run /link, or /panel followed by Link key, to '
         'receive your key in a private response.'),
        ('n',
         '2. Paste the key into the Control tab. The service URL is already filled in; do not paste the '
         'Discord invite into that field.'),
        ('n',
         '3. Enable Send a DM summary on stop or exit. Allow direct messages from the server to receive '
         'reports.'),
        ('li',
         'DM every is measured in minutes. With 0, reports are sent only when you stop or close the app '
         'normally. A higher number also enables progress reports while it runs.'),
        ('li',
         'Reports show elapsed time, actions, peak APM and loops. Actions count automation clicks and Esc, '
         'excluding WASD. Peak APM is the highest number of actions recorded in a rolling 60-second window.'),
        ('h2', 'Settings through Discord'),
        ('li',
         'Enable Allow changes through /settings to allow changes to mode, language, wait time, DM interval '
         'and WASD. The app checks for changes every minute while automation is running.'),
        ('li',
         'Starting and stopping stay local. If you change the language through Discord, adjust Fortnite '
         'manually. Use /unlink to revoke your key.'),
        ('h2', 'Data and privacy'),
        ('p',
         'Without a key, the app makes no requests to the service. Both Discord options start disabled. The '
         'key is not saved when you close the app. Reports contain metrics, a reason and a delivery ID; no '
         'screenshots or personal files. The service stores your Discord ID, a key hash and the settings '
         'needed for the link. An in-flight request may finish after you disable an option.'),
        ('h1', 'Contact'),
        ('p', 'Discord: 5snw | https://discord.gg/446EYkTUJh')],
 'pt': [('h1', 'Começar a usar'),
        ('n', '1. Abra o Fortnite e deixe o jogo no lobby, visível na tela.'),
        ('n',
         '2. Escolha o mesmo idioma no aplicativo e no jogo. Recomendamos inglês; português também está '
         'disponível nesta versão beta.'),
        ('n', '3. Selecione o modo A ou B e ajuste as opções antes de iniciar.'),
        ('n',
         '4. Clique em Iniciar. O programa procura os botões na tela e executa os cliques quando os '
         'reconhece.'),
        ('n',
         '5. Para interromper a automação, clique em Parar ou pressione F8. Isso não fecha o Fortnite nem '
         'sai da partida.'),
        ('h1', 'O que o aplicativo faz'),
        ('p',
         'O Snow Emporium Matchmaking automatiza cliques de entrada e saída de partidas. Ele reconhece '
         'imagens da tela e envia comandos de mouse e teclado. Não controla combate, mira ou objetivos da '
         'partida.'),
        ('h1', 'Modos de funcionamento'),
        ('h2', 'Modo A: ciclo pelas telas de resultado'),
        ('p',
         'Clica em Jogar no lobby e aguarda os próximos botões. Quando aparecem, tenta clicar em Continuar, '
         'Pular e Voltar ao lobby. Depois procura Jogar novamente. A duração depende da partida e das telas '
         'exibidas.'),
        ('li',
         'A opção de WASD segura uma das teclas W, A, S ou D aleatoriamente durante a etapa de partida. O '
         'padrão é segurar por 3 segundos, com intervalo de 10 segundos entre os inícios dos '
         'pressionamentos.'),
        ('li',
         'O programa não joga a partida por você. O WASD apenas produz movimentos; você pode desativá-lo na '
         'aba Controle.'),
        ('h2', 'Modo B: saída após um tempo de espera'),
        ('p',
         'Clica em Jogar e procura o indicador visual usado para detectar a ilha. Ao reconhecer esse '
         'indicador, inicia a contagem. Quando o tempo termina, tenta abrir o menu com Esc e clicar em '
         'Voltar ao lobby.'),
        ('li',
         'A espera padrão é de 90 segundos. Você pode escolher de 10 a 600 segundos. O carregamento não faz '
         'parte dessa contagem; por isso, o ciclo completo demora mais que a espera configurada.'),
        ('li',
         'Esse modo não garante que a saída aconteça antes do início da partida. A detecção das imagens, o '
         'carregamento e o tempo escolhido afetam o momento da saída.'),
        ('li',
         'O WASD automático não é executado no modo B. O reconhecimento continua dependendo de a interface '
         'do jogo ser compatível com os modelos.'),
        ('h1', 'Entender os controles'),
        ('li',
         'Sempre visível: mantém a janela do aplicativo sobre outras janelas. Posicione-a sem cobrir os '
         'botões que precisam ser reconhecidos no jogo.'),
        ('li',
         'Limiar: em modelos convencionais, um valor maior exige uma imagem mais parecida. Diminua pouco a '
         'pouco se o botão não for encontrado; aumente se houver cliques errados. Alguns modelos por formato '
         'têm limites próprios.'),
        ('li',
         'O estado mostrado indica a etapa da automação. A similaridade é um índice de reconhecimento de '
         'imagem; não representa XP, nível ou pontos do Fortnite. Voltas registra os retornos ao lobby '
         'contados pelo modo.'),
        ('h2', 'Capturar um botão da sua tela'),
        ('n', '1. Pare a automação e deixe o botão desejado visível no jogo.'),
        ('n',
         '2. Escolha o botão na lista ao lado de Recortar imagem. Por exemplo: play para Jogar e '
         'return_lobby para Voltar ao lobby.'),
        ('n',
         '3. Clique em Recortar imagem e arraste uma seleção justa ao redor do botão. Pressione Esc para '
         'cancelar.'),
        ('n',
         '4. A imagem fica na pasta assets ao lado do executável e tem prioridade sobre o modelo incluído. '
         'Inicie novamente para testar.'),
        ('h1', 'Se os cliques não funcionarem'),
        ('li',
         'Confirme o idioma e mantenha o jogo visível. Menus, sobreposições e a própria janela do aplicativo '
         'podem esconder os botões.'),
        ('li',
         'Antes de iniciar, desconecte qualquer controle conectado ao PC, inclusive por Bluetooth. Se os cliques não chegarem ao '
         'jogo, tente executar o aplicativo como administrador.'),
        ('li',
         'No modo B, aguarde o carregamento e a espera configurada. O programa não deve sair imediatamente '
         'após você clicar em Iniciar.'),
        ('li',
         'Confira o registro de mensagens. Se houver falha no reconhecimento, recapture o botão correto '
         'antes de reduzir muito o limiar.'),
        ('h1', 'Discord: relatórios opcionais'),
        ('p',
         'Para configurar os relatórios, entre no nosso servidor do Discord. O bot ss :) fornece a chave '
         'privada para conectar o aplicativo. A automação local também funciona sem Discord.'),
        ('n',
         '1. Entre pelo botão Entrar no servidor do Discord. No servidor, use /link, ou /panel e depois Link '
         'key, para receber sua chave em uma resposta privada.'),
        ('n',
         '2. Cole a chave na aba Controle. A URL do serviço já vem preenchida; não use o link de convite do '
         'Discord nesse campo.'),
        ('n',
         '3. Ative Enviar resumo por DM ao parar ou sair. Permita mensagens diretas do servidor para receber '
         'os relatórios.'),
        ('li',
         'DM a cada usa minutos. Com 0, o resumo é enviado somente ao parar ou fechar normalmente o '
         'aplicativo. Um número maior também permite relatórios de progresso enquanto ele roda.'),
        ('li',
         'O resumo mostra tempo, ações, pico APM e voltas. Ações contam cliques e Esc da automação, sem '
         'incluir WASD. Pico APM é a maior quantidade de ações registrada em uma janela de 60 segundos.'),
        ('h2', 'Configurações pelo Discord'),
        ('li',
         'Ative Permitir ajustes pelo /settings para permitir mudanças de modo, idioma, espera, intervalo de '
         'DM e WASD. O aplicativo consulta as alterações a cada minuto enquanto a automação roda.'),
        ('li',
         'Iniciar e parar continuam sendo ações locais. Se mudar o idioma pelo Discord, ajuste o idioma do '
         'Fortnite manualmente. Use /unlink para revogar sua chave.'),
        ('h2', 'Dados e privacidade'),
        ('p',
         'Sem chave, o aplicativo não faz requisições ao serviço. As duas opções de Discord começam '
         'desligadas. A chave não é salva ao fechar o programa. Relatórios contêm métricas, motivo e '
         'identificador de entrega; não contêm screenshots nem arquivos pessoais. O serviço guarda seu ID do '
         'Discord, um hash da chave e as configurações necessárias ao vínculo. Uma requisição já iniciada '
         'pode terminar depois de você desligar uma opção.'),
        ('h1', 'Contato'),
        ('p', 'Discord: 5snw | https://discord.gg/446EYkTUJh')]}

def norm(lang):
    return lang if lang in UI else DEFAULT_LANG

def t(lang, key, **kw):
    s = UI.get(lang, {}).get(key) or UI[DEFAULT_LANG].get(key) or key
    return s.format(**kw) if kw else s

def guide(lang):
    return GUIDE.get(lang) or GUIDE[DEFAULT_LANG]
