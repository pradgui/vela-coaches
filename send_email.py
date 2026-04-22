import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

ZOHO_EMAIL = os.getenv("ZOHO_EMAIL")
ZOHO_PASSWORD = os.getenv("ZOHO_PASSWORD")


def cor_prioridade(prioridade: str):
    cores = {
        "alta":  {"bg": "#FEE2E2", "texto": "#DC2626", "borda": "#DC2626", "label": "🔴 ALTA"},
        "media": {"bg": "#FEF9C3", "texto": "#B45309", "borda": "#F59E0B", "label": "🟡 MÉDIA"},
        "baixa": {"bg": "#DCFCE7", "texto": "#15803D", "borda": "#16A34A", "label": "🟢 BAIXA"},
    }
    return cores.get(prioridade, cores["baixa"])


def barra_aderencia(aderencia: int) -> str:
    pct = min(aderencia, 100)
    if aderencia >= 90:
        cor = "#1D9E75"
    elif aderencia >= 70:
        cor = "#F59E0B"
    else:
        cor = "#DC2626"

    return f"""
    <div style="margin-top:8px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-size:11px;color:#6B7280;font-family:Arial,sans-serif;">Aderência ao plano</span>
        <span style="font-size:11px;font-weight:700;color:{cor};font-family:Arial,sans-serif;">{aderencia}%</span>
      </div>
      <div style="background:#E5E7EB;border-radius:999px;height:6px;width:100%;">
        <div style="background:{cor};border-radius:999px;height:6px;width:{pct}%;"></div>
      </div>
    </div>
    """


def cartao_atleta(atleta: dict) -> str:
    cor = cor_prioridade(atleta["prioridade"])
    barra = barra_aderencia(atleta["aderencia"])

    return f"""
    <div style="border:1px solid #E5E7EB;border-left:4px solid {cor['borda']};
                border-radius:8px;padding:16px 20px;margin-bottom:12px;background:#FFFFFF;">

      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
        <div>
          <div style="font-size:16px;font-weight:700;color:#111827;font-family:Arial,sans-serif;">
            {atleta['nome']}
          </div>
          <div style="font-size:12px;color:#6B7280;margin-top:2px;font-family:Arial,sans-serif;">
            {atleta['sinal_principal']}
          </div>
        </div>
        <div style="background:{cor['bg']};color:{cor['texto']};font-size:11px;font-weight:700;
                    padding:4px 10px;border-radius:999px;font-family:Arial,sans-serif;white-space:nowrap;">
          {cor['label']}
        </div>
      </div>

      {barra}

      <div style="margin-top:12px;font-size:13px;color:#374151;line-height:1.6;font-family:Arial,sans-serif;">
        {atleta['analise']}
      </div>

      <div style="margin-top:10px;background:#F0FDF4;border-left:3px solid #1D9E75;
                  padding:8px 12px;border-radius:0 6px 6px 0;">
        <span style="font-size:11px;font-weight:700;color:#0F6E56;font-family:Arial,sans-serif;">AÇÃO → </span>
        <span style="font-size:12px;color:#065F46;font-family:Arial,sans-serif;">{atleta['acao']}</span>
      </div>
    </div>
    """


def ranking_visual(atletas: list) -> str:
    itens = ""
    for i, atleta in enumerate(atletas):
        cor = cor_prioridade(atleta["prioridade"])
        itens += f"""
        <tr>
          <td style="padding:8px 12px;font-size:13px;font-weight:700;color:#6B7280;
                     font-family:Arial,sans-serif;">{i+1}</td>
          <td style="padding:8px 12px;font-size:13px;font-weight:600;color:#111827;
                     font-family:Arial,sans-serif;">{atleta['nome']}</td>
          <td style="padding:8px 12px;">
            <span style="background:{cor['bg']};color:{cor['texto']};font-size:11px;font-weight:700;
                         padding:3px 8px;border-radius:999px;font-family:Arial,sans-serif;">
              {cor['label']}
            </span>
          </td>
          <td style="padding:8px 12px;font-size:13px;color:#6B7280;
                     font-family:Arial,sans-serif;">{atleta['sinal_principal']}</td>
        </tr>
        """

    return f"""
    <table style="width:100%;border-collapse:collapse;background:#FFFFFF;
                  border:1px solid #E5E7EB;border-radius:8px;overflow:hidden;">
      <thead>
        <tr style="background:#F9FAFB;">
          <th style="padding:10px 12px;text-align:left;font-size:11px;color:#9CA3AF;
                     font-weight:600;font-family:Arial,sans-serif;">#</th>
          <th style="padding:10px 12px;text-align:left;font-size:11px;color:#9CA3AF;
                     font-weight:600;font-family:Arial,sans-serif;">ATLETA</th>
          <th style="padding:10px 12px;text-align:left;font-size:11px;color:#9CA3AF;
                     font-weight:600;font-family:Arial,sans-serif;">PRIORIDADE</th>
          <th style="padding:10px 12px;text-align:left;font-size:11px;color:#9CA3AF;
                     font-weight:600;font-family:Arial,sans-serif;">SINAL</th>
        </tr>
      </thead>
      <tbody>{itens}</tbody>
    </table>
    """


