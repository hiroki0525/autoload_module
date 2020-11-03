echo "Docker Build"
docker build --no-cache -t autoload-module-test  .
echo "Docker Run"
docker run -it autoload-module-test