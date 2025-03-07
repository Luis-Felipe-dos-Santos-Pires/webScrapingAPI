from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

app = FastAPI()

# Função para fazer Web Scraping no Google Maps
def scrape_google_maps(cidade: str, segmento: str):
    # Configuração do Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executa sem abrir o navegador
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    # Monta a URL de busca no Google Maps
    busca = f"{segmento} em {cidade}"
    url = f"https://www.google.com/maps/search/{busca.replace(' ', '+')}"
    
    driver.get(url)
    time.sleep(5)  # Aguarda a página carregar

    estabelecimentos = []

    try:
        # Captura a lista de resultados
        resultados = driver.find_elements(By.CLASS_NAME, "Nv2PK")

        for resultado in resultados[:10]:  # Limita a 10 estabelecimentos para evitar bloqueio
            try:
                nome = resultado.find_element(By.CLASS_NAME, "qBF1Pd").text
            except:
                nome = "Nome não encontrado"

            try:
                endereco = resultado.find_element(By.CLASS_NAME, "W4Efsd").text
            except:
                endereco = "Endereço não encontrado"

            try:
                telefone = resultado.find_element(By.CLASS_NAME, "UsdlK").text
            except:
                telefone = "Telefone não encontrado"

            estabelecimentos.append({"Nome": nome, "Endereço": endereco, "Telefone": telefone})

    except Exception as e:
        print(f"Erro ao buscar os dados: {e}")

    driver.quit()
    return estabelecimentos

# Função para gerar o arquivo Excel
def gerar_excel(dados, cidade, segmento):
    df = pd.DataFrame(dados)
    filename = f"{segmento}_{cidade}.xlsx"
    df.to_excel(filename, index=False, engine="openpyxl")
    return filename

# Endpoint da API para gerar e retornar o Excel
@app.get("/scrape")
def get_excel(cidade: str = Query(..., title="Cidade"), segmento: str = Query(..., title="Segmento")):
    dados = scrape_google_maps(cidade, segmento)

    if not dados:
        return {"erro": "Nenhum dado encontrado"}

    filename = gerar_excel(dados, cidade, segmento)

    return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=filename)

