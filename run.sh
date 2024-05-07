gunicorn app.app:server &
echo $! > gunicorn.pid

python pourCommunicationsToDB.py &
echo $! > pourCommunicationsToDB.pid

containerName=$(jq -r '.redis.container_name' config.json)
redisPassword=$(jq -r '.redis.password' config.json)
redisPort=$(jq -r '.redis.port' config.json)
redisVersion=$(jq -r '.redis.version' config.json)
docker run -p $redisPort:$redisPort \
           -v $PWD/redis_data/:/data \
           --name $containerName \
           -d redis:$redisVersion redis-server \
           --appendonly yes \
           --requirepass "$redisPassword"