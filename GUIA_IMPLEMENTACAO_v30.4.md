# Guia de Implementação - Pharmyrus v30.4 Enhanced Reporting

## 🎯 Objetivo

Integrar o módulo de enhanced reporting ao pipeline principal do Pharmyrus para que **todas** as buscas de moléculas gerem automaticamente JSONs aprimorados com:
- Contabilização detalhada por tier
- Comparativo Cortellis aprimorado
- Disclaimers jurídicos profundos (PT/EN)
- Análise de patent cliff futuro

---

## 📦 Arquivos Necessários

```
pharmyrus-v30.4/
├── enhanced_reporting.py          # Módulo principal (NOVO)
├── apply_enhancement.py            # Script standalone (opcional)
└── main_v30.3_MINIMAL.py          # Atualizar para chamar enhancement
```

---

## 🔧 Opção 1: Integração Automática (Recomendado)

### Passo 1: Adicionar enhanced_reporting.py ao projeto

```bash
# Copiar para o diretório do projeto
cp enhanced_reporting.py /path/to/pharmyrus-v30.4/
```

### Passo 2: Modificar main_v30.3_MINIMAL.py

**Adicionar import no topo:**
```python
from enhanced_reporting import enhance_json_output
```

**Localizar a parte onde o JSON final é salvo** (geralmente no final da função `run_pharmyrus_search` ou similar):

**ANTES:**
```python
# Salvar resultado final
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=2)

logger.info(f"✅ Busca concluída: {output_path}")
```

**DEPOIS:**
```python
# ===== PHARMYRUS v30.4 - ENHANCED REPORTING =====
logger.info("Aplicando Enhanced Reporting v30.4...")
try:
    enhanced_result = enhance_json_output(final_result)
    logger.info("✅ Enhanced reporting aplicado com sucesso")
except Exception as e:
    logger.error(f"⚠️ Erro no enhanced reporting: {e}")
    logger.error("Continuando com JSON original...")
    enhanced_result = final_result
# ================================================

# Salvar resultado final
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(enhanced_result, f, ensure_ascii=False, indent=2)

logger.info(f"✅ Busca concluída: {output_path}")
```

### Passo 3: Testar

```bash
python main_v30.3_MINIMAL.py --molecule="Imatinib" --countries=BR
```

**Verificar no JSON de saída:**
- ✅ Seção `legal_framework` presente
- ✅ Seção `cortellis_audit_enhanced` presente
- ✅ Eventos com `enhanced_v30_4` metadata
- ✅ Patent cliff com análise preditiva

---

## 🔧 Opção 2: Script Pós-Processamento (Alternativa)

Se preferir não modificar o main, pode usar como pós-processamento:

### Criar script wrapper:

```python
#!/usr/bin/env python3
"""
Wrapper para aplicar enhanced reporting após busca normal
"""
import sys
import json
from enhanced_reporting import enhance_json_output

def enhance_existing_json(input_path, output_path=None):
    """Aplica enhancement a JSON existente"""
    if output_path is None:
        output_path = input_path.replace('.json', '_ENHANCED.json')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    enhanced = enhance_json_output(data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Enhanced JSON salvo: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python enhance_existing.py <input.json> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    enhance_existing_json(input_file, output_file)
```

**Uso:**
```bash
# Busca normal
python main_v30.3_MINIMAL.py --molecule="Imatinib" --countries=BR

# Aplicar enhancement
python enhance_existing.py imatinib_BR.json
```

---

## 🧪 Testes Recomendados

### 1. Teste Unitário

```python
import json
from enhanced_reporting import enhance_json_output

def test_enhancement():
    """Teste básico do enhancement"""
    # Carregar JSON de teste
    with open('darolutamide_BR_-_15.json', 'r') as f:
        test_data = json.load(f)
    
    # Aplicar enhancement
    enhanced = enhance_json_output(test_data)
    
    # Verificações
    assert 'legal_framework' in enhanced
    assert 'cortellis_audit_enhanced' in enhanced
    assert enhanced['legal_framework']['enhancement_applied'] == True
    
    pred_intel = enhanced['predictive_intelligence']
    assert 'by_confidence_tier_detailed' in pred_intel['summary']
    
    print("✅ Todos os testes passaram!")

if __name__ == "__main__":
    test_enhancement()
```

### 2. Teste de Regressão

**Moléculas de teste recomendadas:**
- Darolutamide ✅ (já testado)
- Ixazomib (oncológico, muitas patentes)
- Paracetamol (genérico, poucas patentes)
- Trastuzumab (biológico)

**Executar:**
```bash
for molecule in "Ixazomib" "Paracetamol" "Trastuzumab"; do
    echo "Testando $molecule..."
    python main_v30.4.py --molecule="$molecule" --countries=BR
    
    # Verificar se tem legal_framework
    python -c "import json; d=json.load(open('${molecule}_BR.json')); assert 'legal_framework' in d"
    echo "✅ $molecule OK"
done
```

### 3. Teste de Performance

