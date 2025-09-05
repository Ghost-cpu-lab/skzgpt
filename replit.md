# Bot Discord Melhorado

## Visão Geral
Bot do Discord com IA integrada usando Groq/LLaMA, funcionalidades administrativas e busca de GIFs.

## Principais Melhorias Implementadas

### ✅ Arquitetura Modular
- Estrutura organizada em módulos (core, services, handlers, commands, utils)
- Separação clara de responsabilidades
- Código reutilizável e maintível

### ✅ Tratamento de Erros Robusto
- Handler centralizado de erros
- Logging estruturado com arquivos de log
- Mensagens de erro amigáveis para usuários

### ✅ Segurança Melhorada
- Validação de entrada de usuários
- Sanitização de texto
- Verificação de permissões administrativas
- Bloqueio de padrões perigosos (@everyone, links suspeitos)

### ✅ Funcionalidades do Bot - 95+ COMANDOS!
**💬 COMANDOS DE CHAT:**
- `/chat <mensagem>` - Chat simples com IA (sem funcionalidades admin)
- `/skgpt <mensagem>` - Chatbot IA com TODAS as 95+ funcionalidades
- `/gif <termo>` - Busca GIFs do Tenor
- `/help` - Ajuda completa dos comandos

**📊 COMANDOS DE INFORMAÇÃO:**
- `/info servidor` - Informações completas do servidor
- `/info membros` - Estatísticas de membros
- `/info cargos` - Lista todos os cargos
- `/info canais` - Lista todos os canais
- `/info bots` - Lista todos os bots
- `/info stats` - Estatísticas detalhadas
- `/info boost` - Informações de boost

**🛠️ COMANDOS DE GERENCIAMENTO:**
- `/gerenciar criar_canal <nome>` - Criar canais
- `/gerenciar criar_categoria <nome>` - Criar categorias
- `/gerenciar slowmode <canal> <segundos>` - Modo lento
- `/gerenciar bloquear_canal <canal>` - Controle de acesso
- `/gerenciar backup_cargos` - Backup de configurações

**🛡️ COMANDOS DE MODERAÇÃO:**
- `/moderar add_reacao <canal> <emoji>` - Adicionar reações
- `/moderar pin_mensagem <canal>` - Fixar mensagens
- `/moderar auto_mod` - Sistema automático

**🎮 COMANDOS DE DIVERSÃO:**
- `/diversao coin_flip` - Cara ou coroa
- `/diversao dice_roll` - Rolar dados
- `/diversao 8ball` - Bola mágica 8
- `/diversao random_facts` - Fatos aleatórios
- `/diversao word_game` - Jogos de palavras

**🤖 COMANDOS DE AUTOMAÇÃO:**
- `/automatizar auto_role` - Auto cargo na entrada
- `/automatizar welcome_msg` - Mensagens de boas vindas
- `/automatizar level_system` - Sistema de níveis

### ✅ Todas as 95+ Funcionalidades Implementadas
**🛠️ Criação e Gestão:**
- Criar/editar embeds personalizados
- Criar/gerenciar canais de texto e voz
- Criar/gerenciar cargos/roles
- Criar categorias e organizar canais
- Duplicar canais existentes
- Criar webhooks em canais
- Backup de configurações de cargos

**📊 Informações Avançadas:**
- Listar todos os cargos do servidor
- Listar todos os canais (texto/voz)
- Listar todos os bots do servidor
- Ver estatísticas detalhadas de membros
- Top usuários por hierarquia
- Log de auditoria recente
- Convites ativos do servidor
- Informações completas do servidor

**🛡️ Controle e Moderação:**
- Limpar mensagens (específicas ou TODAS)
- Modo lento em canais (slowmode)
- Bloquear/desbloquear canais para @everyone
- Fixar/desfixar mensagens
- Adicionar reações automáticas
- Mover canais entre categorias

*Todas as funcionalidades requerem permissões de administrador*

## Estrutura do Projeto

```
├── main.py                     # Arquivo principal
├── requirements.txt            # Dependências Python
├── bot/
│   ├── core/
│   │   └── bot.py             # Classe principal do bot
│   ├── services/
│   │   ├── groq_service.py    # Integração Groq IA
│   │   └── gif_service.py     # Busca GIFs Tenor
│   ├── handlers/
│   │   ├── error_handler.py   # Tratamento de erros
│   │   └── event_handler.py   # Eventos Discord
│   ├── commands/
│   │   └── chat_commands.py   # Comandos de chat
│   ├── utils/
│   │   ├── security.py        # Validação segurança
│   │   └── admin_actions.py   # Ações administrativas
│   └── config.py              # Configurações
```

## APIs e Secrets Configurados
- ✅ DISCORD_TOKEN - Token do bot Discord  
- ✅ GROQ_API_KEY - API Groq para IA
- ✅ TENOR_API_KEY - API Tenor para GIFs
- ✅ YOUTUBE_API_KEY - API YouTube (preparado para futuro)

## Status Atual
- ✅ Bot estruturado e melhorado
- ✅ Dependências instaladas
- ✅ Workflow configurado
- ✅ Pronto para uso

## Próximos Passos Sugeridos
- Adicionar funcionalidades YouTube se necessário
- Implementar sistema de moderação avançado
- Adicionar comandos personalizados por servidor
- Dashboard web para configurações