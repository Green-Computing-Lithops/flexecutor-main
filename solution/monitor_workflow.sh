#!/bin/bash
# Debug script to monitor workflow execution

echo "=== MONITORING TITANIC WORKFLOW ==="

echo "1. Current Kubernetes resources:"
kubectl get pods,jobs -n inigo-jobs-energy

echo -e "\n2. Recent events:"
kubectl get events -n inigo-jobs-energy --sort-by='.lastTimestamp' | tail -5

echo -e "\n3. Node resources:"
kubectl top nodes | head -3

echo -e "\n4. Current MinIO results:"
cd /home/users/iarriazu/flexecutor-main && source .venv/bin/activate && python3 verify_results.py

echo -e "\n5. Recent logs (if any):"
ls -la /tmp/lithops-iarriazu/logs/ | tail -3