```python
import time
import json
from enhanced_reporting import enhance_json_output

# Carregar JSON
with open('darolutamide_BR_-_15.json', 'r') as f:
    data = json.load(f)

# Benchmark
start = time.time()
enhanced = enhance_json_output(data)
elapsed = time.time() - start

print(f"Tempo de enhancement: {elapsed:.3f}s")
print(f"Tamanho original: {len(json.dumps(data))} chars")
print(f"Tamanho enhanced: {len(json.dumps(enhanced))} chars")
print(f"Overhead: +{len(json.dumps(enhanced)) - len(json.dumps(data))} chars")

# Meta: < 2 segundos para JSONs típicos
assert elapsed < 2.0, f"Enhancement muito lento: {elapsed}s"
print("✅ Performance aceitável")
```

---

## 📊 Validação de Deployment

### Checklist pré-deploy:

- [ ] `enhanced_reporting.py` no diretório do projeto
- [ ] Import adicionado em `main_v30.3_MINIMAL.py`
- [ ] Chamada a `enhance_json_output()` antes de salvar JSON
- [ ] Try-catch para não quebrar em caso de erro
- [ ] Testes unitários passando
- [ ] 3+ moléculas testadas com sucesso
- [ ] Performance < 2s por enhancement
- [ ] Documentação atualizada no README.md

### Checklist pós-deploy (Railway):

- [ ] Variáveis de ambiente configuradas
- [ ] Build bem-sucedido
- [ ] Logs não mostram erros de enhanced reporting
- [ ] Primeira busca produz JSON com `legal_framework`
- [ ] Disclaimers bilíngues presentes
- [ ] Patent cliff enhanced presente

---

## 🔄 Rollback (se necessário)

Se encontrar problemas após deployment:

### Opção 1: Desabilitar temporariamente

```python
# Em main_v30.3_MINIMAL.py
ENABLE_ENHANCED_REPORTING = False  # Adicionar no topo

# No código
if ENABLE_ENHANCED_REPORTING:
    enhanced_result = enhance_json_output(final_result)
else:
    enhanced_result = final_result
```

### Opção 2: Reverter commit

```bash
git revert <commit_hash_do_enhancement>
git push origin main
```

### Opção 3: Remover import

Simplesmente comentar:
```python
# from enhanced_reporting import enhance_json_output

# ... e no final ...
# enhanced_result = enhance_json_output(final_result)
enhanced_result = final_result  # Usar original
```

---

## 🎓 Treinamento da Equipe

### Para Desenvolvedores:

1. **Entender estrutura de tiers:**
   - INFERRED (0.70-0.84): Família PCT confirmada
   - EXPECTED (0.50-0.69): Padrão histórico
   - PREDICTED (0.30-0.49): ML sem corroboração
   - SPECULATIVE (<0.30): Análise tecnológica

2. **Saber onde encontrar disclaimers:**
   - Globais: `json['legal_framework']`
   - Por evento: `json['predictive_intelligence']['inferred_events'][i]['warnings']`
   - Cortellis: `json['cortellis_audit_enhanced']['legal_disclaimers']`

3. **Debug de problemas:**
   ```python
   # Se enhancement falhar, verificar:
   logger.error(f"Keys disponíveis: {list(final_result.keys())}")
   logger.error(f"Predictive intel: {final_result.get('predictive_intelligence', {}).keys()}")
   ```

### Para Time de Negócios:

1. **Interpretar o JSON:**
   - `logical_match_rate`: % de concordância familiar com Cortellis
   - `total_advantage`: quantas patentes/predições a mais que Cortellis
   - `risk_assessment`: urgência do patent cliff

2. **Apresentar para clientes:**
   - Usar `RESUMO_EXECUTIVO_v30.4.md` como template
   - Destacar 93% de economia
   - Enfatizar transparência vs. caixa-preta do Cortellis

---

## 📞 Suporte

### Logs importantes:

```python
# Se enhanced reporting falhar, verificar:
tail -f logs/pharmyrus.log | grep -i "enhanced"

# Erros típicos:
# - "KeyError: 'predictive_intelligence'" → JSON não tem predições
# - "AttributeError: 'NoneType'" → Algum campo None inesperado
```

### Contato:

- **Desenvolvedor:** Daniel Silva
- **Versão:** v30.4
- **Data:** 2026-01-11

---

## ✅ Status de Implementação

| Componente | Status | Testado |
|------------|--------|---------|
| enhanced_reporting.py | ✅ Completo | ✅ Sim (Darolutamide) |
| Integração main.py | 🔄 Pendente | ⏳ Aguardando |
| Testes unitários | ✅ Completo | ✅ Sim |
| Testes regressão | 🔄 Parcial | ⏳ 1/4 moléculas |
| Deploy Railway | ⏳ Pendente | ❌ Não |
| Documentação | ✅ Completo | N/A |

---

**Última atualização:** 2026-01-11  
**Versão do guia:** 1.0  
**Próxima revisão:** Após primeiro deploy em produção
