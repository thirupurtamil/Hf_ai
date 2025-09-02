"""
Setup script for Mobile AI Django project
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_system_dependencies():
    """Check system dependencies"""
    system = platform.system().lower()

    if system == 'linux':
        # Check for Ubuntu/Debian packages
        packages = ['python3-dev', 'python3-pip', 'redis-server', 'git']
        for package in packages:
            if not run_command(f"dpkg -l | grep -q {package}"):
                print(f"⚠️  Consider installing: sudo apt install {package}")

    elif system == 'darwin':  # macOS
        print("ℹ️  On macOS, consider using Homebrew for Redis: brew install redis")

    elif system == 'windows':
        print("ℹ️  On Windows, consider using Windows Subsystem for Linux (WSL)")

    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists('venv'):
        if not run_command('python -m venv venv'):
            return False

    # Activation command varies by system
    system = platform.system().lower()
    if system == 'windows':
        activate_cmd = 'venv\\Scripts\\activate'
    else:
        activate_cmd = 'source venv/bin/activate'

    print(f"ℹ️  Activate virtual environment: {activate_cmd}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    pip_cmd = 'venv/bin/pip' if platform.system().lower() != 'windows' else 'venv\\Scripts\\pip'

    commands = [
        f'{pip_cmd} install --upgrade pip',
        f'{pip_cmd} install -r requirements.txt'
    ]

    for cmd in commands:
        if not run_command(cmd):
            return False

    return True

def setup_database():
    """Setup database"""
    python_cmd = 'venv/bin/python' if platform.system().lower() != 'windows' else 'venv\\Scripts\\python'

    commands = [
        f'{python_cmd} manage.py makemigrations',
        f'{python_cmd} manage.py migrate',
    ]

    for cmd in commands:
        if not run_command(cmd):
            return False

    return True

def create_superuser():
    """Create Django superuser"""
    python_cmd = 'venv/bin/python' if platform.system().lower() != 'windows' else 'venv\\Scripts\\python'

    print("\n📝 Creating Django superuser...")
    print("You'll be prompted to enter username, email, and password.")

    try:
        subprocess.run([python_cmd, 'manage.py', 'createsuperuser'], check=True)
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Superuser creation skipped or failed")
        return False

def setup_static_files():
    """Collect static files"""
    python_cmd = 'venv/bin/python' if platform.system().lower() != 'windows' else 'venv\\Scripts\\python'
    return run_command(f'{python_cmd} manage.py collectstatic --noinput')

def check_redis():
    """Check if Redis is running"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except:
        print("⚠️  Redis is not running. Please start Redis server:")
        system = platform.system().lower()
        if system == 'linux':
            print("   sudo systemctl start redis-server")
        elif system == 'darwin':
            print("   brew services start redis")
        else:
            print("   Start Redis according to your system documentation")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Mobile AI Django Project\n")

    # Check prerequisites
    if not check_python_version():
        return False

    check_system_dependencies()

    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to setup virtual environment")
        return False

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False

    # Setup environment file
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        with open('.env.example', 'r') as src, open('.env', 'w') as dst:
            dst.write(src.read())
        print("⚠️  Please edit .env file with your configuration")

    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        return False

    # Setup static files
    if not setup_static_files():
        print("❌ Failed to setup static files")
        return False

    # Check Redis (optional for basic functionality)
    check_redis()

    # Create superuser (optional)
    create_superuser()

    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys and configuration")
    print("2. Start Redis server if not running")
    print("3. Run the development server:")

    python_cmd = 'venv/bin/python' if platform.system().lower() != 'windows' else 'venv\\Scripts\\python'
    print(f"   {python_cmd} manage.py runserver")

    print("\n4. In another terminal, start Celery worker:")
    celery_cmd = 'venv/bin/celery' if platform.system().lower() != 'windows' else 'venv\\Scripts\\celery'
    print(f"   {celery_cmd} -A mobile_ai_django worker --loglevel=info")

    print("\n5. In another terminal, start Celery Beat:")
    print(f"   {celery_cmd} -A mobile_ai_django beat --loglevel=info")

    print("\n6. Access the application:")
    print("   - Web interface: http://127.0.0.1:8000/")
    print("   - Admin interface: http://127.0.0.1:8000/admin/")
    print("   - API documentation: http://127.0.0.1:8000/api/")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
