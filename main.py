import schedule
import time
from datetime import datetime
from futebol_bot_gols import monitorar_partidas
from config import TELEGRAM_USER_ID, TELEGRAM_BOT_TOKEN
import requests

def notificar_agendamento():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensagem = f"⏰ Verificação diária de jogos iniciada às {agora}."
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": mensagem
    }
    requests.post(url, data=payload)

def verificar_jogos():
    notificar_agendamento()
    monitorar_partidas()

schedule.every().day.at("08:00").do(verificar_jogos)
schedule.every().day.at("12:00").do(verificar_jogos)
schedule.every().day.at("18:00").do(verificar_jogos)

print("⏳ Bot de futebol iniciado! Esperando horários agendados...")

while True:
    schedule.run_pending()
    time.sleep(1)
