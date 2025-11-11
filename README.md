# Sistema de Agendamentos - CMFAM/UEPB

Protótipo funcional de sistema de agendamento para laboratório multiusuário da Universidade Estadual da Paraíba (UEPB).

## 📋 Sobre o Projeto

Este é um sistema web desenvolvido em Python com Flask para gerenciar agendamentos de equipamentos do Centro Multiusuário de Análises Físico-Químicas e Microbiológicas (CMFAM). O sistema permite visualizar, reservar e gerenciar horários de uso de equipamentos científicos de forma eficiente e intuitiva.

## 🚀 Funcionalidades

- **Dashboard Interativo**: Visualização rápida de estatísticas e reservas do dia
- **Gerenciamento de Equipamentos**: Listagem e detalhes de equipamentos disponíveis
- **Sistema de Reservas**: Criação de reservas com validação de conflitos de horário
- **Calendário de Reservas**: Visualização de reservas por equipamento
- **Gerenciamento de Reservas**: Visualização e cancelamento de reservas
- **Painel Administrativo**: Visualização de estatísticas, equipamentos e usuários
- **Validação de Conflitos**: Verificação automática de conflitos de horário
- **Interface Responsiva**: Design adaptável para desktop, tablet e mobile

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.x**: Linguagem de programação principal
- **Flask**: Framework web minimalista
- **SQLite**: Banco de dados relacional leve

### Frontend
- **HTML5**: Estrutura das páginas
- **Bootstrap 5**: Framework CSS para interface responsiva
- **Bootstrap Icons**: Ícones vetoriais
- **JavaScript/jQuery**: Interatividade e requisições AJAX
- **CSS3**: Estilização customizada

## 📁 Estrutura do Projeto

```
Sistema-de-Agendamentos-cmfam/
│
├── app.py                  # Aplicação Flask principal
├── agendamentos.db         # Banco de dados SQLite (criado automaticamente)
├── README.md               # Documentação do projeto
│
├── templates/              # Templates HTML
│   ├── base.html          # Template base com navegação
│   ├── index.html         # Dashboard principal
│   ├── equipamentos.html  # Lista de equipamentos
│   ├── equipamento_detalhes.html  # Detalhes do equipamento
│   ├── reservar.html      # Formulário de reserva
│   ├── minhas_reservas.html  # Lista de reservas
│   ├── calendario.html    # Calendário de reservas
│   └── admin.html         # Painel administrativo
│
└── static/                 # Arquivos estáticos
    ├── css/
    │   └── style.css      # Estilos customizados
    └── js/
        └── main.js        # JavaScript customizado
```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/nathanufpb/Sistema-de-Agendamentos-cmfam.git
cd Sistema-de-Agendamentos-cmfam
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install flask
```

4. **Execute a aplicação**
```bash
python app.py
```

5. **Acesse o sistema**
Abra seu navegador e acesse: `http://localhost:5000`

## 💾 Banco de Dados

O sistema utiliza SQLite e cria automaticamente o banco de dados `agendamentos.db` na primeira execução.

### Estrutura das Tabelas

**equipamentos**
- id (INTEGER PRIMARY KEY)
- nome (TEXT)
- descricao (TEXT)
- localizacao (TEXT)
- ativo (BOOLEAN)
- created_at (TIMESTAMP)

**usuarios**
- id (INTEGER PRIMARY KEY)
- nome (TEXT)
- email (TEXT UNIQUE)
- tipo (TEXT) - 'admin' ou 'usuario'
- created_at (TIMESTAMP)

**reservas**
- id (INTEGER PRIMARY KEY)
- equipamento_id (INTEGER FOREIGN KEY)
- usuario_id (INTEGER FOREIGN KEY)
- data_inicio (TIMESTAMP)
- data_fim (TIMESTAMP)
- status (TEXT) - 'pendente', 'confirmada', 'cancelada'
- observacoes (TEXT)
- created_at (TIMESTAMP)

### Dados de Exemplo

O sistema vem pré-configurado com dados de exemplo:

