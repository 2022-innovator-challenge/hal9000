echo $GH_COM_UPLOAD | podman login ghcr.io -u $GH_COM_USER2 --password-stdin
podman build --arch=amd64 -t=ghcr.io/2022-innovator-challenge/hal9000 .

sleep 1

podman push ghcr.io/2022-innovator-challenge/hal9000:latest

sleep 1

# kubectl apply -f k8s/secrets.yml --kubeconfig=k8s/kubeconfig.yaml
# kubectl apply -f k8s/service.yml --kubeconfig=k8s/kubeconfig.yaml
# kubectl apply -f k8s/api.yml --kubeconfig=k8s/kubeconfig.yaml
kubectl apply -f k8s/deployment.yml --kubeconfig=k8s/kubeconfig.yaml


# podman build --platform=darwin/arm64 -t=ghcr.io/2022-innovator-challenge/hal9000 .
# podman run -e GH_WDF_USER=$GH_WDF_USER -e GH_WDF_TOKEN=$GH_WDF_TOKEN -e GH_TOOLS_USER=$GH_TOOLS_USER -e GH_TOOLS_TOKEN=$GH_TOOLS_TOKEN -e GH_COM_USER=$GH_COM_USER -e GH_COM_TOKEN=$GH_COM_TOKEN -p 3000:3000 hal9000
