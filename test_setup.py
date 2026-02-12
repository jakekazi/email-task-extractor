"""
Quick test script to verify the installation and API key setup
"""
import os
from task_extractor import process_email


def test_installation():
    """Test that everything is set up correctly"""
    print("="*60)
    print("Email Task Extractor - Installation Test")
    print("="*60)
    
    # Check Python version
    import sys
    print(f"\n✓ Python version: {sys.version.split()[0]}")
    
    # Check dependencies
    try:
        import anthropic
        print("✓ anthropic library installed")
    except ImportError:
        print("✗ anthropic library not found - run: pip install -r requirements.txt")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv library installed")
    except ImportError:
        print("✗ python-dotenv library not found - run: pip install -r requirements.txt")
        return False
    
    # Check API key
    load_dotenv()
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("\n✗ ANTHROPIC_API_KEY not found in .env file")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to .env file")
        print("3. Get API key from: https://console.anthropic.com/settings/keys")
        return False
    
    if api_key == "your_api_key_here":
        print("\n✗ Please replace 'your_api_key_here' with your actual API key in .env")
        return False
    
    print(f"✓ API key found (starts with: {api_key[:10]}...)")
    
    # Test API call
    print("\n" + "="*60)
    print("Testing API Connection...")
    print("="*60)
    
    test_email = """
    Hi team,
    Please finish the project report by Friday.
    Thanks!
    """
    
    try:
        result = process_email(test_email)
        
        if result['success']:
            print("\n✅ SUCCESS! API connection works.")
            print(f"\nExtracted {len(result['processed_tasks'])} task(s):")
            for i, task in enumerate(result['processed_tasks'], 1):
                conf = task['confidence_metrics']['final_confidence']
                print(f"  {i}. {task['task_description']} (confidence: {conf:.2f})")
            
            print("\n" + "="*60)
            print("✅ All tests passed! You're ready to go.")
            print("="*60)
            print("\nNext steps:")
            print("  • Run 'python main.py' for interactive mode")
            print("  • Or process the sample email: 'python main.py' → option 3 → 'sample_email.txt'")
            return True
        else:
            print(f"\n✗ API call failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error during API test: {e}")
        print("\nThis might be:")
        print("  • Invalid API key")
        print("  • Network connection issue")
        print("  • API service unavailable")
        return False


if __name__ == "__main__":
    success = test_installation()
    exit(0 if success else 1)
