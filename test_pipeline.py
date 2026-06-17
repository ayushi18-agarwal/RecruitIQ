# test_pipeline.py
"""
Testing script to validate the fixed recruitment ML pipeline
Run this after retraining with the fixed models
"""

import sys
sys.path.insert(0, '.')  # Add current directory to path

from utils import evaluate_candidate, predict_candidate_profile, clean_text
import json

# Test Cases: Real-world scenarios
TEST_CASES = {
    "fashion_designer_for_data_analyst": {
        "resume": """
        Fashion Designer | Portfolio Website Developer
        
        10+ years of experience in fashion design and brand development.
        Led creative team of 5 designers. Managed multiple high-profile projects.
        Excellent communication and problem-solving skills.
        Proficient in Adobe Creative Suite, Figma, and basic HTML/CSS.
        
        Experience:
        - Senior Fashion Designer at Luxury Brand Co (2015-2023)
        - Fashion Consultant for Fortune 500 companies
        - Award-winning design portfolio with 50+ pieces
        """,
        "target_role": "Data Analyst",
        "expected": "Reject",
        "reason": "Fashion designer, not data analyst"
    },
    
    "software_engineer_for_data_analyst": {
        "resume": """
        Software Engineer with 8 years of experience
        
        Expert in Python, Java, C++
        Built data pipelines using Apache Spark and Kafka
        SQL, MongoDB, PostgreSQL databases
        Statistical analysis and data visualization
        Led analytics infrastructure projects
        
        Experience:
        - Senior Software Engineer at Tech Company (2018-2024)
        - Data Engineering at Analytics Firm (2015-2018)
        - Strong background in distributed systems and big data
        """,
        "target_role": "Data Analyst",
        "expected": "Strong Hire",
        "reason": "Relevant technical skills and experience"
    },
    
    "marketing_manager_for_data_analyst": {
        "resume": """
        Marketing Manager with analytics background
        
        5 years in marketing with heavy analytics focus
        Google Analytics, Tableau, Power BI
        A/B testing, conversion optimization
        Familiar with SQL and basic Python for data analysis
        Led marketing data team
        
        Experience:
        - Marketing Manager at E-commerce Company (2019-2024)
        - Data Analyst at Digital Marketing Agency (2017-2019)
        """,
        "target_role": "Data Analyst",
        "expected": "Review",  # Could go either way - some relevant skills
        "reason": "Partial match - analytics skills but primarily marketing"
    },
    
    "short_invalid_resume": {
        "resume": "Hello world",
        "target_role": "Data Analyst",
        "expected": "Reject",
        "reason": "Too short - invalid resume"
    }
}


def run_tests():
    """Run all test cases and report results"""
    
    print("\n" + "="*80)
    print("🧪 RECRUITMENT ML PIPELINE - VALIDATION TESTS")
    print("="*80 + "\n")
    
    results = []
    
    for test_name, test_data in TEST_CASES.items():
        print(f"\n{'─'*80}")
        print(f"TEST: {test_name}")
        print(f"Target Role: {test_data['target_role']}")
        print(f"Reason: {test_data['reason']}")
        print(f"{'─'*80}")
        
        # Run evaluation
        evaluation = evaluate_candidate(
            resume_text=test_data['resume'],
            target_job_role=test_data['target_role']
        )
        
        # Display results
        if evaluation['status'] == 'error':
            print(f"❌ ERROR: {evaluation['message']}")
            results.append({
                'test': test_name,
                'status': 'ERROR',
                'passed': False
            })
            continue
        
        print(f"✓ Predicted Role: {evaluation['predicted_role']}")
        print(f"✓ Fit Score: {evaluation['fit_score']}/100")
        print(f"✓ Model Confidence: {evaluation['confidence']}%")
        print(f"✓ Domain Match: {'Yes' if evaluation['domain_match'] else 'No'}")
        print(f"✓ Valid Candidate: {'Yes' if evaluation['is_valid'] else 'No'}")
        print(f"✓ Recommendation: {evaluation['recommendation']}")
        
        # Check if result matches expected
        matches_expected = evaluation['recommendation'] == test_data['expected']
        status = "✅ PASS" if matches_expected else "❌ FAIL"
        print(f"\n{status} (Expected: {test_data['expected']}, Got: {evaluation['recommendation']})")
        
        results.append({
            'test': test_name,
            'status': 'PASS' if matches_expected else 'FAIL',
            'passed': matches_expected,
            'expected': test_data['expected'],
            'actual': evaluation['recommendation'],
            'confidence': evaluation['confidence'],
            'domain_match': evaluation['domain_match']
        })
    
    # Summary
    print(f"\n\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}\n")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['passed'])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%\n")
    
    if failed_tests > 0:
        print("Failed Tests Details:")
        for r in results:
            if not r['passed']:
                print(f"  ❌ {r['test']}")
                print(f"     Expected: {r['expected']}, Got: {r['actual']}")
                print(f"     Confidence: {r.get('confidence', 'N/A')}%")
                print(f"     Domain Match: {r.get('domain_match', 'N/A')}")
    
    # Recommendations
    print(f"\n{'─'*80}")
    print("💡 RECOMMENDATIONS:")
    print(f"{'─'*80}\n")
    
    if passed_tests == total_tests:
        print("✅ All tests passed! Your model is working correctly.")
        print("   Next steps:")
        print("   1. Deploy to production")
        print("   2. Monitor real-world performance")
        print("   3. Collect feedback on recommendations")
        print("   4. Retrain monthly with new data")
    else:
        print(f"⚠️  {failed_tests} test(s) failed. Recommendations:")
        print("   1. Check training data quality and balance")
        print("   2. Review the evaluation results above")
        print("   3. Consider adjusting confidence thresholds")
        print("   4. Add more diverse training samples for failing categories")
        print("   5. Check if BOM character removed from CSV column names")


def test_text_cleaning():
    """Test the text cleaning function"""
    print(f"\n\n{'='*80}")
    print("🔍 TEXT CLEANING TEST")
    print(f"{'='*80}\n")
    
    test_texts = [
        "Python 3.9 with 10+ years experience",
        "Check: www.example.com | http://test.com",
        "   Multiple    spaces    here   ",
        "Special-chars!@#$%^&*() removed"
    ]
    
    for original in test_texts:
        cleaned = clean_text(original)
        print(f"Original: {original}")
        print(f"Cleaned:  {cleaned}")
        print()


if __name__ == "__main__":
    print("\n🚀 Starting validation tests...\n")
    
    # Test text cleaning
    test_text_cleaning()
    
    # Run main tests
    run_tests()
    
    print("\n✅ Validation complete!\n")
