# agent-memory/utils/search_memory.py
import json
from pathlib import Path

MEMORY_FILE = Path(__file__).resolve().parent.parent / "memory.json"


def search_memory(query: str):
    """Busca eventos no memory.json por palavra-chave ou data."""
    if not MEMORY_FILE.exists():
        return ["Nenhuma memória encontrada."]

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            memories = json.load(f)
        except json.JSONDecodeError:
            return ["Erro ao ler o arquivo de memória."]

    resultados = []
    for item in memories.get("events", []):
        texto_evento = str(item).lower()
        if query.lower() in texto_evento:
            resultados.append(item)

    if not resultados:
        return [f"Nenhum evento encontrado para: {query}"]

    return resultados
