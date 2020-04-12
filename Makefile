all: build-docker-service run-docker-service

build-docker-service:
	python3 -m grpc_tools.protoc -I./src --python_out=./src --grpc_python_out=./src ./src/sedgwick_covid.proto
	docker build -t covid_server -f Dockerfile_server .
	docker build -t covid_client -f Dockerfile_client .

run-docker-service:
	docker network create covid_network
	docker run -d --name covid_server --network covid_network covid_server
	docker run -it --name covid_client --network covid_network covid_client

clean:
	docker stop covid_server covid_client
	docker rm covid_server covid_client
	docker rmi covid_server covid_client
	docker network rm covid_network

start-k8s-service:
	python3 -m grpc_tools.protoc -I./src --python_out=./src --grpc_python_out=./src ./src/sedgwick_covid.proto
	kubectl apply -f covid_service.yml
	export COVID_SERVER=localhost; export COVID_PORT=30001; src/sedgwick_covid_client.py

stop-k8s-service:
	kubectl delete deployments,services -l app=covid-k8s

test-covid:
	python3 -m grpc_tools.protoc -I./src --python_out=./src --grpc_python_out=./src ./src/sedgwick_covid.proto
	src/sedgwick_covid_server.py & echo $$! > COVID_SERVID_PID.pid
	sleep 1
	export COVID_SERVER=localhost; export COVID_PORT=50051; src/sedgwick_covid_client.py
	kill -9 `cat COVID_SERVID_PID.pid` & rm COVID_SERVID_PID.pid

