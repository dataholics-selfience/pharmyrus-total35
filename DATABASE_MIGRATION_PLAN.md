# 📊 BANCO DE DADOS - RESPOSTA E PLANO DE MIGRAÇÃO

## ⚠️ SITUAÇÃO ATUAL

### Arquivo JSON vs Banco de Dados

**ATUALMENTE:** `applicant_database.json`
- Tipo: Arquivo JSON no filesystem
- Localização: `/app/applicant_database.json` no container
- Atualização: A cada busca via `applicant_learning.py`

### ❌ PROBLEMA

**Quando você faz upgrade de versão:**

```bash
# Deploy v30.3
Railway → applicant_database.json crescendo
         33 empresas → 50 empresas → 80 empresas

# Deploy v30.4 (novo código)
Railway → applicant_database.json RESETADO para 33 empresas ❌
         TODO O APRENDIZADO PERDIDO!
```

**Causa:** Docker rebuild cria novo container com arquivo original.

---

## ✅ SOLUÇÃO: MIGRAR PARA BANCO DE DADOS

### Opções de Banco

| Banco | Custo Railway | Vantagens | Desvantagens |
|-------|---------------|-----------|--------------|
| **PostgreSQL** | $5/mês | Relacional, robusto | Overkill para JSON |
| **MongoDB** | $0 (Atlas Free) | Nativo JSON | Externa à Railway |
| **Redis** | $5/mês | Já usado (Celery) | Volatil sem persistência |
| **Railway Volume** | $0 | Grátis | Limitado a 1GB |

### 🎯 RECOMENDAÇÃO: PostgreSQL + Railway

**Por quê:**
- ✅ Integrado com Railway (mesma VPC)
- ✅ Persistência garantida
- ✅ Backup automático
- ✅ Escalável para futuras features
- ✅ JSON nativo (type: JSONB)

---

## 🔧 COMO MIGRAR (30 minutos)

### 1. Adicionar PostgreSQL na Railway

```yaml
# railway.yml
services:
  web:
    build: .
    env:
      - DATABASE_URL=${{Postgres.DATABASE_URL}}
  
  postgres:
    plugin: postgres
    plan: hobby  # $5/month
```

### 2. Criar Tabela

```sql
CREATE TABLE applicant_database (
    applicant_name VARCHAR(255) PRIMARY KEY,
    data JSONB NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_applicant_name ON applicant_database(applicant_name);
CREATE INDEX idx_last_updated ON applicant_database(last_updated);
```

### 3. Modificar `applicant_learning.py`

```python
import psycopg2
import os

class ApplicantLearningSystem:
    def __init__(self, database_url=None):
        """
        Initialize with PostgreSQL instead of JSON file.
        
        Args:
            database_url: PostgreSQL connection string
                          Default: from env DATABASE_URL
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.conn = psycopg2.connect(self.database_url)
    
    def _load_database(self) -> Dict:
        """Load from PostgreSQL instead of JSON file."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT applicant_name, data FROM applicant_database")
        
        database = {}
        for row in cursor.fetchall():
            applicant_name, data_json = row
            database[applicant_name] = data_json  # Already dict from JSONB
        
        cursor.close()
        return database
    
    def _save_database(self):
        """Save to PostgreSQL instead of JSON file."""
        cursor = self.conn.cursor()
        
        for applicant_name, data in self.database.items():
            cursor.execute("""
                INSERT INTO applicant_database (applicant_name, data)
                VALUES (%s, %s)
                ON CONFLICT (applicant_name)
                DO UPDATE SET 
                    data = EXCLUDED.data,
                    last_updated = NOW()
            """, (applicant_name, json.dumps(data)))
        
        self.conn.commit()
        cursor.close()
```

### 4. Migração Inicial

```python
# migrate_to_postgres.py
import json
import psycopg2
import os

# Load JSON
with open('applicant_database.json') as f:
    data = json.load(f)

# Connect to PostgreSQL
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Insert all data
for applicant_name, applicant_data in data.items():
    cursor.execute("""
        INSERT INTO applicant_database (applicant_name, data)
        VALUES (%s, %s)
    """, (applicant_name, json.dumps(applicant_data)))

conn.commit()
cursor.close()
print(f"✅ Migrated {len(data)} applicants to PostgreSQL")
```

