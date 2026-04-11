# RFC: Request for Comments – Projeto Portfólio  
Engenharia de Software – Católica SC  

## Identificação:
**Título do Projeto:** Talentix - Sistema de Análise de Currículos  
**Linha do Projeto:** Web  
**Autor:** Lucas Grimes Ceola  
**Data da Proposta:** 27/02/2026  
**Versão:** 1.0  

---

# 1. VISÃO DO PRODUTO E IMPACTO

## 1.1. CONTEXTO E PROBLEMA

O processo de recrutamento e seleção é uma etapa essencial para organizações que buscam identificar candidatos adequados às suas vagas, haja vista que com o crescimento do número de profissionais disponíveis no mercado e a digitalização dos processos seletivos, empresas passaram a receber grandes volumes de currículos para uma única vaga. 

Nesse contexto, recrutadores precisam analisar e avaliar manualmente diversos perfis de vários usuários, o que torna o processo lento, suscetível a erros e pouco escalável. Ademais, em muitas organizações, especialmente de médio e grande porte, o processo de análise e seleção de candidatos não envolve apenas um profissional, mas sim uma equipe de colaboradores encarregados das etapas de análise e avaliação, o que tendência ainda mais atrasos no que diz respeito ao tempo necessário para a tomada de decisão. Além disso, pequenas e médias empresas não possuem ferramentas avançadas para auxiliar nessa triagem, dependendo de processos manuais ou soluções simplificadas.

Por outro lado, do ponto de vista dos candidatos, também existem dificuldades relevantes. Muitos profissionais enfrentam a ausência de feedback sobre seus currículos, não compreendem os critérios utilizados nas seleções e encontram dificuldades em identificar pontos de melhoria, o que pode comprometer seu desempenho em processos seletivos.

A ausência de um sistema que favoreça a metodologia de análise de currículos de forma mais completa, robusta e acessível, torna-se cada vez mais evidente quando avaliado o contexto atual, em que as principais abordagens e métodos de avaliação são análises manuais, sistemas ATS (Applicant Tracking System) e plataformas automatizadas, as quais buscam fornecer testes online, sistemas de pontuação e formulários estruturados para medir a qualidade e veracidade de um currículo. Entretanto, apesar de amplamente utilizadas, essas abordagens apresentam limitações importantes, como a dependência de palavras-chave tendendo à exclusão de aspirantes qualificados, a falta de transparência com relação aos critérios de avaliação, como a pontuação é calculada, processos manuais ainda predominantes e acessibilidade limitada devido a custos muito elevados.

Diante desse cenário, identifica-se a necessidade de realizar análises e ranqueamento de currículos de forma mais automatizada, transparente e acessível, atendendo tanto às necessidades de recrutadores quanto de candidatos.

Portanto, este projeto propõe o desenvolvimento de um sistema de análise e ranqueamento de currículos baseado em um algoritmo próprio, utilizando critérios explícitos e interpretáveis, permitindo maior transparência e controle no processo de seleção.

---

## 1.2. ORIGEM DA DEMANDA E EVIDÊNCIAS

A demanda para o desenvolvimento deste projeto surgiu a partir da análise das dificuldades enfrentadas por candidatos e recrutadores no processo de triagem de currículos. Observou-se, que com o aumento do volume de candidaturas e a digitalização dos processos seletivos, tanto empresas quanto profissionais enfrentam desafios relacionados à avaliação de currículos, à falta de critérios claros e à baixa transparência nos processos de seleção.

Diante desse cenário, identificou-se a necessidade de uma solução que possibilite uma análise automatizada, estruturada e compreensível, atendendo às demandas de ambos os públicos.

---

### 1.2.1. PESQUISA COM USUÁRIOS

Com o objetivo de validar a existência do problema e identificar necessidades reais dos usuários, foi realizada uma pesquisa por meio de um formulário online (Google Forms).

**Características da pesquisa:**  
Número de participantes: 9  
Perfis:  
Candidatos  

**Resultados e análises:**  
A análise das respostas permitiu identificar padrões relevantes entre os participantes.  

**Principais resultados:**  
77,8% relataram dificuldade em participar de processos seletivos pela falta de feedback.  
44,4% relataram não saber o que melhorar no currículo.  
55,6% relataram ter dificuldade em destacar habilidades no currículo.  
66,7% acham interessante a função de “nota do currículo”.  
88,9% acham interessante a feature de “sugestão de melhoria”.  
88,9% acham interessante a feature de “comparação de vagas”.  
66,7% acham que um sistema de análise de currículos automático seria muito útil.  

