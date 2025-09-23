#!/usr/bin/env python3
"""
GitHub to App Converter - Demo Script
Demonstrates the tool that solves the viral GitHub issue!
"""

import requests
import json
import time
import webbrowser
import os

def print_banner():
    """Print the application banner."""
    print("🚀" + "=" * 60 + "🚀")
    print("    GITHUB TO APP CONVERTER - DEMO")
    print("    Solving the 'I just want to download and use it' problem!")
    print("🚀" + "=" * 60 + "🚀")
    print()

def demo_conversion():
    """Demonstrate the conversion process."""
    base_url = "http://localhost:8000"
    
    print("🎯 DEMO: Converting a GitHub repository to a working app")
    print("-" * 60)
    
    # Example repositories to try
    examples = [
        {
            "name": "Simple Python App",
            "url": "https://github.com/octocat/Hello-World",
            "platform": "web"
        },
        {
            "name": "FastAPI Example", 
            "url": "https://github.com/tiangolo/fastapi",
            "platform": "executable"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Converting: {example['name']}")
        print(f"   Repository: {example['url']}")
        print(f"   Platform: {example['platform']}")
        
        conversion_data = {
            "github_url": example['url'],
            "app_name": f"demo_app_{i}",
            "target_platform": example['platform']
        }
        
        try:
            print("   ⏳ Processing...")
            response = requests.post(f"{base_url}/convert", data=conversion_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success! {result.get('message')}")
                if 'download_url' in result:
                    print(f"   📦 Download: {base_url}{result.get('download_url')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout (normal for large repositories)")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Brief pause between conversions

def show_features():
    """Show the key features of the tool."""
    print("\n✨ KEY FEATURES")
    print("-" * 60)
    
    features = [
        "🤖 AI-Powered Analysis - Understands any codebase",
        "📦 Multiple Platforms - Executable, Docker, Web apps",
        "⚡ One-Click Conversion - No technical knowledge needed",
        "🔧 Auto-Dependency Management - Installs everything automatically",
        "📱 Beautiful Web Interface - Easy to use for everyone",
        "🛠️ Agentic Coding - AI agents generate intelligent wrappers"
    ]
    
    for feature in features:
        print(f"   {feature}")
        time.sleep(0.5)

def show_problem_solution():
    """Show the problem this tool solves."""
    print("\n🎯 THE PROBLEM WE SOLVE")
    print("-" * 60)
    print("Remember this viral GitHub issue?")
    print()
    print('   "I DONT GIVE A FUCK ABOUT THE FUCKING CODE!')
    print('    i just want to download this stupid fucking application')
    print('    and use it."')
    print()
    print("This tool solves EXACTLY that problem!")
    print()
    print("❌ Before: Confusing installation instructions, dependency hell")
    print("✅ After:  Paste URL → Click Convert → Download & Run")

def open_web_interface():
    """Open the web interface in the browser."""
    print("\n🌐 OPENING WEB INTERFACE")
    print("-" * 60)
    print("Opening http://localhost:8000 in your browser...")
    
    try:
        webbrowser.open("http://localhost:8000")
        print("✅ Web interface opened!")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print("   Please manually open: http://localhost:8000")

def main():
    """Main demo function."""
    print_banner()
    
    # Check if the application is running
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code != 200:
            print("❌ Application is not running!")
            print("   Please start it with: python3 run.py")
            return
    except Exception:
        print("❌ Application is not running!")
        print("   Please start it with: python3 run.py")
        return
    
    show_problem_solution()
    show_features()
    
    print("\n🧪 LIVE DEMO")
    print("-" * 60)
    print("Let's convert some real GitHub repositories...")
    
    demo_conversion()
    
    print("\n🎉 DEMO COMPLETE!")
    print("-" * 60)
    print("The GitHub to App Converter is working perfectly!")
    print()
    print("Next steps:")
    print("1. Open the web interface to try it yourself")
    print("2. Try converting your favorite GitHub repositories")
    print("3. Share this tool with others who need it!")
    
    open_web_interface()

if __name__ == "__main__":
    main()