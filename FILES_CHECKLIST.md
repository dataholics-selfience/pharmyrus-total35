# 📋 CHECKLIST DE ARQUIVOS NECESSÁRIOS

## ✅ OBRIGATÓRIOS (devem estar no repositório)

### Core Application
- [ ] main_v30.3_PREDICTIVE.py (renomear para main.py no deploy)
- [ ] requirements.txt
- [ ] Dockerfile

### Predictive Layer (v30.3)
- [ ] predictive_layer.py
- [ ] applicant_learning.py
- [ ] applicant_database.json

### Crawlers (v30.2)
- [ ] google_patents_crawler.py
- [ ] inpi_crawler.py
- [ ] merge_logic.py
- [ ] patent_cliff.py

## ⚠️ OPCIONAIS (app funciona sem eles)

- [ ] wipo_crawler.py (opcional - app verifica com try/except)
- [ ] celery_app.py (opcional - para async jobs)

---

## 🔍 COMO VERIFICAR

No seu repositório GitHub, deve ter PELO MENOS estes arquivos:

```bash
pharmyrus/
├── main_v30.3_PREDICTIVE.py  # ← Será copiado como main.py
├── requirements.txt
├── Dockerfile
├── predictive_layer.py
├── applicant_learning.py
├── applicant_database.json
├── google_patents_crawler.py
├── inpi_crawler.py
├── merge_logic.py
└── patent_cliff.py
```

---

## ❌ SE FALTAREM ARQUIVOS

### google_patents_crawler.py
```python
# Criar arquivo vazio com stub
class GoogleCrawler:
    async def enrich_with_google(self, **kwargs):
        return set()

google_crawler = GoogleCrawler()
```

### inpi_crawler.py
```python
# Criar arquivo vazio com stub
class INPICrawler:
    async def search_inpi(self, **kwargs):
        return []
    
    async def search_by_numbers(self, numbers, **kwargs):
        return []

inpi_crawler = INPICrawler()
```

### merge_logic.py
```python
def merge_br_patents(list1, list2):
    """Simple merge by patent_number"""
    seen = set()
    merged = []
    
    for patent in list1 + list2:
        pnum = patent.get('patent_number')
        if pnum and pnum not in seen:
            seen.add(pnum)
            merged.append(patent)
    
    return merged
```

### patent_cliff.py
```python
from datetime import datetime, timedelta

def calculate_patent_cliff(patents):
    """Calculate patent expiration dates"""
    cliff_data = {}
    
    for patent in patents:
        filing_date = patent.get('filing_date')
        if filing_date:
            # Patent expires 20 years after filing
            try:
                filing = datetime.fromisoformat(filing_date.replace('Z', '+00:00'))
                expiry = filing + timedelta(days=20*365)
                cliff_data[patent.get('patent_number')] = {
                    'filing_date': filing_date,
                    'expiry_date': expiry.isoformat(),
                    'years_remaining': (expiry - datetime.now()).days / 365
                }
            except:
                pass
    
    return cliff_data
```

---

## 🚀 AÇÃO IMEDIATA

1. **Verificar repositório GitHub:**
   - Todos os 10 arquivos obrigatórios estão lá?

2. **Se faltarem arquivos:**
   - Criar stubs acima OU
   - Me diga quais faltam e crio completos

3. **Fazer commit e push:**
   ```bash
   git add .
   git commit -m "fix: Dockerfile corrigido v30.3"
   git push origin main
   ```

4. **Railway vai rebuildar automaticamente**
   - Deve funcionar agora!
