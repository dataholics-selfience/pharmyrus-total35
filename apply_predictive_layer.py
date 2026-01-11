#!/usr/bin/env python3
"""
Aplicar LAYER 4 Predictive Intelligence aos resultados do Darolutamide
"""

import json
import sys
from pathlib import Path

# Importar o engine preditivo
sys.path.insert(0, str(Path(__file__).parent))
from pharmyrus_layer4_predictive import process_patent_search_results

def load_darolutamide_unified():
    """Carregar arquivo unified existente"""
    unified_path = Path("/mnt/project/darolutamide-unified.json")
    
    if not unified_path.exists():
        print(f"❌ Arquivo não encontrado: {unified_path}")
        return None
    
    with open(unified_path, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_unified_to_predictive_format(unified_data):
    """
    Converter formato unified para formato esperado pelo engine preditivo
    """
    # Extrair WOs
    wo_patents = []
    consolidated = unified_data.get("consolidated_patents", [])
    
    for item in consolidated:
        wo_data_raw = item.get("wo_data", {})
        
        wo_patents.append({
            "publication_number": wo_data_raw.get("publication_number"),
            "priority_date": wo_data_raw.get("priority_date"),
            "filing_date": wo_data_raw.get("filing_date"),
            "assignees": wo_data_raw.get("assignees", []),
            "ipc_classifications": wo_data_raw.get("ipc_classifications", []),
            "cpc_classifications": wo_data_raw.get("cpc_classifications", []),
            "family_members": [],  # Pode enriquecer depois
            "title": wo_data_raw.get("title", ""),
            "abstract": wo_data_raw.get("abstract", "")
        })
    
    # Extrair BRs encontradas
    br_patents = []
    for item in consolidated:
        national_patents = item.get("national_patents", {})
        br_list = national_patents.get("BR", [])
        
        for br in br_list:
            br_patents.append({
                "publication_number": br.get("patent_number"),
                "wo_related": item.get("wo_number"),
                "title": br.get("bibliographic_data", {}).get("title", ""),
                "filing_date": br.get("dates", {}).get("filing_date"),
                "publication_date": br.get("dates", {}).get("publication_date"),
                "legal_status": br.get("legal_status"),
                "patent_type": br.get("patent_type")
            })
    
    return {
        "molecule_name": unified_data.get("metadata", {}).get("molecule_name", {}).get("molecule_name", "Unknown"),
        "wo_patents": wo_patents,
        "br_patents": br_patents,
        "metadata": unified_data.get("metadata", {}),
        "statistics": unified_data.get("statistics", {})
    }

def main():
    print("\n🔬 PHARMYRUS - LAYER 4: Juridical Predictive Intelligence")
    print("=" * 80)
    print("Aplicando inferências preditivas aos resultados do Darolutamide...")
    print()
    
    # Carregar dados unified
    print("📂 Carregando darolutamide-unified.json...")
    unified_data = load_darolutamide_unified()
    
    if not unified_data:
        print("❌ Falha ao carregar dados")
        return 1
    
    print(f"✅ Dados carregados: {unified_data.get('metadata', {}).get('total_wo_patents', 0)} WOs, "
          f"{unified_data.get('metadata', {}).get('total_national_patents', 0)} patentes nacionais")
    
    # Converter formato
    print("\n🔄 Convertendo para formato preditivo...")
    converted_data = convert_unified_to_predictive_format(unified_data)
    print(f"✅ Convertido: {len(converted_data['wo_patents'])} WOs, {len(converted_data['br_patents'])} BRs")
    
    # Aplicar LAYER 4
    print("\n🧠 Aplicando inteligência preditiva...")
    enriched_results = process_patent_search_results(converted_data)
    
    # Estatísticas
    predictive = enriched_results.get("predictive_intelligence", {})
    summary = predictive.get("summary", {})
    
    print("\n📊 RESULTADOS DA CAMADA PREDITIVA:")
    print(f"   Total de WOs analisados: {summary.get('total_wo_analyzed', 0)}")
    print(f"   WOs com BRs encontradas: {summary.get('wos_with_found_br', 0)}")
    print(f"   WOs sem BRs (analisados): {summary.get('wos_without_br', 0)}")
    print(f"   Predições de BRs geradas: {summary.get('predicted_br_filings', 0)}")
    print(f"   Predições alta confiança (≥70%): {summary.get('high_confidence_predictions', 0)}")
    
    # Mostrar algumas predições de alta confiança
    high_conf = predictive.get("high_confidence_only", [])
    if high_conf:
        print(f"\n🎯 TOP 5 PREDIÇÕES DE ALTA CONFIANÇA:")
        for i, pred in enumerate(high_conf[:5], 1):
            status_info = pred.get("patent_status", {})
            inference = pred.get("inference_details", {})
            pct = inference.get("pct_timeline", {})
            applicant = inference.get("applicant_analysis", {})
            
            print(f"\n   {i}. WO: {pred.get('wo_number')}")
            print(f"      Status: {status_info.get('type')} ({status_info.get('certainty_level')})")
            print(f"      Confiança: {status_info.get('confidence_score', 0):.1%}")
            print(f"      Prazo: {pct.get('days_remaining', 0)} dias restantes")
            print(f"      Depositante: {applicant.get('name', 'Unknown')} "
                  f"(taxa BR: {applicant.get('historical_br_filing_rate', 0):.0%})")
    
    # Salvar resultado enriquecido
    output_path = Path("/home/claude/darolutamide-predictive-v31.json")
    print(f"\n💾 Salvando resultados em: {output_path}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Arquivo salvo com sucesso!")
    print(f"\n📋 Estrutura do output:")
    print(f"   - Todos os dados originais mantidos")
    print(f"   - Nova seção: 'predictive_intelligence'")
    print(f"   - Predições completas com metadata de certeza")
    print(f"   - Disclaimer legal incluído")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
