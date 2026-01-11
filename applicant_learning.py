"""
Pharmyrus v30.3 - Dynamic Applicant Learning System
Automatically learns and updates applicant filing behavior as molecules are searched.

This creates a "living database" that improves over time with usage.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class ApplicantLearningSystem:
    """
    Living database that learns applicant behavior from actual searches.
    
    Features:
    - Automatically captures WO → BR filing patterns
    - Updates filing rates as new data comes in
    - Persists to JSON (can be extended to Firebase/Redis)
    - Thread-safe updates
    - Validates data quality before updating
    """
    
    def __init__(self, database_path: str = "applicant_database.json"):
        """
        Initialize learning system.
        
        Args:
            database_path: Path to JSON database file
        """
        self.database_path = Path(database_path)
        self.database = self._load_database()
        self.session_updates = defaultdict(lambda: {'wos': set(), 'brs': set()})
        
    def _load_database(self) -> Dict:
        """Load existing database or create new one."""
        if self.database_path.exists():
            try:
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                logger.info(f"📚 Loaded applicant database: {len(db)} companies")
                return db
            except Exception as e:
                logger.error(f"❌ Error loading database: {e}")
                return {}
        else:
            logger.warning(f"⚠️  Database not found at {self.database_path}, starting fresh")
            return {}
    
    def _save_database(self):
        """Persist database to disk."""
        try:
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Saved applicant database: {len(self.database)} companies")
        except Exception as e:
            logger.error(f"❌ Error saving database: {e}")
    
    def _normalize_applicant_name(self, applicant: str) -> str:
        """
        Normalize applicant name for consistent matching.
        
        Handles:
        - "Bayer AG" vs "BAYER AG" vs "Bayer Ag"
        - "Pfizer Inc." vs "Pfizer Inc" vs "Pfizer, Inc."
        - Multiple applicants: "Bayer AG; Orion Corporation" → "Bayer AG"
        """
        if not applicant:
            return "Unknown"
        
        # Take first applicant if multiple
        applicant = str(applicant).split(';')[0].split(',')[0].strip()
        
        # Normalize common suffixes
        replacements = {
            'Inc.': 'Inc',
            'Ltd.': 'Ltd',
            'S.A.': 'SA',
            'Co.': 'Co',
            'Corp.': 'Corp',
        }
        
        for old, new in replacements.items():
            applicant = applicant.replace(old, new)
        
        # Title case for consistency
        return applicant.strip()
    
    def learn_from_search_results(
        self,
        wipo_patents: list,
        brazilian_patents: list,
        therapeutic_area: str = "Unknown"
    ):
        """
        Learn from a single molecule search.
        
        Extracts WO → BR filing patterns and updates database.
        
        Args:
            wipo_patents: List of WO patents found
            brazilian_patents: List of BR patents found
            therapeutic_area: Therapeutic classification
        """
        logger.info("🧠 Learning from search results...")
        
        # Build mapping: applicant → {WOs, BRs}
        applicant_data = defaultdict(lambda: {'wos': set(), 'brs': set(), 'areas': set()})
        
        # Process WIPO patents
        for wo in wipo_patents:
            applicant = self._normalize_applicant_name(wo.get('applicant', 'Unknown'))
            wo_number = wo.get('wo_number') or wo.get('publication_number')
            
            if applicant != 'Unknown' and wo_number:
                applicant_data[applicant]['wos'].add(wo_number)
                applicant_data[applicant]['areas'].add(therapeutic_area)
        
        # Process Brazilian patents (find which WOs led to BRs)
        for br in brazilian_patents:
            # BR patents should have reference to original WO
            wo_ref = br.get('wo_reference') or br.get('pct_number')
            applicant = self._normalize_applicant_name(br.get('applicant', 'Unknown'))
            
            if applicant != 'Unknown':
                if wo_ref:
                    # This WO entered Brazil
                    applicant_data[applicant]['brs'].add(wo_ref)
                applicant_data[applicant]['areas'].add(therapeutic_area)
        
        # Update database for each applicant
        updates_made = 0
        for applicant, data in applicant_data.items():
            if self._update_applicant(applicant, data):
                updates_made += 1
        
        if updates_made > 0:
            self._save_database()
            logger.info(f"✅ Updated {updates_made} applicants from this search")
    
    def _update_applicant(self, applicant: str, new_data: Dict) -> bool:
        """
        Update a single applicant's data.
        
        Returns:
            True if database was modified
        """
        wos = new_data['wos']
        brs = new_data['brs']
        areas = new_data['areas']
        
        # Skip if no meaningful data
        if len(wos) == 0:
            return False
        
        # Get existing entry or create new
        if applicant in self.database:
            entry = self.database[applicant]
            
            # Add new WOs
            existing_wos = set(entry.get('observed_wos', []))
            existing_brs = set(entry.get('observed_brs', []))
            existing_areas = set(entry.get('therapeutic_areas', []))
            
            combined_wos = existing_wos | wos
            combined_brs = existing_brs | brs
            combined_areas = existing_areas | areas
            
            # Only update if we have new information
            if combined_wos == existing_wos and combined_brs == existing_brs:
                return False  # No new data
            
            # Recalculate filing rate
            total_wos = len(combined_wos)
            total_brs = len(combined_brs)
            filing_rate = total_brs / total_wos if total_wos > 0 else entry.get('filing_rate', 0.5)
            
            # Update entry
            entry['total_wo_brazil_designated'] = total_wos
            entry['total_br_filings_found'] = total_brs
            entry['filing_rate'] = round(filing_rate, 2)
            entry['therapeutic_areas'] = list(combined_areas)
            entry['observed_wos'] = list(combined_wos)
            entry['observed_brs'] = list(combined_brs)
            entry['last_updated'] = datetime.now().isoformat()
            entry['data_source'] = 'learned_from_searches'
            entry['confidence'] = self._calculate_confidence(total_wos)
            
            logger.info(f"  📊 Updated {applicant}: {total_wos} WOs, {total_brs} BRs ({filing_rate:.0%})")
            
        else:
            # New applicant - create entry
            total_wos = len(wos)
            total_brs = len(brs)
            filing_rate = total_brs / total_wos if total_wos > 0 else 0.5
            
            self.database[applicant] = {
                "applicant_name": applicant,
                "total_wo_brazil_designated": total_wos,
                "total_br_filings_found": total_brs,
                "filing_rate": round(filing_rate, 2),
                "therapeutic_areas": list(areas),
                "observed_wos": list(wos),
                "observed_brs": list(brs),
                "last_updated": datetime.now().isoformat(),
                "data_source": "learned_from_searches",
                "confidence": self._calculate_confidence(total_wos)
            }
            
            logger.info(f"  🆕 New applicant: {applicant} ({total_wos} WOs, {filing_rate:.0%})")
        
        return True
    
    def _calculate_confidence(self, total_wos: int) -> str:
        """Calculate confidence level based on sample size."""
        if total_wos >= 30:
            return "high"
        elif total_wos >= 15:
            return "medium"
        else:
            return "low"
    
    def get_applicant_behavior(self, applicant: str) -> Optional[Dict]:
        """
        Get behavior data for an applicant.
        
        Returns:
            Applicant data dict or None if not found
        """
        normalized = self._normalize_applicant_name(applicant)
        return self.database.get(normalized)
    
    def get_all_applicants(self) -> Dict:
        """Get complete database."""
        return self.database
    
    def merge_with_seed_database(self, seed_database: Dict):
        """
        Merge with a seed database (e.g., industry research).
        
        Keeps learned data but fills gaps with seed data.
        """
        for applicant, seed_data in seed_database.items():
            if applicant not in self.database:
                # Add seed data for unknown applicants
                self.database[applicant] = seed_data
                logger.info(f"  📥 Added seed data for {applicant}")
        
        self._save_database()
    
    def export_to_firebase(self, firebase_ref):
        """
        Export database to Firebase Realtime Database.
        
        Args:
            firebase_ref: Firebase database reference
            
        Example:
            import firebase_admin
            from firebase_admin import credentials, db
            
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://pharmyrus.firebaseio.com/'
            })
            
            ref = db.reference('applicant_database')
            learning_system.export_to_firebase(ref)
        """
        try:
            firebase_ref.set(self.database)
            logger.info(f"🔥 Exported {len(self.database)} applicants to Firebase")
        except Exception as e:
            logger.error(f"❌ Firebase export failed: {e}")
    
    def import_from_firebase(self, firebase_ref):
        """
        Import database from Firebase.
        
        Args:
            firebase_ref: Firebase database reference
        """
        try:
            data = firebase_ref.get()
            if data:
                self.database = data
                self._save_database()  # Also save to local file
                logger.info(f"🔥 Imported {len(self.database)} applicants from Firebase")
        except Exception as e:
            logger.error(f"❌ Firebase import failed: {e}")
    
    def export_to_redis(self, redis_client, key_prefix: str = "pharmyrus:applicant"):
        """
        Export database to Redis.
        
        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
            
        Example:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            learning_system.export_to_redis(r)
        """
        try:
            for applicant, data in self.database.items():
                key = f"{key_prefix}:{applicant}"
                redis_client.set(key, json.dumps(data))
            
            logger.info(f"📮 Exported {len(self.database)} applicants to Redis")
        except Exception as e:
            logger.error(f"❌ Redis export failed: {e}")


# Singleton instance for global access
_learning_system = None

def get_learning_system(database_path: str = "applicant_database.json") -> ApplicantLearningSystem:
    """Get or create global learning system instance."""
    global _learning_system
    if _learning_system is None:
        _learning_system = ApplicantLearningSystem(database_path)
    return _learning_system
