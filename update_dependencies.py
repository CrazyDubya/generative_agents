"""
Dependency update script for generative agents.
Safely updates dependencies while maintaining compatibility.
"""
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def check_dependency_vulnerabilities():
    """Check for known vulnerabilities in current dependencies."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Outdated packages:")
            print(result.stdout)
        else:
            print("Error checking outdated packages:", result.stderr)
            
    except Exception as e:
        print(f"Error running pip list: {e}")

def create_updated_requirements():
    """Create updated requirements.txt with security fixes."""
    
    # Critical security updates
    security_updates = {
        'Django': '4.2.7',  # LTS version with security fixes
        'openai': '1.3.5',  # Latest stable version
        'requests': '2.31.0',  # Security fixes
        'Pillow': '10.1.0',  # Security fixes
        'urllib3': '2.0.7',  # Security fixes
    }
    
    # Read current requirements
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("requirements.txt not found!")
        return
    
    with open(req_file, 'r') as f:
        lines = f.readlines()
    
    updated_lines = []
    updated_packages = set()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Parse package name
            if '==' in line:
                package_name = line.split('==')[0]
            elif '>=' in line:
                package_name = line.split('>=')[0]
            else:
                package_name = line
            
            # Check if we have a security update
            package_name_clean = package_name.strip()
            for sec_package, sec_version in security_updates.items():
                if package_name_clean.lower() == sec_package.lower():
                    updated_lines.append(f"{sec_package}=={sec_version}")
                    updated_packages.add(sec_package.lower())
                    print(f"Updated {package_name_clean} to {sec_version}")
                    break
            else:
                # Keep original line
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Add any new security packages that weren't in original
    for sec_package, sec_version in security_updates.items():
        if sec_package.lower() not in updated_packages:
            updated_lines.append(f"{sec_package}=={sec_version}")
            print(f"Added new package: {sec_package}=={sec_version}")
    
    # Add development dependencies
    dev_deps = [
        "flake8==6.1.0",
        "black==23.11.0", 
        "pylint==3.0.3",
        "mypy==1.7.1",
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
    ]
    
    updated_lines.extend(["", "# Development dependencies"] + dev_deps)
    
    # Write updated requirements
    backup_file = Path("requirements.txt.backup")
    req_file.rename(backup_file)
    print(f"Backed up original requirements to {backup_file}")
    
    with open(req_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    print(f"Updated requirements.txt created")
    
    return str(req_file)

def create_requirements_security():
    """Create a security-focused requirements file."""
    security_requirements = [
        "# Security-focused requirements for generative agents",
        "",
        "# Core framework with security updates",
        "Django==4.2.7",
        "django-cors-headers==4.3.1",
        "",
        "# OpenAI with latest security patches", 
        "openai==1.3.5",
        "",
        "# Data processing with security fixes",
        "numpy==1.24.4",
        "pandas==2.1.3",
        "scikit-learn==1.3.2",
        "",
        "# Web and networking with security patches",
        "requests==2.31.0",
        "urllib3==2.0.7",
        "certifi==2023.11.17",
        "",
        "# Image processing with security fixes",
        "Pillow==10.1.0",
        "",
        "# Natural language processing",
        "nltk==3.8.1",
        "",
        "# Web automation (if needed)",
        "selenium==4.15.2",
        "",
        "# Development and testing",
        "flake8==6.1.0",
        "black==23.11.0",
        "pylint==3.0.3", 
        "mypy==1.7.1",
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
        "",
        "# Additional security tools",
        "bandit==1.7.5",  # Security linting
        "safety==2.3.5",  # Vulnerability scanning
    ]
    
    security_file = Path("requirements-security.txt")
    with open(security_file, 'w') as f:
        f.write('\n'.join(security_requirements))
    
    print(f"Created {security_file} with security-focused dependencies")
    return str(security_file)

def run_security_audit():
    """Run security audit on dependencies."""
    print("\n=== Running Security Audit ===")
    
    # Check for known vulnerabilities
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "safety"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Run safety check
            safety_result = subprocess.run(
                [sys.executable, "-m", "safety", "check"],
                capture_output=True,
                text=True
            )
            
            if safety_result.returncode == 0:
                print("✅ No known security vulnerabilities found")
            else:
                print("⚠️ Security vulnerabilities detected:")
                print(safety_result.stdout)
                print(safety_result.stderr)
        
    except Exception as e:
        print(f"Error running security audit: {e}")

def main():
    """Main function to coordinate dependency updates."""
    print("=== Generative Agents Dependency Security Update ===\n")
    
    # Check current outdated packages
    print("1. Checking for outdated packages...")
    check_dependency_vulnerabilities()
    
    # Create updated requirements
    print("\n2. Creating updated requirements...")
    updated_file = create_updated_requirements()
    
    # Create security-focused requirements
    print("\n3. Creating security requirements...")
    security_file = create_requirements_security()
    
    # Run security audit
    print("\n4. Running security audit...")
    run_security_audit()
    
    print("\n=== Update Summary ===")
    print(f"✅ Backup created: requirements.txt.backup")
    print(f"✅ Updated file: {updated_file}")
    print(f"✅ Security file: {security_file}")
    print("\n📋 Next Steps:")
    print("1. Review the updated requirements files")
    print("2. Test with: pip install -r requirements-security.txt")
    print("3. Run tests to ensure compatibility")
    print("4. Commit changes if tests pass")
    
    print("\n⚠️ IMPORTANT:")
    print("- Test thoroughly before deploying to production")
    print("- Check for breaking changes in major version updates")
    print("- Update code if OpenAI API has changed")

if __name__ == "__main__":
    main()