### 5. Atualizar `requirements.txt`

```txt
# Add PostgreSQL
psycopg2-binary==2.9.9
```

### 6. Atualizar `Dockerfile`

```dockerfile
# Install PostgreSQL client libs
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \  # <-- NOVO: Para psycopg2
    && rm -rf /var/lib/apt/lists/*
```

---

## 📊 COMPARAÇÃO: JSON vs PostgreSQL

### Com JSON (Atual)

```
Deploy v30.3 → applicant_database.json (33 empresas)
↓ 100 buscas
Database cresce → 80 empresas no container

Deploy v30.4 → REBUILD
applicant_database.json resetado → 33 empresas ❌
80 empresas aprendidas PERDIDAS!
```

### Com PostgreSQL (Futuro)

```
Deploy v30.3 → PostgreSQL (33 empresas)
↓ 100 buscas  
PostgreSQL cresce → 80 empresas no DB

Deploy v30.4 → REBUILD
applicant_database carregado do PostgreSQL → 80 empresas ✅
NADA PERDIDO! Continua aprendendo de onde parou.
```

---

## 🎯 QUANDO MIGRAR?

### Opções:

**1. AGORA (antes do deploy v30.3)**
- ✅ Já começa certo
- ❌ Atrasa deploy inicial

**2. DEPOIS (após validar v30.3)**
- ✅ Deploy rápido agora
- ✅ Migra quando frontend iniciar
- ❌ Perde primeiros aprendizados

**3. HÍBRIDO (melhor opção)**
- ✅ Deploy v30.3 com JSON agora
- ✅ Migra para PostgreSQL na v30.4
- ✅ **Solução:** Fazer backup manual do JSON antes de cada deploy

### 🎯 RECOMENDAÇÃO: Opção 3 (Híbrido)

**Agora (v30.3):**
1. Deploy com JSON
2. Testar sistema
3. Validar aprendizado

**Backup antes de cada deploy:**
```bash
# No Railway terminal:
cat /app/applicant_database.json > /tmp/backup.json
# Download via Railway CLI
railway run cat /app/applicant_database.json > applicant_db_backup.json
```

**Futuro (v30.4 ou frontend):**
1. Setup PostgreSQL na Railway
2. Migrar dados do JSON
3. Atualizar código
4. Deploy

---

## 💰 CUSTO

| Solução | Custo Mensal | Persistência | Complexidade |
|---------|--------------|--------------|--------------|
| JSON File | $0 | ❌ Perde em rebuild | Simples |
| Railway Volume | $0 | ✅ Persiste | Média |
| PostgreSQL | $5 | ✅ Persiste + Backup | Média |
| MongoDB Atlas | $0 (Free tier) | ✅ Persiste | Alta |

---

## 🚀 PLANO FINAL

### v30.3 (AGORA):
- ✅ JSON file (rápido, funciona)
- ✅ Backup manual antes de deploys
- ✅ Testar e validar sistema

### v30.4 (PRÓXIMA):
- ✅ Migrar para PostgreSQL
- ✅ Adicionar Railway Postgres plugin
- ✅ Rodar script de migração
- ✅ Persistência garantida

### Frontend (FUTURO):
- ✅ PostgreSQL já configurado
- ✅ Mesmo DB para applicants + usuários
- ✅ Queries SQL para dashboards

---

## 📝 RESUMO DA RESPOSTA

**PERGUNTA:** Banco de empresas fica em arquivo .py ou banco de dados?

**RESPOSTA:** 
- **ATUAL:** Arquivo JSON (`applicant_database.json`)
- **PROBLEMA:** Perde dados em rebuild/upgrade
- **SOLUÇÃO:** Migrar para PostgreSQL (~30min, $5/mês)
- **TIMING:** Pode fazer agora OU na próxima versão
- **RECOMENDAÇÃO:** Deploy v30.3 com JSON agora, migra para PostgreSQL quando fizer frontend

**CÓDIGO PRONTO:** Todo o código de migração está documentado acima, pronto para copiar quando decidir migrar.

---

**Conclusão:** Sistema já funciona com JSON. Quando quiser persistência permanente, basta seguir os passos acima! 🚀
