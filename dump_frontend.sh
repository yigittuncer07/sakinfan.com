{
  find . \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "seeder.py" \) \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/venv/*" | while read -r file; do
    
    clean_path="${file#./}"
    
    echo "=== $PWD/$clean_path ==="
    cat "$file"
    echo -e "\n"
  done
} > all_frontend.txt