**Interpretação dos dados:**  
Os resultados indicam que existe uma dificuldade significativa na compreensão dos critérios de seleção, o processo atual apresenta baixa transparência, há uma demanda por automação e padronização e que tanto candidatos quanto recrutadores se beneficiariam de uma solução integrada.

---

## 1.3. ANÁLISE DE SOLUÇÕES EXISTENTES (BENCHMARK)

Para validar a viabilidade e necessidade de desenvolvimento de um sistema de análise de currículos, foram analisadas as principais alternativas tecnológicas disponíveis no mercado:

### LinkedIn  
Link: https://www.linkedin.com  
Público-alvo: Profissionais e recrutadores  

Principais funcionalidades:  
Criação de perfil profissional  
Publicação de vagas  
Candidatura simplificada  
Busca de candidatos  

Pontos fortes:  
Grande base de usuários  
Facilidade de uso  
Integração entre candidatos e empresas  

Limitações:  
Não realiza análise detalhada de currículos  
Não fornece pontuação ou ranking automático  
Falta de transparência nos critérios de seleção  

Figura 1 - Perfil do LinkedIn  
Fonte: Print retirada do LinkedIn de Lucas Grimes Ceola (meu próprio linkedin).

---

### Jobscan  
Link: https://jobscan.co  
Público-alvo: Candidatos  

Principais funcionalidades:  
Comparação de currículo com vaga  
Identificação de palavras-chave  
Sugestões de melhoria  

Pontos fortes:  
Foco na melhoria do currículo  
Interface simples  
Feedback direto ao usuário  

Limitações:  
Não atende recrutadores  
Baseado fortemente em palavras-chave  
Não realiza ranking entre candidatos  

Figura 2 - Relatório de exemplo (Jobscan)  
Fonte: Print retirada do website Jobscan, mostrando a interface de relatório e a pontuação obtida pela qualidade do currículo analisado.

---

### Workable  
Link: https://www.workable.com  
Público-alvo: Empresas e recrutadores  

Principais funcionalidades:  
Gestão de vagas  
Triagem de candidatos  
Pipeline de contratação  

Pontos fortes:  
Sistema completo de recrutamento  
Organização do processo seletivo  
Integração com outras ferramentas  

Limitações:  
Alto custo  
Triagem pouco transparente  
Dependência de filtros simples  

---

### HireVue  
Link: https://www.hirevue.com  
Público-alvo: Grandes empresas  

Principais funcionalidades:  
Entrevistas em vídeo  
Avaliação automatizada  
Análise comportamental  

Pontos fortes:  
Avaliação mais aprofundada  
Escalável  

Limitações:  
Processo complexo  
Foco fora da análise de currículo  
Alta barreira de uso  

---

### Comparação

| Solução | Pontos Fortes | Limitações |
|--------|--------------|-----------|
| LinkedIn | Ampla base de usuários e alto alcance, com integração entre candidatos e recrutadores. | Ausência de análise estruturada de currículos e falta de critérios explícitos de avaliação. |
| Jobscan | Feedback imediato, comparações diretas com a descrição de vaga. | Não considera contexto, ausência de comparação entre múltiplos candidatos. |
| Workable | Organização do pipeline de candidatos, suporte a múltiplas vagas. | Alto custo de implementação, pouca explicabilidade na pontuação. |
| HireVue | Escalabilidade em processos seletivos, análise comportamental adicional. | Barreira de entrada para pequenas empresas, foco fora da análise inicial de currículos. |

---

## 1.3.1. DIFERENCIAL DO PROJETO

Diante da análise realizada, observa-se que as soluções existentes atendem apenas parcialmente às necessidades do processo de seleção, apresentando limitações relevantes tanto para candidatos quanto para recrutadores. Nesse contexto, identifica-se a ausência de uma solução que integre de forma equilibrada, as necessidades de ambos os públicos, oferecendo uma análise estruturada, transparente e acessível de currículos.

Diferentemente das ferramentas analisadas, o sistema proposto neste trabalho apresenta os seguintes diferenciais:

- Análise baseada em algoritmo próprio, sem dependência exclusiva de palavras-chave  
- Transparência na avaliação, permitindo visualizar como a pontuação foi calculada  
- Ranqueamento automático de candidatos, com base em critérios definidos  
- Acessibilidade, visando utilização por pequenas e médias empresas  

Assim, o projeto busca preencher a lacuna existente entre ferramentas voltadas exclusivamente para candidatos e sistemas focados apenas em recrutadores, propondo uma solução integrada e explicável para o processo de análise de currículos.

---

## 1.4. PÚBLICO-ALVO

O sistema proposto é adicionado a dois públicos principais: candidatos a vagas de emprego e recrutadores ou profissionais responsáveis por processos seletivos, caracterizando uma abordagem híbrida.

### Candidatos:

**Perfil do usuário**  
Estudantes ou profissionais em busca de oportunidades no mercado de trabalho.  
Pessoas que desejam melhorar seus currículos.  
Usuários com diferentes níveis de experiência profissional.  

**Contexto de uso**  
Os candidatos utilizarão o sistema para:  
Enviar seus currículos.  
Obter uma avaliação automatizada.  
Identificar pontos fortes e pontos de melhoria.  
Comparar seu perfil com requisitos de vagas.  

O uso ocorre, principalmente, durante a preparação para processos seletivos ou após receberem retorno negativo em candidaturas.  

**Nível de conhecimento técnico**  
Básico a intermediário.  
Familiaridade com navegação web.  
Não é necessário conhecimento técnico avançado.  

---

### Recrutadores/Empresas:

**Perfil de usuário**  
Profissionais de Recursos Humanos.  
Gestores responsáveis por contratação.  
Pequenas e médias empresas com necessidade de triagem de currículos.  

**Contexto de uso**  
Os recrutadores utilizarão o sistema para:  
Criar vagas com critérios específicos.  
Receber currículos de candidatos.  
Obter um ranking automático de candidatos.  
Analisar justificativas das pontuações atribuídas.  

O uso ocorre durante o processo de triagem inicial, com o objetivo de reduzir o tempo gasto na análise manual.  

**Nível de conhecimento técnico**  
Básico a intermediário.  
Experiência com ferramentas digitais corporativas.  
Não é necessário conhecimento técnico especializado.  

---

## 1.4.1 DIFERENCIAL DO PÚBLICO-ALVO

Diferentemente de soluções tradicionais, que atendem exclusivamente candidatos ou recrutadores, o sistema proposto busca integrar ambos os perfis em uma única plataforma, promovendo maior alinhamento entre as expectativas do mercado e as qualificações dos profissionais.

---

## 1.5. OBJETIVOS DO PROJETO

### 1.5.1. OBJETIVO GERAL

Desenvolver uma plataforma web para análise e ranqueamento de currículos, baseada em um algoritmo próprio, capaz de avaliar candidatos de forma automatizada, transparente e acessível, atendendo tanto às necessidades de recrutadores quanto de candidatos.

---

### 1.5.2. OBJETIVOS ESPECÍFICOS

- Desenvolver um sistema capaz de realizar a análise automatizada de currículos, reduzindo a necessidade de triagem manual.  
- Implementar um algoritmo de pontuação baseado em critérios explícitos, com habilidades, experiência e formação.  
- Permitir a criação de vagas com definição de requisitos e pesos, possibilitando avaliações personalizadas.  
- Gerar um ranking de candidatos com base na compatibilidade com a vaga, facilitando a tomada de decisão.  
- Disponibilizar ao usuário uma visualização detalhada da pontuação, promovendo transparência no processo de avaliação.  

---

## 1.6. MÉTRICAS DE SUCESSO (KPIs)

A avaliação do sucesso do projeto será realizada com base em métricas relacionadas ao desempenho do sistema, eficiência do processo de análise e qualidade dos resultados apresentados aos usuários. Por conseguinte, as métricas definidas para esse projeto são:

- O sistema deve realizar a análise de um currículo em até 2 segundos;  
- Redução de pelo menos 50% no tempo de triagem inicial em relação à análise manual;  
- O algoritmo deve gerar resultados determinísticos e consistentes para os mesmos dados de entrada;  
- Suporte a pelo menos 20 usuários simultâneos sem degradação significativa de desempenho;  
- Pelo menos 80% dos usuários devem ser capazes de compreender a pontuação gerada pelo sistema (com base em questionário);  
- Pelo menos 75% dos usuários devem avaliar o sistema como útil ou muito útil;  