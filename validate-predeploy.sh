#!/bin/bash
# Script de validação pre-deploy para Railway

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  VALIDAÇÃO PRE-DEPLOY - Pharmyrus v30.4-ENHANCED-FIXED              ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0
warnings=0

# 1. Verificar Dockerfile
echo "1️⃣  VERIFICANDO DOCKERFILE..."
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile não encontrado${NC}"
    errors=$((errors+1))
else
    echo -e "${GREEN}✅ Dockerfile encontrado${NC}"
    
    # Verificar se enhanced_reporting está no Dockerfile
    if grep -q "COPY enhanced_reporting.py" Dockerfile; then
        echo -e "${GREEN}✅ enhanced_reporting.py está no Dockerfile${NC}"
    else
        echo -e "${RED}❌ enhanced_reporting.py NÃO está no Dockerfile${NC}"
        errors=$((errors+1))
    fi
fi
echo ""

# 2. Verificar arquivos Python essenciais
echo "2️⃣  VERIFICANDO ARQUIVOS PYTHON..."
required_files=(
    "main_v30.3_MINIMAL.py"
    "enhanced_reporting.py"
    "google_patents_crawler.py"
    "inpi_crawler.py"
    "wipo_crawler.py"
    "predictive_layer.py"
    "applicant_learning.py"
    "celery_app.py"
    "tasks.py"
    "merge_logic.py"
    "patent_cliff.py"
    "family_resolver.py"
    "materialization.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file NÃO ENCONTRADO${NC}"
        errors=$((errors+1))
    fi
done
echo ""

# 3. Verificar arquivos de dados
echo "3️⃣  VERIFICANDO ARQUIVOS DE DADOS..."
if [ -f "applicant_database.json" ]; then
    echo -e "${GREEN}✅ applicant_database.json${NC}"
else
    echo -e "${RED}❌ applicant_database.json NÃO ENCONTRADO${NC}"
    errors=$((errors+1))
fi

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt${NC}"
else
    echo -e "${RED}❌ requirements.txt NÃO ENCONTRADO${NC}"
    errors=$((errors+1))
fi
echo ""

# 4. Verificar diretório core
echo "4️⃣  VERIFICANDO DIRETÓRIO CORE..."
if [ -d "core" ]; then
    echo -e "${GREEN}✅ core/ existe${NC}"
    
    if [ -f "core/__init__.py" ]; then
        echo -e "${GREEN}✅ core/__init__.py${NC}"
    else
        echo -e "${YELLOW}⚠️  core/__init__.py ausente (criando...)${NC}"
        echo '"""Core search engine module"""' > core/__init__.py
        warnings=$((warnings+1))
    fi
    
    if [ -f "core/search_engine.py" ]; then
        # Verificar se não é um Dockerfile
        if head -1 core/search_engine.py | grep -q "^FROM "; then
            echo -e "${RED}❌ core/search_engine.py é um Dockerfile!${NC}"
            errors=$((errors+1))
        else
            echo -e "${GREEN}✅ core/search_engine.py${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  core/search_engine.py ausente${NC}"
        warnings=$((warnings+1))
    fi
else
    echo -e "${RED}❌ core/ diretório NÃO ENCONTRADO${NC}"
    errors=$((errors+1))
fi
echo ""

# 5. Verificar imports no main
echo "5️⃣  VERIFICANDO IMPORTS NO MAIN..."
if grep -q "from enhanced_reporting import enhance_json_output" main_v30.3_MINIMAL.py; then
    echo -e "${GREEN}✅ Import do enhanced_reporting presente${NC}"
else
    echo -e "${RED}❌ Import do enhanced_reporting AUSENTE${NC}"
    errors=$((errors+1))
fi

# Verificar ordem do logger
logger_def=$(grep -n 'logger = logging.getLogger("pharmyrus")' main_v30.3_MINIMAL.py | cut -d: -f1)
logger_use=$(grep -n 'logger.info("✅ Enhanced Reporting' main_v30.3_MINIMAL.py | cut -d: -f1)

if [ -n "$logger_def" ] && [ -n "$logger_use" ]; then
    if [ "$logger_def" -lt "$logger_use" ]; then
        echo -e "${GREEN}✅ Logger definido ANTES de ser usado (linha $logger_def < linha $logger_use)${NC}"
    else
        echo -e "${RED}❌ Logger usado ANTES de ser definido (linha $logger_use < linha $logger_def)${NC}"
        errors=$((errors+1))
    fi
else
    echo -e "${YELLOW}⚠️  Não foi possível verificar ordem do logger${NC}"
    warnings=$((warnings+1))
fi
echo ""

# 6. Validação Python syntax
echo "6️⃣  VERIFICANDO SINTAXE PYTHON..."
if command -v python3 &> /dev/null; then
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                echo -e "${GREEN}✅ $file (sintaxe OK)${NC}"
            else
                echo -e "${RED}❌ $file (erro de sintaxe)${NC}"
                errors=$((errors+1))
            fi
        fi
    done
else
    echo -e "${YELLOW}⚠️  Python3 não disponível para validação${NC}"
    warnings=$((warnings+1))
fi
echo ""

# Resumo
echo "═══════════════════════════════════════════════════════════════════════"
echo "RESUMO DA VALIDAÇÃO"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Erros: $errors"
echo "Avisos: $warnings"
echo ""

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}🎉 VALIDAÇÃO COMPLETA - PRONTO PARA DEPLOY!${NC}"
    echo ""
    echo "Próximos passos:"
    echo "  1. railway up"
    echo "  2. Verificar logs: railway logs | grep 'Enhanced Reporting'"
    echo ""
    exit 0
else
    echo -e "${RED}❌ VALIDAÇÃO FALHOU - $errors erro(s) encontrado(s)${NC}"
    echo ""
    echo "Corrija os erros antes de fazer deploy!"
    echo ""
    exit 1
fi
