docker build -t stock_trade:latest -f dockerfiles/Dockerfile .
docker run -it --rm -p 8080:5000 stock_trade:latest