from django.db import models


class Ticker(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    company_name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    technical_metrics = models.JSONField(blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    market_cap = models.BigIntegerField(null=True,blank=True)
    country=models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.symbol} - {self.technical_metrics}'


class News(models.Model):
    class Sentiment(models.TextChoices):
        BULLISH = 'BULLISH', 'Bullish'
        BEARISH = 'BEARISH', 'Bearish'
        NEUTRAL = 'NEUTRAL', 'Neutral'

    ticker = models.ForeignKey(Ticker, on_delete=models.CASCADE, related_name='news')
    headline = models.TextField()
    source_url = models.URLField(unique=True, max_length=500, blank=True)
    market_feeling = models.CharField(
        max_length=10,
        choices=Sentiment,
        default=Sentiment.NEUTRAL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f'{self.ticker.symbol} - {self.headline}'
