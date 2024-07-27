
local:
	docker-compose -f docker-compose.yaml up --build

test:
	docker-compose -f docker-compose.yaml -f docker-compose.test.yaml up --build --abort-on-container-exit
