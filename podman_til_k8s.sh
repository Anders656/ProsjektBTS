#!/bin/sh 

# Rydder opp (ved å drepe og fjerne podden -- om den finnes)
podman pod kill allpodd
podman pod rm   allpodd


########################################################
# Bygger konteinerbilder i Podmans konteinerbildearkiv #
# med kommandoer på følgende form:			   # 
# 							   #
# podman build <katalog> -t <bildenavn>                #
########################################################

podman build pseudonym-db -t pseudonym-db
podman build bidrag-db    -t bidrag-db
podman build app          -t app
podman build web          -t web


##################################################################
# Overfører bilder fra Podman til Kubernetes	             #
# Referanser:						     #
# - https://docs.podman.io/en/latest/markdown/podman-save.1.html #
# - https://microk8s.io/docs/registry-images		     #
##################################################################

podman save  pseudonym-db:latest | microk8s ctr image import -
podman save  bidrag-db:latest    | microk8s ctr image import -
podman save  app:latest          | microk8s ctr image import -
podman save  web:latest          | microk8s ctr image import -


##########################################################
# Lager og redigerer filen allpodd.yaml som brukes til å #
# iverksette systemet i Kubernetes (microk8s) 	     #
##########################################################

# Oppretter Podman-podd
podman  pod create --name allpodd -p 8080:80 -p 8081:81

# Starter konteinere, basert på konternerbildene, i den opprettede
# podden.
podman run -dit --pod=allpodd --restart=always --name app          localhost/app
podman run -dit --pod=allpodd --restart=always --name bidrag-db    localhost/bidrag-db
podman run -dit --pod=allpodd --restart=always --name pseudonym-db localhost/pseudonym-db
podman run -dit --pod=allpodd --restart=always --name web          localhost/web


# Check if allpodd.yaml already exists
if [ -f ./allpodd.yaml ]; then
  echo "File 'allpodd.yaml' already exists. Skipping generation."
else
  echo "Generating 'allpodd.yaml'..."
  podman generate kube allpodd --service -f ./allpodd.yaml

  # Add imagePullPolicy: Never to the generated YAML
  sed -i "/image:/a \    imagePullPolicy: Never" allpodd.yaml
fi

# Rydder opp (ved å drepe og fjerne podden)
podman pod kill allpodd
podman pod rm   allpodd

########################
# Legger til PersistentVolume og PersistentVolumeClaim #
########################

echo "Applying PersistentVolume and PersistentVolumeClaim for bidrag-db..."
microk8s kubectl apply -f /home/kasper/ProsjektBTS/bidrag-pv-pvc.yaml

echo "Applying PersistentVolume and PersistentVolumeClaim for pseudonym-db..."
microk8s kubectl apply -f /home/kasper/ProsjektBTS/pseudonym-pv-pvc.yaml

echo "Checking PersistentVolume and PersistentVolumeClaim status..."
microk8s kubectl get pv
microk8s kubectl get pvc


########################
# Starter opp systemet #
########################

# Stoppper kjørende service og pod -- om de finnes
kubectl delete service/allpodd --grace-period=1
kubectl delete pod/allpodd     --grace-period=1

# Starte podden i en Service i K8S
kubectl create -f allpodd.yaml


####################################################
# Skriver ut info for tilgang på lokal vertsmaskin #
####################################################

echo 
echo
echo "Gjør web (80) og app (81) tilgjengelig på localhost:"
echo 
echo "microk8s kubectl port-forward service/allpodd 8080:80 &"
echo "microk8s kubectl port-forward service/allpodd 8081:81 &"
echo 
echo "For å se i nettleser, gå til http://localhost:8080"
