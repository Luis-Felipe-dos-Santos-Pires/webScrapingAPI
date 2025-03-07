import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app, scrape_google_maps, gerar_excel

client = TestClient(app)

# Dados simulados para evitar chamadas reais ao Google Maps
mock_data = [
    {"Nome": "Restaurante Teste", "Endereço": "Rua Fictícia, 123", "Telefone": "(11) 99999-9999"},
    {"Nome": "Padaria Exemplo", "Endereço": "Avenida Fake, 456", "Telefone": "(21) 98888-8888"},
]

# Lista de cidades e segmentos para testar
test_cases = [
    ("São Paulo", "Restaurantes"),
    ("Rio de Janeiro", "Supermercados"),
    ("Belo Horizonte", "Padarias"),
    ("Curitiba", "Academias"),
    ("Salvador", "Hotéis"),
]

# Mockando a função scrape_google_maps para evitar scraping real
@pytest.mark.parametrize("cidade, segmento", test_cases)
@patch("main.scrape_google_maps", return_value=mock_data)
def test_api_response(mock_scrape, cidade, segmento):
    response = client.get(f"/scrape?cidade={cidade}&segmento={segmento}")
    assert response.status_code == 200  # Deve retornar status 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Mockando o web scraping para verificar se retorna a estrutura correta
@pytest.mark.parametrize("cidade, segmento", test_cases)
@patch("main.scrape_google_maps", return_value=mock_data)
def test_scraping(mock_scrape, cidade, segmento):
    resultado = scrape_google_maps(cidade, segmento)
    assert isinstance(resultado, list)  # Deve retornar uma lista
    assert len(resultado) == len(mock_data)  # Deve ter a mesma quantidade de resultados simulados
    assert resultado[0]["Nome"] == "Restaurante Teste"
    assert resultado[1]["Nome"] == "Padaria Exemplo"

# Mockando a geração do Excel
@pytest.mark.parametrize("cidade, segmento", test_cases)
@patch("main.scrape_google_maps", return_value=mock_data)
def test_excel_generation(mock_scrape, cidade, segmento):
    filename = gerar_excel(mock_data, cidade, segmento)
    assert filename.endswith(".xlsx")  # Verifica se o arquivo gerado é Excel
