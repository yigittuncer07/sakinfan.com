{
  echo "=== $PWD/docker-compose.yml ==="
  cat docker-compose.yml
  echo -e "\n"
  
  echo "=== $PWD/requirements.txt ==="
  cat requirements.txt
  echo -e "\n"

  if [ -f ".env.example" ]; then
    echo "=== $PWD/.env.example ==="
    cat .env.example
    echo -e "\n"
  fi

  if [ -f "Dockerfile" ]; then
    echo "=== $PWD/Dockerfile ==="
    cat Dockerfile
    echo -e "\n"
  fi

  if [ -f "nginx.conf" ]; then
    echo "=== $PWD/nginx.conf ==="
    cat nginx.conf
    echo -e "\n"
  fi
  
  find app \( -name "*.py" -o -name "*.html" \) -not -path "*/__pycache__*" | while read -r file; do
    echo "=== $PWD/$file ==="
    cat "$file"
    echo -e "\n"
  done
} > all_code.txt