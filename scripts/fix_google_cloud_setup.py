#!/usr/bin/env python3
"""
Quick Fix Script for Google Cloud Vector Search Issues

This script addresses common setup issues:
1. Missing dependencies
2. Authentication problems
3. API enablement
4. Environment variable configuration
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_gcloud_installed():
    """Check if gcloud CLI is installed"""
    try:
        result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud CLI is installed")
            return True
        else:
            print("❌ Google Cloud CLI is not installed")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud CLI is not installed")
        return False

def check_python_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "google-cloud-aiplatform",
        "google-genai", 
        "google-cloud-storage",
        "google-auth"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_").replace("google_", "google."))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """Install missing Python dependencies"""
    if not missing_packages:
        return True
    
    print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
    
    # Try pip install
    packages_str = " ".join(missing_packages)
    return run_command(f"pip install {packages_str}", "Installing Python dependencies")

def check_env_file():
    """Check and create .env file with required variables"""
    env_file = Path(".env")
    
    required_vars = {
        "GOOGLE_CLOUD_PROJECT": "your-google-cloud-project-id",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "GEMINI_API_KEY": "your-gemini-api-key-here"
    }
    
    if not env_file.exists():
        print("\n📝 Creating .env file template...")
        with open(env_file, "w") as f:
            f.write("# Google Cloud Vector Search Configuration\n")
            for var, default in required_vars.items():
                f.write(f"{var}={default}\n")
        print("✅ .env file created with template values")
        print("⚠️  Please edit .env file with your actual values")
        return False
    else:
        print("\n✅ .env file exists")
        
        # Check if required variables are set
        from dotenv import load_dotenv
        load_dotenv()
        
        missing_vars = []
        for var, default in required_vars.items():
            value = os.getenv(var)
            if not value or value == default:
                missing_vars.append(var)
                print(f"⚠️  {var} is not properly set")
            else:
                print(f"✅ {var} is configured")
        
        if missing_vars:
            print(f"\n⚠️  Please set the following variables in your .env file:")
            for var in missing_vars:
                print(f"   {var}={required_vars[var]}")
            return False
        
        return True

def check_gcloud_auth():
    """Check Google Cloud authentication"""
    print("\n🔐 Checking Google Cloud authentication...")
    
    # Check if authenticated
    result = subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        print(f"✅ Authenticated as: {result.stdout.strip()}")
        
        # Check application default credentials
        try:
            from google.auth import default
            credentials, project = default()
            if project:
                print(f"✅ Application default credentials configured for project: {project}")
                return True
            else:
                print("⚠️  Application default credentials not properly configured")
                return False
        except Exception as e:
            print(f"⚠️  Application default credentials issue: {e}")
            return False
    else:
        print("❌ Not authenticated with Google Cloud")
        return False

def setup_gcloud_auth():
    """Setup Google Cloud authentication"""
    print("\n🔐 Setting up Google Cloud authentication...")
    
    # Login
    if not run_command("gcloud auth login", "Google Cloud login"):
        return False
    
    # Set application default credentials
    if not run_command("gcloud auth application-default login", "Application default credentials setup"):
        return False
    
    return True

def enable_apis():
    """Enable required Google Cloud APIs"""
    apis = [
        "aiplatform.googleapis.com",
        "storage.googleapis.com"
    ]
    
    for api in apis:
        if not run_command(f"gcloud services enable {api}", f"Enabling {api}"):
            print(f"⚠️  Failed to enable {api}. You may need to enable it manually in the Google Cloud Console.")
    
    return True

def main():
    """Main function"""
    print("🔧 Google Cloud Vector Search Setup Fix")
    print("This script will help fix common setup issues.\n")
    
    # Check Google Cloud CLI
    if not check_gcloud_installed():
        print("\n❌ Google Cloud CLI is required. Please install it from:")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    
    # Check Python dependencies
    missing_packages = check_python_dependencies()
    if missing_packages:
        if not install_dependencies(missing_packages):
            print("\n❌ Failed to install dependencies. Please install manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    # Check .env file
    env_configured = check_env_file()
    if not env_configured:
        print("\n⚠️  Please configure your .env file before continuing.")
        return False
    
    # Check authentication
    if not check_gcloud_auth():
        print("\n🔐 Setting up authentication...")
        if not setup_gcloud_auth():
            print("\n❌ Failed to setup authentication. Please run manually:")
            print("   gcloud auth login")
            print("   gcloud auth application-default login")
            return False
    
    # Enable APIs
    enable_apis()
    
    print("\n✅ Setup fix completed!")
    print("\nNext steps:")
    print("1. Verify your .env file has correct values")
    print("2. Run: python scripts/setup_google_vector_search.py")
    print("3. Or run: python scripts/migrate_to_google_vector_search.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)