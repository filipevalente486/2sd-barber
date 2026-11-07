"""
Configuração da empresa 2SD.Barber.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

EMPRESA = {
    "id": 1,
    "nome": "2SD.Barber",
    "tipo_servico": "barbearia",
    "logo_path": "assets/logo.png",

    "cores": {
        "primaria": "#000000",
        "secundaria": "#D4AF37",
        "fundo": "#0a0a0a",
        "texto": "#ffffff",
        "texto_secundario": "#b0b0b0",
    },

    "contacto": {
        "telefone": "+351935926754",
        "whatsapp": "351935926754",
        "email": "geral@2sdbarber.pt",
        "instagram": "@2sd.barber",
    },

    "morada": {
        "rua": "Imprensa Oliveirense, 213",
        "codigo_postal": "3720-256",
        "cidade": "Oliveira de Azeméis",
        "google_maps_url": "https://maps.google.com/?q=Oliveira+de+Azemeis",
    },

    "horario_funcionamento": {
        0: ("09:00", "19:00"),
        1: ("09:00", "19:00"),
        2: ("09:00", "19:00"),
        3: ("09:00", "19:00"),
        4: ("09:00", "19:00"),
        5: ("09:00", "19:00"),
        6: None,  # Domingo — sob consulta
    },

    "notas_horario": {
        6: "Sob consulta",
    },

   
    "carousel_imagens": [
        "assets/carousel/corte1.jpg",
        "assets/carousel/corte2.jpg",
        "assets/carousel/corte3.jpg",
        "assets/carousel/corte4.jpg",
    ],

    "mensagem_whatsapp": (
        "Olá! Acabei de fazer uma marcação na 2SD.Barber:\n\n"
        "👤 Nome: {nome}\n"
        "✂️ Serviço: {servico}\n"
        "📅 Data: {data}\n"
        "🕐 Hora: {hora}\n\n"
        "Até breve!"
    ),
"fidelizacao": {
    "ativa": True,
    "modo": "visita",
    "pontos_por_visita": 1,
    "pontos_para_premio": 10,
    "descricao_premio": "Corte simples grátis",
    "servico_premio_id": 1,
    "pontos_por_referral": 3,
    "descricao_referral": "Traz o teu amigo",
},

# NOVO — URL da app (atualizar se recriar a app)
"app_url": "https://2sd-barber.streamlit.app",

"categorias_despesa": [
        "🏠 Renda",
        "💡 Eletricidade / Água",
        "✂️ Material (lâminas, produtos)",
        "📱 Comunicações",
        "💰 Salários",
        "📊 Contabilidade",
        "🔧 Manutenção",
        "📦 Outros",
    ],

}


DIAS_SEMANA = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo",
}
