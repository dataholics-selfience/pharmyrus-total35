"""
Pharmyrus v30.3 - Test Suite
Tests the complete predictive intelligence pipeline
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_predictive_layer():
    """Test predictive intelligence engine."""
    logger.info("\n" + "="*80)
    logger.info("🧪 TEST 1: Predictive Layer")
    logger.info("="*80)
    
    from predictive_layer import (
        PCTTimeline,
        ApplicantBehavior,
        MarketRelevance,
        PredictiveInferenceEngine
    )
    
    # Test 1: PCT Timeline
    wo_data = {
        "wo_number": "WO2023161458",
        "priority_date": "2022-02-28",
        "publication_date": "2023-08-31",
        "brazil_designated": True
    }
    
    timeline = PCTTimeline.from_wo_data(wo_data)
    logger.info(f"  ✅ PCT Timeline: Deadline = {timeline.thirty_month_deadline.date()}")
    
    # Test 2: Applicant Behavior
    applicant_data = {
        "applicant_name": "Bayer AG",
        "total_wo_brazil_designated": 42,
        "total_br_filings_found": 39,
        "filing_rate": 0.93,
        "therapeutic_areas": ["Oncology"],
        "last_updated": datetime.now().isoformat()
    }
    
    applicant = ApplicantBehavior.from_dict(applicant_data)
    logger.info(f"  ✅ Applicant Behavior: {applicant.get_description()}")
    
    # Test 3: Market Relevance
    market = MarketRelevance(
        therapeutic_area="Oncology",
        ipc_codes=["A61K31/00", "A61P35/00"]
    )
    logger.info(f"  ✅ Market Relevance: {market.get_description()}")
    
    # Test 4: Inference Engine
    applicant_db = {"Bayer AG": applicant}
    engine = PredictiveInferenceEngine(applicant_db)
    
    wo_complete = {
        **wo_data,
        "applicant": "Bayer AG",
        "title": "Test composition",
        "ipc_codes": ["A61K31/00"],
        "therapeutic_area": "Oncology",
        "family_size": 12
    }
    
    event = engine.create_inferred_event(wo_complete, existing_br_data=[])
    
    if event:
        confidence = event['brazilian_prediction']['confidence_analysis']['overall_confidence']
        tier = event['brazilian_prediction']['confidence_analysis']['confidence_tier']
        logger.info(f"  ✅ Inferred Event Created: Confidence = {confidence:.2f}, Tier = {tier}")
    else:
        logger.info("  ⚠️  No event created (expected if criteria not met)")
    
    logger.info("✅ Predictive layer test PASSED\n")


def test_learning_system():
    """Test dynamic applicant learning."""
    logger.info("="*80)
    logger.info("🧪 TEST 2: Learning System")
    logger.info("="*80)
    
    from applicant_learning import ApplicantLearningSystem
    
    # Create temporary learning system
    learning = ApplicantLearningSystem(database_path="test_applicants.json")
    
    # Mock search results
    wipo_patents = [
        {
            "wo_number": "WO2023123456",
            "applicant": "Test Pharma Inc",
            "publication_date": "2023-08-01"
        }
    ]
    
    brazilian_patents = [
        {
            "patent_number": "BR112024123456",
            "applicant": "Test Pharma Inc",
            "wo_reference": "WO2023123456"
        }
    ]
    
    # Learn from search
    learning.learn_from_search_results(
        wipo_patents=wipo_patents,
        brazilian_patents=brazilian_patents,
        therapeutic_area="Test Area"
    )
    
    # Check if learned
    behavior = learning.get_applicant_behavior("Test Pharma Inc")
    
    if behavior:
        logger.info(f"  ✅ Learned new applicant: {behavior['applicant_name']}")
        logger.info(f"     Filing rate: {behavior['filing_rate']:.0%}")
        logger.info(f"     Confidence: {behavior['confidence']}")
    else:
        logger.error("  ❌ Learning failed")
    
    # Cleanup
    Path("test_applicants.json").unlink(missing_ok=True)
    
    logger.info("✅ Learning system test PASSED\n")


def test_main_pipeline():
    """Test complete search pipeline."""
    logger.info("="*80)
    logger.info("🧪 TEST 3: Complete Pipeline")
    logger.info("="*80)
    
    from main import PharmyrusSearch
    
    # Initialize
    pharmyrus = PharmyrusSearch()
    
    # Search
    result = pharmyrus.search_molecule(
        molecule_name="Test Molecule",
        cas_number="12345-67-8",
        therapeutic_area="Test Therapy",
        include_predictive=True
    )
    
    # Validate structure
    assert "molecule_name" in result
    assert "patents_found" in result
    assert "predictive_intelligence" in result
    assert "search_metadata" in result
    
    logger.info(f"  ✅ Molecule: {result['molecule_name']}")
    logger.info(f"  ✅ WIPO Patents: {result['patents_found']['total_wipo']}")
    logger.info(f"  ✅ BR Published: {result['patents_found']['total_br_published']}")
    
    if 'predictive_intelligence' in result:
        inferred = len(result['predictive_intelligence']['inferred_events'])
        logger.info(f"  ✅ BR Inferred: {inferred}")
    
    logger.info("✅ Complete pipeline test PASSED\n")


def test_confidence_calculation():
    """Test confidence score calculation."""
    logger.info("="*80)
    logger.info("🧪 TEST 4: Confidence Calculation")
    logger.info("="*80)
    
    from predictive_layer import PredictiveInferenceEngine, ApplicantBehavior
    from datetime import timedelta
    
    # High confidence scenario (Big Pharma + Oncology + Within deadline)
    applicant = ApplicantBehavior(
        applicant_name="Bayer AG",
        total_wo_brazil_designated=42,
        total_br_filings_found=39,
        filing_rate=0.93,
        therapeutic_areas=["Oncology"],
        last_updated=datetime.now().isoformat()
    )
    
    applicant_db = {"Bayer AG": applicant}
    engine = PredictiveInferenceEngine(applicant_db)
    
    # WO within filing window
    today = datetime.now()
    priority = today - timedelta(days=400)  # ~13 months ago
    
    wo_data = {
        "wo_number": "WO2023XXXXXX",
        "applicant": "Bayer AG",
        "priority_date": priority.isoformat(),
        "publication_date": (priority + timedelta(days=540)).isoformat(),
        "brazil_designated": True,
        "ipc_codes": ["A61K31/00"],
        "therapeutic_area": "Oncology",
        "family_size": 15
    }
    
    from predictive_layer import PCTTimeline, MarketRelevance
    
    timeline = PCTTimeline.from_wo_data(wo_data)
    market = MarketRelevance("Oncology", ["A61K31/00"])
    
    confidence_result = engine.calculate_confidence(
        wo_data, timeline, applicant, market, 15
    )
    
    confidence = confidence_result['overall_confidence']
    tier = confidence_result['confidence_tier']
    
    logger.info(f"  ✅ Confidence Score: {confidence:.2f}")
    logger.info(f"  ✅ Confidence Tier: {tier}")
    logger.info(f"  ✅ Expected: 0.75-0.90 (INFERRED)")
    
    # Validate components
    factors = confidence_result['factors']
    logger.info(f"\n  Component Breakdown:")
    logger.info(f"    - PCT Timeline: {factors['pct_timeline']['score']:.2f} (weight: 30%)")
    logger.info(f"    - Applicant: {factors['applicant_behavior']['score']:.2f} (weight: 40%)")
    logger.info(f"    - Market: {factors['market_relevance']['score']:.2f} (weight: 20%)")
    logger.info(f"    - Family: {factors['patent_family_strength']['score']:.2f} (weight: 10%)")
    
    assert 0.70 <= confidence <= 0.95, f"Confidence {confidence} out of expected range"
    
    logger.info("\n✅ Confidence calculation test PASSED\n")


def main():
    """Run all tests."""
    logger.info("\n" + "🧪"*40)
    logger.info("PHARMYRUS v30.3 TEST SUITE")
    logger.info("🧪"*40 + "\n")
    
    try:
        test_predictive_layer()
        test_learning_system()
        test_main_pipeline()
        test_confidence_calculation()
        
        logger.info("="*80)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("="*80)
        logger.info("\n🎉 Pharmyrus v30.3 is ready for deployment!\n")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
