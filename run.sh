docker build -t stock_trade:latest -f dockerfiles/Dockerfile .
docker run -it --rm --entrypoint bash stock_trade:latest