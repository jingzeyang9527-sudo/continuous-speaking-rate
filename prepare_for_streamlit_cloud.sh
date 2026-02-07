#!/bin/bash
# Script to prepare repository for Streamlit Cloud deployment

echo "=== Preparing DSAL for Streamlit Cloud ==="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "⚠️  Git not initialized. Initializing..."
    git init
    echo "✅ Git initialized"
fi

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "⚠️  .gitignore not found. Creating..."
    # .gitignore should already exist, but just in case
    echo "✅ .gitignore checked"
fi

# Check requirements.txt
if [ ! -f requirements.txt ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi
echo "✅ requirements.txt found"

# Check app/main.py
if [ ! -f app/main.py ]; then
    echo "❌ Error: app/main.py not found!"
    exit 1
fi
echo "✅ app/main.py found"

# Check .streamlit/config.toml
if [ ! -f .streamlit/config.toml ]; then
    echo "⚠️  .streamlit/config.toml not found. Creating default..."
    mkdir -p .streamlit
    cat > .streamlit/config.toml << EOF
[server]
headless = true
port = 8501

[theme]
primaryColor = "#1f77b4"
EOF
    echo "✅ Created .streamlit/config.toml"
else
    echo "✅ .streamlit/config.toml found"
fi

echo ""
echo "=== Repository Status ==="
git status --short | head -20

echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Review changes:"
echo "   git status"
echo ""
echo "2. Add files:"
echo "   git add ."
echo ""
echo "3. Commit:"
echo "   git commit -m 'Prepare for Streamlit Cloud deployment'"
echo ""
echo "4. Push to GitHub (if remote exists):"
echo "   git remote -v  # Check if remote exists"
echo "   git push origin main"
echo ""
echo "5. Deploy on Streamlit Cloud:"
echo "   - Visit https://share.streamlit.io/"
echo "   - Sign in with GitHub"
echo "   - Click 'New app'"
echo "   - Select your repository"
echo "   - Main file: app/main.py"
echo "   - Click 'Deploy'"
echo ""
echo "✅ Preparation complete!"
