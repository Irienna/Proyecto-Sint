# Proyecto-Sint

App para registrar qué comes y qué síntomas sientes después, que detecta
patrones de alimentos ligados a síntomas usando machine learning (reglas de
asociación).

## Cómo correrlo

```
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
python app.py
```

Abre [http://localhost:5000](http://localhost:5000) en tu navegador.

Necesitas al menos 10 registros para que empiecen a aparecer patrones.
Tus datos se guardan localmente en `data/entries.json` (no se sube a git).
