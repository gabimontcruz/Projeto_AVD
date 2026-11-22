"""
Script para download automático do dataset da Parte Específica (The Complete Pokemon Dataset - Kaggle).
Fonte original: https://www.kaggle.com/datasets/rounakbanik/pokemon
Mirror de repositório público com os mesmos 801 Pokémons e 41 variáveis.
"""

import os
import urllib.request

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_PATH = os.path.join(DATA_DIR, "pokemon.csv")
SOURCE_URL = "https://raw.githubusercontent.com/darszam/WhatMakesPokemonLegendary/master/pokemon.csv"

def download():
    print(f"Baixando dataset Pokémon para: {TARGET_PATH}")
    urllib.request.urlretrieve(SOURCE_URL, TARGET_PATH)
    file_size = os.path.getsize(TARGET_PATH)
    print(f"Download concluído com sucesso! Tamanho do arquivo: {file_size / 1024:.2f} KB")

if __name__ == "__main__":
    download()
