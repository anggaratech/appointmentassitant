run:
	uvicorn main:app --reload --log-level debug --timeout-keep-alive 30
build:
	docker build -t chatbot-palm .
serve:
	docker run -d -p 8000:8000 --name chatbot-palm chatbot-palm
stop:
	docker stop chatbot-palm && docker rm chatbot-palm
logs:
	docker logs -f chatbot-palm
shell:
	docker exec -it chatbot-palm bash