#!/bin/bash
# Deployment verification script for Streamlit Cloud

echo "=========================================="
echo "DSAL Streamlit Cloud Deployment Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check git status
echo "1. Checking Git status..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Git repository initialized${NC}"
    
    # Check if remote is configured
    if git remote get-url origin > /dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        echo -e "${GREEN}✅ Remote configured: ${REMOTE_URL}${NC}"
    else
        echo -e "${RED}❌ No remote configured${NC}"
    fi
    
    # Check if there are uncommitted changes
    if [ -z "$(git status --porcelain)" ]; then
        echo -e "${GREEN}✅ No uncommitted changes${NC}"
    else
        echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
        git status --short
    fi
    
    # Check last commit
    LAST_COMMIT=$(git log -1 --oneline 2>/dev/null)
    if [ -n "$LAST_COMMIT" ]; then
        echo -e "${GREEN}✅ Last commit: ${LAST_COMMIT}${NC}"
    fi
else
    echo -e "${RED}❌ Not a git repository${NC}"
fi

echo ""
echo "2. Checking required files..."

REQUIRED_FILES=(
    "requirements.txt"
    "app/main.py"
    ".streamlit/config.toml"
    "core/preprocessor.py"
    "core/dynamics.py"
    "core/features.py"
    "core/visualizer.py"
    "utils/helpers.py"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file - MISSING${NC}"
        ALL_FILES_EXIST=false
    fi
done

echo ""
echo "3. Checking Python dependencies..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment found${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment not found (not required for Streamlit Cloud)${NC}"
fi

# Check if requirements.txt exists and has content
if [ -f "requirements.txt" ] && [ -s "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt exists and has content${NC}"
    echo "   Dependencies listed:"
    grep -v "^#" requirements.txt | grep -v "^$" | sed 's/^/   - /'
else
    echo -e "${RED}❌ requirements.txt missing or empty${NC}"
fi

echo ""
echo "4. Checking app structure..."

if [ -f "app/main.py" ]; then
    echo -e "${GREEN}✅ app/main.py exists${NC}"
    
    # Check if it's a valid Python file
    if python3 -m py_compile app/main.py 2>/dev/null; then
        echo -e "${GREEN}✅ app/main.py syntax is valid${NC}"
    else
        echo -e "${RED}❌ app/main.py has syntax errors${NC}"
    fi
else
    echo -e "${RED}❌ app/main.py missing${NC}"
fi

# Check pages directory
if [ -d "app/pages" ]; then
    PAGE_COUNT=$(find app/pages -name "*.py" | wc -l)
    echo -e "${GREEN}✅ app/pages/ directory exists (${PAGE_COUNT} page(s))${NC}"
else
    echo -e "${YELLOW}⚠️  app/pages/ directory not found (optional)${NC}"
fi

echo ""
echo "5. Running Python tests..."

if command -v python3 &> /dev/null; then
    if python3 test_app_locally.py 2>&1 | tail -10; then
        echo ""
        echo -e "${GREEN}✅ Python tests passed${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠️  Some Python tests may have issues${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Python3 not found, skipping tests${NC}"
fi

echo ""
echo "=========================================="
echo "Deployment Checklist"
echo "=========================================="
echo ""
echo "Before deploying to Streamlit Cloud:"
echo ""
echo "  [ ] Code pushed to GitHub"
echo "  [ ] All required files present"
echo "  [ ] requirements.txt is up to date"
echo "  [ ] app/main.py is the correct entry point"
echo "  [ ] .gitignore excludes large files (CSV, WAV)"
echo ""
echo "Deployment steps:"
echo ""
echo "  1. Visit https://share.streamlit.io/"
echo "  2. Sign in with GitHub"
echo "  3. Click 'New app'"
echo "  4. Repository: jingzeyang9527-sudo/continuous-speaking-rate"
echo "  5. Branch: main"
echo "  6. Main file: app/main.py"
echo "  7. Click 'Deploy'"
echo ""
echo "After deployment:"
echo ""
echo "  [ ] App URL is accessible"
echo "  [ ] Main page loads correctly"
echo "  [ ] Data Browser page works"
echo "  [ ] File upload works"
echo "  [ ] Analysis functions work"
echo ""
