#!/usr/bin/env python3
"""
File Permission Fixer for cPanel Deployment
Ensures all files have proper permissions for Apache/Passenger
"""

import os
import stat
import sys
from pathlib import Path

def set_file_permissions():
    """Set proper file permissions for cPanel hosting"""
    
    print("🔒 Setting file permissions for cPanel deployment...")
    
    # Get current directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    try:
        # Set directory permissions (755 = rwxr-xr-x)
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if not dir_path.name.startswith('.git'):
                    os.chmod(dir_path, 0o755)
                    print(f"📁 {dir_path}: 755")
        
        # Set file permissions (644 = rw-r--r--)
        for root, dirs, files in os.walk('.'):
            for file_name in files:
                file_path = Path(root) / file_name
                
                # Skip .git files
                if '.git' in str(file_path):
                    continue
                
                # Executable files (755 = rwxr-xr-x)
                if file_name in ['passenger_wsgi.py', 'deploy_cpanel.sh'] or file_name.endswith('.sh'):
                    os.chmod(file_path, 0o755)
                    print(f"🔧 {file_path}: 755")
                
                # Sensitive files (600 = rw-------)
                elif file_name in ['.env', '.env.local', '.env.production']:
                    if file_path.exists():
                        os.chmod(file_path, 0o600)
                        print(f"🔐 {file_path}: 600")
                
                # Regular files (644 = rw-r--r--)
                else:
                    os.chmod(file_path, 0o644)
                    print(f"📄 {file_path}: 644")
        
        # Special handling for specific files
        special_files = {
            'Passengerfile.json': 0o644,
            '.htaccess': 0o644,
            'passenger_wsgi.py': 0o755,
        }
        
        for filename, perm in special_files.items():
            if Path(filename).exists():
                os.chmod(filename, perm)
                print(f"⚙️  {filename}: {oct(perm)}")
        
        print("✅ File permissions set successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting permissions: {e}")
        return False

def validate_permissions():
    """Validate that files have correct permissions"""
    
    print("\n🔍 Validating file permissions...")
    
    issues = []
    
    # Check critical files
    critical_files = {
        'passenger_wsgi.py': 0o755,
        'Passengerfile.json': 0o644,
        '.htaccess': 0o644,
        'main.py': 0o644,
        'requirements.txt': 0o644,
    }
    
    for filename, expected_perm in critical_files.items():
        if Path(filename).exists():
            current_perm = stat.S_IMODE(os.stat(filename).st_mode)
            if current_perm == expected_perm:
                print(f"✅ {filename}: {oct(current_perm)}")
            else:
                issues.append(f"❌ {filename}: {oct(current_perm)} (expected {oct(expected_perm)})")
        else:
            issues.append(f"⚠️  {filename}: File not found")
    
    if issues:
        print("\n⚠️  Permission Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("✅ All file permissions are correct!")
        return True

if __name__ == "__main__":
    print("🚀 cPanel Permission Fixer")
    print("=" * 30)
    
    success = set_file_permissions()
    
    if success:
        validate_permissions()
        print("\n🎉 Permission setup completed!")
        print("\n📋 Next steps:")
        print("1. Upload files to cPanel")
        print("2. Run: chmod +x deploy_cpanel.sh && ./deploy_cpanel.sh")
        print("3. Configure Python app in cPanel")
    else:
        print("\n❌ Permission setup failed!")
        sys.exit(1)