def montar_html(brief: dict, nome_coach: str) -> str:
    cartoes = "".join(cartao_atleta(a) for a in brief["atletas"])
    ranking = ranking_visual(brief["atletas"])

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F3F4F6;font-family:Arial,sans-serif;">

  <div style="max-width:620px;margin:0 auto;padding:24px 16px;">

    <!-- HEADER -->
    <div style="background:#0F6E56;border-radius:12px 12px 0 0;padding:28px 32px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:24px;font-weight:300;color:#FFFFFF;letter-spacing:-0.5px;">
            ☀️ Monday Brief
          </div>
          <div style="font-size:12px;color:#5DCAA5;margin-top:4px;letter-spacing:1px;">
            VELA COACH INTELLIGENCE
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:12px;color:#5DCAA5;">Semana</div>
          <div style="font-size:14px;color:#FFFFFF;font-weight:600;">{brief['semana']}</div>
        </div>
      </div>
      <div style="margin-top:16px;font-size:14px;color:#A7F3D0;">
        Olá {nome_coach}, aqui está o resumo da semana.
      </div>
    </div>

    <!-- BODY -->
    <div style="background:#F9FAFB;padding:24px 32px;">

      <!-- RANKING -->
      <div style="margin-bottom:24px;">
        <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1.5px;margin-bottom:12px;">
          RANKING DE ATENÇÃO
        </div>
        {ranking}
      </div>

      <!-- ATLETAS -->
      <div style="margin-bottom:24px;">
        <div style="font-size:11px;font-weight:700;color:#9CA3AF;letter-spacing:1.5px;margin-bottom:12px;">
          ANÁLISE POR ATLETA
        </div>
        {cartoes}
      </div>

      <!-- RESUMO EXECUTIVO -->
      <div style="background:#ECFDF5;border:1px solid #A7F3D0;border-radius:8px;padding:16px 20px;">
        <div style="font-size:11px;font-weight:700;color:#065F46;letter-spacing:1.5px;margin-bottom:8px;">
          RESUMO EXECUTIVO
        </div>
        <div style="font-size:14px;color:#064E3B;line-height:1.6;">
          {brief['resumo_executivo']}
        </div>
      </div>

    </div>

    <!-- FOOTER -->
    <div style="background:#111827;border-radius:0 0 12px 12px;padding:16px 32px;
                display:flex;justify-content:space-between;align-items:center;">
      <div style="font-size:14px;color:#FFFFFF;font-weight:300;letter-spacing:-0.3px;">
        Vela
      </div>
      <a href="https://usevela.co" style="font-size:11px;color:#5DCAA5;text-decoration:none;">
        usevela.co
      </a>
    </div>

  </div>

</body>
</html>
"""


def enviar_brief(destinatario: str, nome_coach: str, brief: dict):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☀️ Monday Brief | Semana {brief['semana']} | Vela"
    msg["From"] = ZOHO_EMAIL
    msg["To"] = destinatario

    html = montar_html(brief, nome_coach)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.zoho.com", 465) as servidor:
        servidor.login(ZOHO_EMAIL, ZOHO_PASSWORD)
        servidor.sendmail(ZOHO_EMAIL, destinatario, msg.as_string())
        print(f"Brief enviado para {destinatario}")


if __name__ == "__main__":
    from build_brief import gerar_brief

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

    print("Gerando brief...")
    brief = gerar_brief(atletas_teste)
    print("Enviando email...")
    enviar_brief(ZOHO_EMAIL, "Guilherme", brief)