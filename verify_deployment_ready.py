#!/usr/bin/env python3
"""
Verify that AI Brand Studio is deployment-ready.

This script checks all deployment prerequisites and configuration files.
"""

import os
import sys
import json
from pathlib import Path

def check_file(path, description):
    """Check if a file exists."""
    if Path(path).exists():
        print(f"  ✅ {description}: {path}")
        return True
    else:
        print(f"  ❌ {description} missing: {path}")
        return False

def check_directory(path, description):
    """Check if a directory exists."""
    if Path(path).is_dir():
        print(f"  ✅ {description}: {path}/")
        return True
    else:
        print(f"  ❌ {description} missing: {path}/")
        return False

def check_agent_structure():
    """Verify brand_studio_agent directory structure."""
    print("\n" + "=" * 60)
    print("1. Checking Agent Directory Structure")
    print("=" * 60)

    checks = []
    checks.append(check_directory("brand_studio_agent", "Agent directory"))
    checks.append(check_file("brand_studio_agent/agent.py", "Agent entry point"))
    checks.append(check_file("brand_studio_agent/.agent_engine_config.json", "Agent Engine config"))
    checks.append(check_file("brand_studio_agent/requirements.txt", "Requirements"))
    checks.append(check_file("brand_studio_agent/.env", "Environment config"))

    return all(checks)

def check_source_code():
    """Verify source code structure."""
    print("\n" + "=" * 60)
    print("2. Checking Source Code")
    print("=" * 60)

    checks = []
    checks.append(check_directory("src/agents", "Agents directory"))
    checks.append(check_file("src/agents/orchestrator.py", "Orchestrator"))
    checks.append(check_file("src/agents/research_agent.py", "Research Agent"))
    checks.append(check_file("src/agents/name_generator.py", "Name Generator"))
    checks.append(check_file("src/agents/validation_agent.py", "Validation Agent"))
    checks.append(check_file("src/agents/seo_agent.py", "SEO Agent"))
    checks.append(check_file("src/agents/story_agent.py", "Story Agent"))

    checks.append(check_directory("src/tools", "Tools directory"))
    checks.append(check_file("src/tools/domain_checker.py", "Domain Checker"))
    checks.append(check_file("src/tools/trademark_checker.py", "Trademark Checker"))

    return all(checks)

def check_config_files():
    """Verify configuration files."""
    print("\n" + "=" * 60)
    print("3. Checking Configuration Files")
    print("=" * 60)

    checks = []
    checks.append(check_file(".env", "Root environment file"))
    checks.append(check_file(".agent_engine_config.json", "Root agent config"))

    # Validate JSON configs
    try:
        with open(".agent_engine_config.json") as f:
            config = json.load(f)
            print(f"  ✅ Agent Engine config valid JSON")
            print(f"     - Min instances: {config['resource_settings']['min_instances']}")
            print(f"     - Max instances: {config['resource_settings']['max_instances']}")
            print(f"     - CPU: {config['resource_settings']['cpu']}")
            print(f"     - Memory: {config['resource_settings']['memory']}")
    except Exception as e:
        print(f"  ❌ Agent Engine config invalid: {e}")
        checks.append(False)

    return all(checks)

def check_documentation():
    """Verify documentation files."""
    print("\n" + "=" * 60)
    print("4. Checking Documentation")
    print("=" * 60)

    checks = []
    checks.append(check_file("README.md", "README"))
    checks.append(check_file("CLAUDE.md", "Architecture guide"))
    checks.append(check_file("TESTING.md", "Testing guide"))
    checks.append(check_file("DEPLOYMENT.md", "Deployment guide"))

    return all(checks)

def check_tests():
    """Verify test files."""
    print("\n" + "=" * 60)
    print("5. Checking Test Suite")
    print("=" * 60)

    checks = []
    checks.append(check_directory("tests", "Tests directory"))
    checks.append(check_file("tests/integration.evalset.json", "Evaluation test set"))
    checks.append(check_file("tests/eval_config.json", "Evaluation config"))

    # Count test cases
    try:
        with open("tests/integration.evalset.json") as f:
            evalset = json.load(f)
            num_tests = len(evalset.get("test_cases", []))
            print(f"  ✅ {num_tests} evaluation test cases configured")
    except Exception as e:
        print(f"  ❌ Could not read evalset: {e}")
        checks.append(False)

    return all(checks)

def check_environment():
    """Verify environment configuration."""
    print("\n" + "=" * 60)
    print("6. Checking Environment Variables")
    print("=" * 60)

    from dotenv import load_dotenv
    load_dotenv()

    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = os.getenv('GOOGLE_CLOUD_LOCATION')
    use_vertexai = os.getenv('GOOGLE_GENAI_USE_VERTEXAI')

    if project_id:
        print(f"  ✅ GOOGLE_CLOUD_PROJECT: {project_id}")
    else:
        print(f"  ❌ GOOGLE_CLOUD_PROJECT not set")
        return False

    if location:
        print(f"  ✅ GOOGLE_CLOUD_LOCATION: {location}")
    else:
        print(f"  ⚠️  GOOGLE_CLOUD_LOCATION not set (will use default)")

    if use_vertexai == "1":
        print(f"  ✅ GOOGLE_GENAI_USE_VERTEXAI: {use_vertexai}")
    else:
        print(f"  ⚠️  GOOGLE_GENAI_USE_VERTEXAI: {use_vertexai} (should be 1 for Vertex AI)")

    return True

def check_dependencies():
    """Verify Python dependencies."""
    print("\n" + "=" * 60)
    print("7. Checking Python Dependencies")
    print("=" * 60)

    try:
        import google.adk
        print(f"  ✅ google-adk installed (version: {getattr(google.adk, '__version__', 'unknown')})")
    except ImportError:
        print(f"  ❌ google-adk not installed")
        return False

    try:
        import google.genai
        print(f"  ✅ google-genai installed")
    except ImportError:
        print(f"  ❌ google-genai not installed")
        return False

    try:
        import whois
        print(f"  ✅ python-whois installed")
    except ImportError:
        print(f"  ❌ python-whois not installed")
        return False

    return True

def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("AI BRAND STUDIO - DEPLOYMENT READINESS VERIFICATION")
    print("=" * 60)

    results = []

    results.append(("Agent Structure", check_agent_structure()))
    results.append(("Source Code", check_source_code()))
    results.append(("Configuration", check_config_files()))
    results.append(("Documentation", check_documentation()))
    results.append(("Test Suite", check_tests()))
    results.append(("Environment", check_environment()))
    results.append(("Dependencies", check_dependencies()))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(result[1] for result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - DEPLOYMENT READY")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Deploy using: cd brand_studio_agent && adk deploy agent_engine ...")
        print("2. See DEPLOYMENT.md for detailed instructions")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - RESOLVE ISSUES BEFORE DEPLOYMENT")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
