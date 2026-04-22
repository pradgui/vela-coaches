import json
import os
import requests
import zipfile
import io
from dotenv import load_dotenv

load_dotenv()

NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN")
NETLIFY_COACHES_SITE_ID = os.getenv("NETLIFY_COACHES_SITE_ID")

LABELS = {
    "pt": {
        "title": "Monday Brief",
        "subtitle": "Vela Coach Intelligence",
        "week": "Semana",
        "ranking": "Ranking de Atenção",
        "analysis": "Análise por Atleta",
        "adherence": "Aderência ao plano",
        "action": "AÇÃO",
        "executive": "Resumo Executivo",
        "athletes": "atletas",
        "high": "ALTA",
        "medium": "MÉDIA",
        "low": "BAIXA",
    },
    "en": {
        "title": "Monday Brief",
        "subtitle": "Vela Coach Intelligence",
        "week": "Week",
        "ranking": "Attention Ranking",
        "analysis": "Athlete Analysis",
        "adherence": "Plan adherence",
        "action": "ACTION",
        "executive": "Executive Summary",
        "athletes": "athletes",
        "high": "HIGH",
        "medium": "MEDIUM",
        "low": "LOW",
    }
}

PRIORITY_COLORS = {
    "alta":   {"bg": "#FEE2E2", "text": "#DC2626", "border": "#DC2626"},
    "media":  {"bg": "#FEF9C3", "text": "#B45309", "border": "#F59E0B"},
    "baixa":  {"bg": "#DCFCE7", "text": "#15803D", "border": "#16A34A"},
    "high":   {"bg": "#FEE2E2", "text": "#DC2626", "border": "#DC2626"},
    "medium": {"bg": "#FEF9C3", "text": "#B45309", "border": "#F59E0B"},
    "low":    {"bg": "#DCFCE7", "text": "#15803D", "border": "#16A34A"},
}


