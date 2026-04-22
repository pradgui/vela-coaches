import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()


def gerar_brief(dados_atletas: list) -> dict:

    dados_formatados = json.dumps(dados_atletas, ensure_ascii=False, indent=2)

    prompt = f"""
Você é o assistente de coaching da Vela. Analise os dados dos atletas e retorne APENAS um JSON válido, sem texto antes ou depois.

O JSON deve seguir exatamente esta estrutura:
{{
  "semana": "período da semana (ex: 14-20 Abril)",
  "atletas": [
    {{
      "nome": "nome do atleta",
      "prioridade": "alta" ou "media" ou "baixa",
      "aderencia": número de 0 a 100,
      "sinal_principal": "frase curta de até 6 palavras",
      "analise": "2-3 frases explicando o que está acontecendo",
      "acao": "ação concreta recomendada ao coach"
    }}
  ],
  "resumo_executivo": "2-3 frases resumindo a semana para o coach"
}}

Ordene os atletas por prioridade: alta primeiro, depois media, depois baixa.

DADOS:
{dados_formatados}

Retorne apenas o JSON:
"""

    mensagem = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    texto = mensagem.content[0].text.strip()
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]
    return json.loads(texto.strip())


if __name__ == "__main__":
    atletas_teste = [
        {
            "nome": "Ana Lima",
            "semana": "14-20 abril",
            "carga_planejada_tss": 380,
            "carga_executada_tss": 210,
            "aderencia_percentual": 55,
            "horas_treinadas": 6.5,
            "frequencia_cardiaca_media_repouso": 52,
            "qualidade_sono_autoreportada": "ruim",
            "observacoes": "Pulou os dois longoes do fim de semana sem avisar"
        },
        {
            "nome": "Carlos Mota",
            "semana": "14-20 abril",
            "carga_planejada_tss": 420,
            "carga_executada_tss": 415,
            "aderencia_percentual": 99,
            "horas_treinadas": 11.2,
            "frequencia_cardiaca_media_repouso": 48,
            "qualidade_sono_autoreportada": "boa",
            "observacoes": "Semana consistente, FC em queda positiva"
        },
        {
            "nome": "Mariana Souza",
            "semana": "14-20 abril",
            "carga_planejada_tss": 300,
            "carga_executada_tss": 340,
            "aderencia_percentual": 113,
            "horas_treinadas": 9.8,
            "frequencia_cardiaca_media_repouso": 58,
            "qualidade_sono_autoreportada": "regular",
            "observacoes": "Treinou alem do planejado, FC repouso subindo"
        }
    ]

    brief = gerar_brief(atletas_teste)
    print(json.dumps(brief, ensure_ascii=False, indent=2))