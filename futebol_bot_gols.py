import requests
import time
from datetime import datetime
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, API_FOOTBALL_KEY, TIME_ID

HEADERS = {
    'x-apisports-key': API_FOOTBALL_KEY
}

bot = Bot(token=TELEGRAM_BOT_TOKEN)

jogos_ativos = {}
gols_anteriores = {}
eventos_enviados = {}

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": texto
    }
    try:
        resposta = requests.post(url, data=payload)
        print("🔔 Notificação enviada:", texto)
        print("Status:", resposta.status_code)
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def monitorar_partidas():
    hoje = datetime.now().strftime("%Y-%m-%d")
    season = 2025

    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "team": TIME_ID,
        "date": hoje,
        "season": season
    }

    try:
        resposta = requests.get(url, headers=HEADERS, params=params)
        dados = resposta.json()
        jogos = dados.get("response", [])

        if not jogos:
            enviar_mensagem("⚠️ Nenhum jogo do seu time hoje!")
            return

        for jogo in jogos:
            fixture_id = jogo["fixture"]["id"]
            status = jogo["fixture"]["status"]["short"]
            time_casa = jogo["teams"]["home"]["name"]
            time_fora = jogo["teams"]["away"]["name"]
            gols_casa = jogo["goals"]["home"]
            gols_fora = jogo["goals"]["away"]
            nome_partida = f"{time_casa} x {time_fora}"

            if status == "1H" and fixture_id not in jogos_ativos:
                enviar_mensagem(f"🟢 Começou o jogo: {nome_partida}!")
                jogos_ativos[fixture_id] = "1H"

            if status == "HT" and jogos_ativos.get(fixture_id) != "HT":
                enviar_mensagem(f"🟡 Intervalo em {nome_partida}. Placar: {gols_casa} x {gols_fora}")
                jogos_ativos[fixture_id] = "HT"

            if status in ["FT", "AET", "PEN"] and jogos_ativos.get(fixture_id) != "FT":
                enviar_mensagem(f"🔴 Fim de jogo: {nome_partida}\n🔚 Placar final: {gols_casa} x {gols_fora}")
                jogos_ativos[fixture_id] = "FT"

            placar_atual = (gols_casa, gols_fora)
            if fixture_id in gols_anteriores:
                gols_antes = gols_anteriores[fixture_id]
                if placar_atual != gols_antes:
                    if gols_casa > gols_antes[0]:
                        enviar_mensagem(f"⚽ Gol do {time_casa}! Placar: {gols_casa} x {gols_fora}")
                    elif gols_fora > gols_antes[1]:
                        enviar_mensagem(f"⚽ Gol do {time_fora}! Placar: {gols_casa} x {gols_fora}")
            gols_anteriores[fixture_id] = placar_atual

            eventos_url = f"https://v3.football.api-sports.io/fixtures/events?fixture={fixture_id}"
            eventos_resp = requests.get(eventos_url, headers=HEADERS).json()
            eventos = eventos_resp.get("response", [])

            for evento in eventos:
                evento_id = f'{fixture_id}-{evento["time"]["elapsed"]}-{evento["team"]["id"]}-{evento["player"]["id"]}-{evento["type"]}-{evento["detail"]}'
                if evento_id in eventos_enviados:
                    continue

                tipo = evento["type"]
                detalhe = evento["detail"]
                jogador = evento["player"]["name"]
                time_evento = evento["team"]["name"]
                minuto = evento["time"]["elapsed"]

                if tipo == "Card":
                    if detalhe == "Yellow Card":
                        enviar_mensagem(f"🟨 {jogador} recebeu cartão amarelo aos {minuto}' — {time_evento}")
                    elif detalhe == "Red Card":
                        enviar_mensagem(f"🟥 {jogador} foi expulso aos {minuto}' — {time_evento}")

                elif tipo == "Penalty":
                    enviar_mensagem(f"⚪ Pênalti marcado para {time_evento} aos {minuto}'!")

                elif tipo == "subst":
                    substituto = evento.get("assist", {}).get("name")
                    enviar_mensagem(f"🔄 Substituição: {jogador} sai, {substituto} entra ({time_evento}, {minuto}')")

                eventos_enviados[evento_id] = True

    except Exception as e:
        print("Erro ao monitorar partidas:", e)

    time.sleep(60)
