#!/bin/bash -e

kubectl apply --namespace webisservices -f dist/k8s/pan18-author-profiling-k8s.yml
kubectl apply --namespace webisservices -f dist/k8s/pan18-style-k8s.yml
kubectl apply --namespace webisservices -f dist/k8s/pan18-masking-k8s.yml

