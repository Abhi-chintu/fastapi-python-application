# fastapi-python-application
Python application deployment project

## Prerequisite
1. Install eks cluster
2. Install docker and docker-compose
3. Install Kubectl
4. Install helm
   
## Steps:

**Clone repo**

    git clone https://github.com/Abhi-chintu/fastapi-python-application.git

**Run application with docker-compose**

    cd fastapi-python-application
    docker-compose up -d --buildx

**To remove container**

    docker-compose down

## To Deploy application with K8s (EKS cluster)

**Create secret for postgres**

    read -s -p "PostgreSQL password: " DB_PASSWORD; echo

    kubectl create secret generic postgres-auth \
      --namespace product-app \
      --from-literal=POSTGRES_USER=appuser \
      --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
      --from-literal=POSTGRES_DB=products \
      --dry-run=client -o yaml | kubectl apply -f -

**Create storage class**

      kubectl apply -f - <<'EOF'
      apiVersion: storage.k8s.io/v1
      kind: StorageClass
      metadata:
        name: ebs-csi-gp3
      provisioner: ebs.csi.aws.com
      volumeBindingMode: WaitForFirstConsumer
      allowVolumeExpansion: true
      parameters:
        type: gp3
        fsType: ext4
      EOF


**Goto EKS dashboard and add EBS-CSI-driver addon**

    eksctl create iamserviceaccount \
    --cluster eksdemo \
    --region ap-south-1 \
    --namespace kube-system \
    --name ebs-csi-controller-sa \
    --role-name AmazonEKS_EBS_CSI_DriverRole \
    --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
    --approve \
    --role-only

**Update addon**

    aws eks update-addon \
    --cluster-name eksdemo \
    --addon-name aws-ebs-csi-driver \
    --region ap-south-1 \
    --service-account-role-arn arn:aws:iam::637423245256:role/AmazonEKS_EBS_CSI_DriverRole \
    --resolve-conflicts PRESERVE

**Deploy database and application using helm commands**

    helm upgrade --install postgres ./k8s/postgres   --namespace demo
    helm upgrade --install application ./k8s/application  --namespace demo

**Since we have give svc as load balancer, copy DNS and paste in url to see the response**
