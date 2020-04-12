Quick example of Docker, Kubernetes, protocol buffer and gRPC.

Setup steps on Ubuntu 18.04:

apt-get update
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add  # Add the Kubernetes signing key
apt install software-properties-common    # needed by apt-add-repository
apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
apt-get install docker.io kubeadm kubectl kubelet kubernetes-cni
swapoff -a
kubeadm init --pod-network-cidr=10.244.0.0/16
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
kubectl taint nodes --all node-role.kubernetes.io/master-

apt install python3-pip
python3 -m pip install grpcio
python3 -m pip install grpcio-tools
git clone -b v1.28.1 https://github.com/grpc/grpc


