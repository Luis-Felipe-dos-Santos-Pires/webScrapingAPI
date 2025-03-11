from fastapi import FastAPI, Query
from fastapi.responses import FileResponse,StreamingResponse
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from io import BytesIO
from dataclasses import dataclass
from credentials import APIKey
import requests

url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

app = FastAPI()

def scrape_google_maps(cidade: str, segmento: str):
    params = {
        "query": f"{cidade} {segmento}",
        "key": APIKey
    }
    response = requests.get(url, params=params)
    data = response.json()
    estabelecimentos = []
    for result in data["results"]:
        estabelecimentos.append(
            {
                "Nome": result["name"], 
                "Endereço": result["formatted_address"], 
                "Telefone": "Sem telefone nesta API" ## Pendente de implementação
            }
        )
    return estabelecimentos

@dataclass
class Sheet:
    headers: object
    content: bytes

def gerar_excel(dados, cidade, segmento):
    df = pd.DataFrame(dados)
    content = BytesIO()
    with pd.ExcelWriter(content, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")
    content.seek(0)
    headers = {
        "Content-Disposition": f"attachment;{segmento}_{cidade}.xlsx"
    }
    return Sheet(
        headers = headers,
        content = content
    )

@app.get("/scrape")
def get_excel(cidade: str = Query(..., title="Cidade"), segmento: str = Query(..., title="Segmento")):
    dados = scrape_google_maps(cidade, segmento)
    if not dados:
        return {"erro": "Nenhum dado encontrado"}
    sheet = gerar_excel(dados, cidade, segmento)
    return StreamingResponse(sheet.content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=sheet.headers)

# Recuperar telefones para implementar
"""
import concurrent.futures

def get_phone_number(place_id):
    place_details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    place_details_params = {
        "place_id": place_id,
        "key": API_KEY,
        "fields": "formatted_phone_number"
    }
    response = requests.get(place_details_url, params=place_details_params)
    data = response.json()
    return data["result"].get("formatted_phone_number", "N/A")

# List of place_ids from the Text Search
place_ids = [result["place_id"] for result in text_search_data["results"]]

# Use ThreadPoolExecutor for parallel requests
with concurrent.futures.ThreadPoolExecutor() as executor:
    phone_numbers = list(executor.map(get_phone_number, place_ids))

# Print results
for result, phone_number in zip(text_search_data["results"], phone_numbers):
    print(f"Name: {result['name']}, Address: {result['formatted_address']}, Phone: {phone_number}")
"""