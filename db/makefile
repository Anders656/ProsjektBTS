all: web app bidrag-db pseudonym-db K8s

K8s: *-*.yaml 

# Konverterer fra compose-fil til kubernetes-filer
*-*.yaml: compose.yaml

	env -i -C ${PWD} PATH=/usr/bin:/bin                                      \
	docker build -t kompose https://github.com/kubernetes/kompose.git\#main; \
	env -i -C ${PWD} PATH=/usr/bin:/bin                                      \
	docker run --rm -t -v ${PWD}:/opt kompose sh -c "cd /opt && kompose convert"

# Bygger bildet for web på nytt og \"ruller det ut\"
web: web/Dockerfile web/index.html web-deployment.yaml web-service.yaml

	docker build web/ -t v3_web             # bygger bildet på nytt
	kubectl rollout restart deployment web  # starter en "pending" pod med nybygd bilde 	
	kubectl delete -f "web-*yaml" --now
	kubectl apply  -f "web-*yaml"

# Bygger bildet for app, bidrag-db og/eller pseudonym på nytt og \"ruller det ut\"
%: %/Dockerfile %/index.cgi %-deployment.yaml %-service.yaml

	docker build $@/ -t v3_$@             # bygger bildet på nytt
	kubectl rollout restart deployment $@ # starter en "pending" pod med nybygd bilde 	
	kubectl delete -f "$@-*yaml" --now
	kubectl apply  -f "$@-*yaml"
