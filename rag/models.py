from dotenv import load_dotenv, find_dotenv
import os
from timescale_vector import client
import uuid
from datetime import datetime, timedelta
from google import genai
from django.db import models
from pgvector.django import VectorField


class Embeddings(models.Model):

    anchor_data = models.OneToOneField(
        'tickers.News',
        on_delete=models.CASCADE,
        related_name='embedding'
    )
    # Vector definido com 768 dimensões, expecífico pro gemini
    vector = VectorField(dimensions=768)

    # Uma, cópia do texto que gerou o vetor
    content = models.TextField()

    #Para filtros SQL (ex : {'categoria': 'financeiro', 'autor_id': 1})
    metadata = models.JSONField(default=dict, blank=True)

    #Controle de tempo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Embedding de {self.anchor_data}'

    class Meta:
        verbose_name = 'Embedding'
        verbose_name_plural = 'Embeddings'
