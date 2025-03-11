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