def gerar_html(brief: dict, nome_coach: str, idioma: str) -> str:
    L = LABELS[idioma]

    def prioridade_label(p):
        mapa = {
            "alta":   f"🔴 {L['high']}",
            "media":  f"🟡 {L['medium']}",
            "baixa":  f"🟢 {L['low']}",
            "high":   f"🔴 {L['high']}",
            "medium": f"🟡 {L['medium']}",
            "low":    f"🟢 {L['low']}",
        }
        return mapa.get(p, p)

    def cor(p):
        return PRIORITY_COLORS.get(p, PRIORITY_COLORS["baixa"])

    def barra(aderencia):
        pct = min(aderencia, 100)
        c = "#1D9E75" if aderencia >= 90 else "#F59E0B" if aderencia >= 70 else "#DC2626"
        return f"""
        <div style="margin-top:8px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:11px;color:#807B75;">{L['adherence']}</span>
            <span style="font-size:11px;font-weight:700;color:{c};">{aderencia}%</span>
          </div>
          <div style="background:#2A2A2A;border-radius:999px;height:6px;">
            <div style="background:{c};border-radius:999px;height:6px;width:{pct}%;"></div>
          </div>
        </div>"""

    def cartao(atleta):
        c = cor(atleta["prioridade"])
        return f"""
        <div style="border:1px solid #2A2A2A;border-left:4px solid {c['border']};
                    border-radius:8px;padding:16px 20px;margin-bottom:12px;background:#1A1A1A;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
            <div>
              <div style="font-size:16px;font-weight:700;color:#EAE8E4;">{atleta['nome']}</div>
              <div style="font-size:12px;color:#807B75;margin-top:2px;">{atleta['sinal_principal']}</div>
            </div>
            <div style="background:{c['bg']};color:{c['text']};font-size:11px;font-weight:700;
                        padding:4px 10px;border-radius:999px;white-space:nowrap;">
              {prioridade_label(atleta['prioridade'])}
            </div>
          </div>
          {barra(atleta['aderencia'])}
          <div style="margin-top:12px;font-size:13px;color:#A39E97;line-height:1.6;">
            {atleta['analise']}
          </div>
          <div style="margin-top:10px;background:#0F2A1E;border-left:3px solid #1D9E75;
                      padding:8px 12px;border-radius:0 6px 6px 0;">
            <span style="font-size:11px;font-weight:700;color:#5DCAA5;">{L['action']} → </span>
            <span style="font-size:12px;color:#A7F3D0;">{atleta['acao']}</span>
          </div>
        </div>"""

    def ranking_row(i, atleta):
        c = cor(atleta["prioridade"])
        return f"""
        <tr>
          <td style="padding:8px 12px;font-size:13px;font-weight:700;color:#524E49;">{i+1}</td>
          <td style="padding:8px 12px;font-size:13px;font-weight:600;color:#EAE8E4;">{atleta['nome']}</td>
          <td style="padding:8px 12px;">
            <span style="background:{c['bg']};color:{c['text']};font-size:11px;font-weight:700;
                         padding:3px 8px;border-radius:999px;">
              {prioridade_label(atleta['prioridade'])}
            </span>
          </td>
          <td style="padding:8px 12px;font-size:13px;color:#807B75;">{atleta['sinal_principal']}</td>
        </tr>"""

    cartoes = "".join(cartao(a) for a in brief["atletas"])
    rows = "".join(ranking_row(i, a) for i, a in enumerate(brief["atletas"]))

    return f"""<!DOCTYPE html>
<html lang="{idioma}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Vela — {L['title']} | {nome_coach}</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:wght@300;400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
</head>
<body style="margin:0;padding:0;background:#141414;font-family:'DM Sans',Arial,sans-serif;color:#EAE8E4;">

  <div style="max-width:720px;margin:0 auto;padding:32px 16px;">

    <!-- HEADER -->
    <div style="background:#0F6E56;border-radius:12px 12px 0 0;padding:32px 36px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-family:'Cormorant',serif;font-size:32px;font-weight:300;color:#FFFFFF;letter-spacing:-0.5px;">
            ☀️ {L['title']}
          </div>
          <div style="font-size:11px;color:#5DCAA5;margin-top:4px;letter-spacing:2px;text-transform:uppercase;">
            {L['subtitle']}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:11px;color:#5DCAA5;text-transform:uppercase;letter-spacing:1px;">{L['week']}</div>
          <div style="font-size:16px;color:#FFFFFF;font-weight:600;margin-top:2px;">{brief['semana']}</div>
        </div>
      </div>
      <div style="margin-top:20px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.15);">
        <div style="font-size:13px;color:#A7F3D0;">
          {nome_coach} · {len(brief['atletas'])} {L['athletes']}
        </div>
      </div>
    </div>

    <!-- BODY -->
    <div style="background:#1A1A1A;padding:28px 36px;">

      <!-- RANKING -->
      <div style="margin-bottom:28px;">
        <div style="font-size:10px;font-weight:700;color:#524E49;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:12px;">
          {L['ranking']}
        </div>
        <table style="width:100%;border-collapse:collapse;background:#141414;
                      border:1px solid #262626;border-radius:8px;overflow:hidden;">
          <tbody>{rows}</tbody>
        </table>
      </div>

      <!-- ATLETAS -->
      <div style="margin-bottom:28px;">
        <div style="font-size:10px;font-weight:700;color:#524E49;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:12px;">
          {L['analysis']}
        </div>
        {cartoes}
      </div>

      <!-- RESUMO EXECUTIVO -->
      <div style="background:#0F2A1E;border:1px solid #1D4A35;border-radius:8px;padding:20px 24px;">
        <div style="font-size:10px;font-weight:700;color:#5DCAA5;letter-spacing:2px;
                    text-transform:uppercase;margin-bottom:10px;">
          {L['executive']}
        </div>
        <div style="font-size:14px;color:#A7F3D0;line-height:1.7;">
          {brief['resumo_executivo']}
        </div>
      </div>

    </div>

    <!-- FOOTER -->
    <div style="background:#0F0F0F;border-radius:0 0 12px 12px;padding:16px 36px;
                display:flex;justify-content:space-between;align-items:center;">
      <div style="font-family:'Cormorant',serif;font-size:18px;color:#EAE8E4;font-weight:300;">
        Vela
      </div>
      <a href="https://usevela.co" style="font-size:11px;color:#5DCAA5;text-decoration:none;">
        usevela.co
      </a>
    </div>

  </div>

</body>
</html>"""


def fazer_deploy(slug: str, html: str) -> str:
    """Faz upload do dashboard para o site de coaches no Netlify."""

    # Pagina raiz simples para o site de coaches
    raiz_html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Vela</title>
<style>body{background:#141414;color:#EAE8E4;font-family:Arial,sans-serif;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;}
.logo{font-size:32px;font-weight:300;text-align:center;}
.sub{font-size:12px;color:#5DCAA5;letter-spacing:3px;text-transform:uppercase;margin-top:8px;}
</style></head>
<body><div><div class="logo">Vela</div>
<div class="sub">Coach Intelligence Platform</div></div></body></html>"""

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.html", raiz_html)
        zf.writestr(f"{slug}/index.html", html)
    zip_buffer.seek(0)

    headers = {
        "Authorization": f"Bearer {NETLIFY_TOKEN}",
        "Content-Type": "application/zip",
    }

    url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_COACHES_SITE_ID}/deploys"
    response = requests.post(url, headers=headers, data=zip_buffer.read())

    if response.status_code in [200, 201]:
        subdomain = response.json().get("subdomain", "vela-coaches")
        deploy_url = f"https://{subdomain}.netlify.app/{slug}"
        print(f"Dashboard publicado: {deploy_url}")
        return deploy_url
    else:
        print(f"Erro no deploy: {response.status_code} — {response.text}")
        return None


if __name__ == "__main__":
    from build_brief import gerar_brief

    atletas_teste = [
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

    print("Gerando brief...")
    brief = gerar_brief(atletas_teste)

    print("Gerando dashboard...")
    html = gerar_html(brief, "Guilherme", "pt")

    print("Fazendo deploy...")
    url = fazer_deploy("guilherme", html)

    if url:
        print(f"\n✓ Acesse: {url}")
