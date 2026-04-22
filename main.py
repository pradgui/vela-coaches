import os
from dotenv import load_dotenv
from build_brief import gerar_brief
from send_email import enviar_brief

load_dotenv()

# ─── CONFIGURAÇÃO ───────────────────────────────────────
# Aqui você vai cadastrar os coaches e seus atletas
# Quando tiver o CSV ou a API, os dados vêm de lá automaticamente
# Por enquanto, edite manualmente a cada semana

COACHES = [
    {
        "nome": "Guilherme",
        "email": os.getenv("ZOHO_EMAIL"),  # troca pelo email do coach real quando tiver
        "atletas": [
            {
                "nome": "Ana Lima",
                "semana": "21-27 Abril",
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
                "semana": "21-27 Abril",
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
                "semana": "21-27 Abril",
                "carga_planejada_tss": 300,
                "carga_executada_tss": 340,
                "aderencia_percentual": 113,
                "horas_treinadas": 9.8,
                "frequencia_cardiaca_media_repouso": 58,
                "qualidade_sono_autoreportada": "regular",
                "observacoes": "Treinou alem do planejado, FC repouso subindo"
            }
        ]
    }
]

# ─── PIPELINE ───────────────────────────────────────────
def rodar():
    print("=" * 50)
    print("VELA — Iniciando pipeline Monday Brief")
    print("=" * 50)

    for coach in COACHES:
        print(f"\nProcessando coach: {coach['nome']}")
        print(f"Atletas: {len(coach['atletas'])}")

        try:
            print("Gerando brief...")
            brief = gerar_brief(coach["atletas"])

            print("Enviando email...")
            enviar_brief(coach["email"], coach["nome"], brief)

            print(f"✓ Brief enviado para {coach['email']}")

        except Exception as e:
            print(f"✗ Erro no coach {coach['nome']}: {e}")

    print("\n" + "=" * 50)
    print("Pipeline finalizado")
    print("=" * 50)


if __name__ == "__main__":
    rodar()