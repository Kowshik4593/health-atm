# backend/test_all_languages.py
"""
Test script to generate patient reports in ALL Indian languages.
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from app.reporter import generate_patient_report, generate_clinician_report

# All Indian language templates
LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी)",
    "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "bn": "Bengali (বাংলা)",
    "gu": "Gujarati (ગુજરાતી)",
    "mr": "Marathi (मराठी)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
}

def test_all_languages(findings_path: str):
    """Generate reports in all supported languages."""
    
    print("=" * 60)
    print("🌍 HealthATM Phase-2: Multi-Language Report Test")
    print("=" * 60)
    print(f"\n📄 Source: {findings_path}\n")
    
    results = {"success": [], "failed": []}
    
    # Generate clinician report first
    print("📊 Generating Clinician Report (English)...")
    try:
        path = generate_clinician_report(findings_path)
        print(f"   ✅ Clinician: {os.path.basename(path)}")
        results["success"].append(("clinician", path))
    except Exception as e:
        print(f"   ❌ Clinician: {e}")
        results["failed"].append(("clinician", str(e)))
    
    print("\n📋 Generating Patient Reports in All Languages...\n")
    
    # Generate patient reports in all languages
    for lang_code, lang_name in LANGUAGES.items():
        try:
            path = generate_patient_report(findings_path, lang_code)
            size_kb = os.path.getsize(path) / 1024
            print(f"   ✅ {lang_name:<25} → {os.path.basename(path)} ({size_kb:.1f} KB)")
            results["success"].append((lang_code, path))
        except Exception as e:
            print(f"   ❌ {lang_name:<25} → Error: {e}")
            results["failed"].append((lang_code, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"   ✅ Successful: {len(results['success'])}")
    print(f"   ❌ Failed: {len(results['failed'])}")
    
    if results["failed"]:
        print("\n⚠️  Failed languages:")
        for lang, err in results["failed"]:
            print(f"      - {lang}: {err}")
    
    print(f"\n📁 Reports saved to: {Path(findings_path).parent / 'reports'}")
    
    return results


if __name__ == "__main__":
    # Default test file
    default_path = Path(__file__).parent / "app" / "LIDC-IDRI-0001_findings.json"
    
    if len(sys.argv) > 1:
        findings_path = sys.argv[1]
    else:
        findings_path = str(default_path)
    
    if not os.path.exists(findings_path):
        print(f"❌ File not found: {findings_path}")
        sys.exit(1)
    
    test_all_languages(findings_path)
