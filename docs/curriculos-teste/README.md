# Currículos de teste

Três currículos **fictícios** para testar o envio de currículo, a simulação de compatibilidade e a análise da candidatura. O formato segue o de currículos reais da área de tecnologia no Brasil: cabeçalho com contato, resumo profissional, experiência em ordem cronológica inversa, formação, habilidades, cursos e idiomas.

Pessoas, empresas, instituições de ensino, e-mails (`@example.com`) e perfis são inventados. Telefones e cidades estão no formato real para que o anonimizador (`algorithm/anonymizer.py`) tenha o que remover.

| Arquivo | Nível | Perfil | Páginas |
|---|---|---|---|
| `curriculo_junior_mariana_costa.pdf` | Júnior | Back-end Python/Django, cerca de 2 anos (estágio + júnior), Sistemas de Informação | 1 |
| `curriculo_pleno_rafael_santos.pdf` | Pleno | Full stack Python (FastAPI) + Vue.js, 5 anos, Ciência da Computação | 1 |
| `curriculo_senior_juliana_lima.pdf` | Sênior | Tech lead, microsserviços Python/Go, AWS e Kubernetes, 11 anos, mestrado | 2 |

## Casos que vale observar

- **Mesmos termos, níveis diferentes:** os três citam Python, SQL, Git e APIs REST. Na busca só por termos (`JEV_ENABLED=false`), pleno e sênior tiram 100 nas duas vagas de exemplo de `evaluation/levels.json`, porque a busca só verifica se o termo aparece. Com o modelo externo ligado, a nota deve cair para o júnior e o pleno na vaga sênior.
- **Formação sem o termo do critério:** o júnior é formado em *Sistemas de Informação*, então o critério "Computação" fica como não encontrado (85 nas duas vagas de exemplo).
- **Negação:** o júnior diz ter "conhecimento teórico de AWS (...) ainda sem experiência prática". Um critério "AWS" encontra o termo, e o modelo externo deve deixá-lo "a revisar" (regra de conflito do `analyzer.py`).
- **Java × JavaScript:** o júnior cita só JavaScript; um critério "Java" não deve ser encontrado nele. O sênior cita Java de verdade.
