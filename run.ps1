docker build -t stock_trade:latest -f dockerfiles/Dockerfile .
docker run -dit --rm -p 5001:5000 stock_trade:latest