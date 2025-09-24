# Quick cPanel PostgreSQL Driver Fix

## The Problem
If you get `pg_config executable not found` error on cPanel, here's the quick fix:

## Solution

### Option 1: Use the main requirements.txt (Updated)
```bash
pip install -r requirements.txt
```
✅ **This now uses `asyncpg` instead of `psycopg2-binary`**

### Option 2: Use the automated installer
```bash
chmod +x install_deps.sh
./install_deps.sh
```

### Option 3: Manual driver installation
If both above fail, install drivers manually:

```bash
# Try these in order:
pip install asyncpg==0.29.0
pip install pg8000==1.30.3
pip install psycopg2-binary==2.9.8  # This might fail
```

## What Changed
- Main `requirements.txt` now uses `asyncpg` (works on most hosting)
- `install_deps.sh` tries `requirements.txt` first
- Multiple fallback options available

## Database Code
Your `database.py` automatically detects available drivers:
- Will use `psycopg2` if available (local development)  
- Will use `asyncpg` if `psycopg2` fails (cPanel hosting)
- Will use `pg8000` as last resort

**No code changes needed!** The multi-driver system handles everything automatically.