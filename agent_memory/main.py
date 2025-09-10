
from dotenv import load_dotenv, find_dotenv
import os
import json
import re
from datetime import datetime
from pathlib import Path
import speech_recognition as sr

from utils.record_audio import record_audio
from utils.search_memory import search_memory
from utils.database import init_db, save_event, search_events, search_events_by_date

# --- Setup
load_dotenv(find_dotenv())

# Inicializa SQLite
init_db()

MEMORY_PATH = Path("memory.json")


def pretty_date_from_iso(iso_date: str):
    try:
        return datetime.fromisoformat(iso_date).strftime("%d/%m/%Y")
    except Exception:
        return iso_date


date_regex = re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}')

print("Agente de Memória iniciado. Fale ou diga 'buscar ...' para pesquisar.")

while True:
    # carrega memory.json (compatibilidade)
    if MEMORY_PATH.exists():
        try:
            memory = json.load(open(MEMORY_PATH, "r", encoding="utf-8"))
        except Exception:
            memory = {"events": [], "interactions": []}
    else:
        memory = {"events": [], "interactions": []}

    # grava áudio
    filename_audio = record_audio()

    # transcreve com Google SpeechRecognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename_audio) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="pt-BR")
        print(f"📝 Transcrição (Google Speech): {text}")
    except sr.UnknownValueError:
        text = ""
        print("⚠️ Não consegui entender o áudio.")
    except sr.RequestError as e:
        text = ""
        print(f"⚠️ Erro ao acessar o Google Speech API: {e}")

    # remover arquivo temporário
    try:
        os.remove(filename_audio)
    except Exception:
        pass

    if not text:
        continue

    # --- Comandos de busca ---
    lower = text.lower()
    if lower.startswith("buscar") or lower.startswith("procurar"):
        # tenta extrair duas datas para busca por intervalo
        date_matches = date_regex.findall(text)
        if len(date_matches) >= 2:
            start_date = date_matches[0]
            end_date = date_matches[1]
            print(
                f"🔎 Buscando eventos de {start_date} até {end_date} no SQLite...")
            resultados = search_events_by_date(start_date, end_date)
            if resultados:
                for r in resultados:
                    print(f"[{pretty_date_from_iso(r[1])}] {r[2]}")
            else:
                print("Nenhum evento encontrado nesse período.")
            continue

        # caso normal: "buscar palavra"
        termo = text.split(" ", 1)[1] if " " in text else ""
        print("🔍 Resultados da busca no JSON:")
        for r in search_memory(termo):
            print(r)

        print("🔍 Resultados da busca no SQLite:")
        resultados = search_events(termo)
        if resultados:
            for r in resultados:
                print(f"[{pretty_date_from_iso(r[1])}] {r[2]}")
        else:
            print("Nenhum evento encontrado.")
        continue

    # --- Salvamento direto (offline) ---
    actual_date = datetime.now().strftime("%d/%m/%Y")

    # salvar no memory.json
    memory["events"].append(f"Day: {actual_date} - {text}")

    # salvar no SQLite
    save_event(date=actual_date, description=text)

    memory['interactions'].append(f"Human: {text}")
    memory['interactions'].append(
        "Assistant: Evento registrado com sucesso (modo offline).")

    print(f"✅ Evento salvo (offline): {actual_date} - {text}")

    # Gravar memory.json (compatibilidade)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