**Equipamentos:**
- Microscópio Eletrônico (MEV)
- Espectrômetro de Massa
- Cromatógrafo (HPLC)
- Analisador Térmico (TGA)

**Usuários:**
- Admin Sistema (admin@uepb.edu.br) - tipo: admin
- João Silva (joao.silva@uepb.edu.br) - tipo: usuario
- Maria Santos (maria.santos@uepb.edu.br) - tipo: usuario

## 📱 Funcionalidades Detalhadas

### 1. Dashboard (/)
- Visualização de estatísticas gerais
- Lista de equipamentos disponíveis
- Reservas do dia atual
- Acesso rápido às principais funcionalidades

### 2. Equipamentos (/equipamentos)
- Lista completa de equipamentos
- Informações detalhadas de cada equipamento
- Link direto para reserva

### 3. Detalhes do Equipamento (/equipamento/<id>)
- Informações completas do equipamento
- Próximas reservas agendadas
- Botão para nova reserva

### 4. Nova Reserva (/reservar)
- Formulário de criação de reserva
- Seleção de equipamento e usuário
- Definição de data/hora de início e fim
- Validação de conflitos de horário
- Campo de observações

### 5. Minhas Reservas (/minhas-reservas)
- Lista de todas as reservas
- Filtro por status (confirmada, pendente, cancelada)
- Opção de cancelar reservas ativas

### 6. Calendário (/calendario)
- Visualização de reservas por equipamento
- Filtro por equipamento específico
- Listagem organizada por data

### 7. Painel Admin (/admin)
- Estatísticas gerais do sistema
- Gerenciamento de equipamentos
- Gerenciamento de usuários
- Ações rápidas

## 🔌 API Endpoints

### GET /api/reservas/<equipamento_id>
Retorna todas as reservas de um equipamento em formato JSON.

**Resposta:**
```json
[
  {
    "id": 1,
    "title": "João Silva (confirmada)",
    "start": "2024-01-15T10:00:00",
    "end": "2024-01-15T12:00:00",
    "status": "confirmada"
  }
]
```

## 🎨 Interface do Usuário

- **Design Responsivo**: Adapta-se automaticamente a diferentes tamanhos de tela
- **Bootstrap 5**: Interface moderna e profissional
- **Ícones**: Bootstrap Icons para melhor visualização
- **Cores e Badges**: Sistema de cores para diferentes status
- **Alertas**: Feedback visual para ações do usuário
- **Animações**: Transições suaves e efeitos hover

## 🔒 Segurança

⚠️ **Nota de Segurança**: Este é um protótipo para demonstração. Para uso em produção, implemente:

- Sistema de autenticação de usuários
- Controle de permissões (RBAC)
- Validação de entrada mais robusta
- Proteção CSRF
- HTTPS/SSL
- Senhas hasheadas
- Limitação de taxa (rate limiting)
- Logs de auditoria

## 🚀 Melhorias Futuras

- [ ] Sistema de autenticação e login
- [ ] Notificações por email
- [ ] Exportação de relatórios (PDF/Excel)
- [ ] Calendário visual interativo (FullCalendar.js)
- [ ] Sistema de aprovação de reservas
- [ ] Histórico de uso por usuário
- [ ] Dashboard com gráficos estatísticos
- [ ] API RESTful completa
- [ ] Aplicativo mobile
- [ ] Integração com calendários externos (Google Calendar)

## 📝 Licença

Este projeto é um protótipo educacional desenvolvido para a Universidade Estadual da Paraíba (UEPB).

## 👥 Autores

- Desenvolvido como protótipo funcional para o CMFAM/UEPB

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## 📞 Suporte

Para questões e suporte, abra uma issue no repositório do GitHub.

## 🙏 Agradecimentos

- Universidade Estadual da Paraíba (UEPB)
- Centro Multiusuário de Análises Físico-Químicas e Microbiológicas (CMFAM)
- Comunidade Flask e Python

---

**Desenvolvido com ❤️ para a UEPB**
