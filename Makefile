drestart: dstop dstart

dstart:
	echo "Starting docker-compose deattahced"
	docker-compose --env-file .custom_env_file up -d

dstop:
	echo "Stopping docker-compose"
	docker-compose down

dclear:
	echo "Prune docker system"
	docker system prune -f