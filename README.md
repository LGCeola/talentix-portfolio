# Talentix 🎯
> **Sistema Inteligente e Transparente de Análise e Ranqueamento de Currículos**

---

## 💡 Sobre o Projeto

O **Talentix** é uma plataforma web desenvolvida para otimizar e democratizar o processo de recrutamento e seleção, conectando as necessidades de **candidatos** e **recrutadores** em um único ecossistema.

Em processos seletivos tradicionais:
- **Candidatos** frequentemente sofrem com a ausência de retorno (feedback), falta de clareza nos critérios de avaliação e dificuldade para identificar pontos de melhoria em seus currículos.
- **Recrutadores** enfrentam sobrecarga na triagem manual de altos volumes de currículos, além de ferramentas de mercado (ATS) que costumam ser caras, rígidas ou dependentes de filtros opacos de palavras-chave.

O Talentix resolve esse desafio por meio de um **algoritmo próprio de pontuação**, baseado em critérios explícitos e interpretáveis (sem "caixas-pretas"), oferecendo um processo seletivo mais ágil, justo e transparente.

---

## ✨ Principais Funcionalidades

### 👤 Para Candidatos
- **Upload Simplificado:** Envio do currículo em formato digital (PDF ou texto).
- **Análise Transparente:** Visualização detalhada de como a pontuação foi calculada (habilidades, formação acadêmica e experiência).
- **Feedback & Melhorias:** Sugestões práticas de pontos fortes e oportunidades de aprimoramento no perfil.
- **Compatibilidade com Vagas:** Comparação direta do perfil com os requisitos de vagas ativas.

### 🏢 Para Recrutadores
- **Gestão de Vagas Customizada:** Criação de vagas com definição de requisitos específicos e pesos para cada critério.
- **Ranqueamento Automatizado:** Classificação determinística dos candidatos mais aderentes ao perfil da vaga em segundos.
- **Tomada de Decisão Humanizada:** Relatórios e justificativas analíticas que aceleram a triagem inicial, mantendo a decisão final nas mãos do recrutador.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python, [FastAPI](https://fastapi.tiangolo.com/), SQLAlchemy, Pydantic
- **Frontend:** [Vue.js](https://vuejs.org/) (Single Page Application)
- **Processamento & Algoritmo:** Engine própria em Python para extração, parsing e pontuação determinística
- **Banco de Dados:** PostgreSQL (com suporte a JSONB para detalhamento dinâmico de pontuações)
- **Cache & Sessão:** Redis

---

## 📁 Estrutura do Repositório

```text
talentix-portfolio/
├── apps/
│   ├── backend/       # API REST, modelos de dados, regras de negócio e algoritmo
│   └── web/           # Interface do usuário (SPA)
├── docs/              # Documentação técnica aprofundada, diagramas C4 e RFC
│   └── RFC.md         # Documento de Request for Comments (RFC) completo
└── README.md          # Visão geral do projeto
```

---

## 📖 Documentação Completa

Para detalhes aprofundados sobre arquitetura (Diagramas C4, modelo relacional), personas, pesquisa com usuários e requisitos funcionais/não funcionais, consulte:

- 📄 **RFC no Repositório:** [`docs/RFC.md`](docs/RFC.md)
- 🌐 **Documento RFC (Google Docs):** [Acessar Documento RFC](https://docs.google.com/document/d/17bO6AqS8L75arfYSQFbCpSuSk0kW0wVpISinQlHUf00/edit?tab=t.0#heading=h.igeih6o6ng6b)
