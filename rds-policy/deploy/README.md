# RDS Policy Agent — Deploy Manifests

Kubernetes CRs for deploying the RDS policy skill via the lightspeed-agentic-operator.

## Prerequisites

- OpenShift 4.18+ cluster with `agent-sandbox-controller` and `lightspeed-agentic-operator` deployed
- GCP Vertex AI credentials (authorized_user or service account JSON)
- Container images pushed to a public registry

## Placeholders

All manifests use placeholders instead of real values. Replace before applying:

| Placeholder | Description | Example |
|---|---|---|
| `REPLACE_REGISTRY` | Container image registry prefix | `quay.io/rh_ee_apalanis` |
| `REPLACE_GCP_PROJECT_ID` | GCP project for Vertex AI | `my-gcp-project` |
| `REPLACE_GCP_REGION` | Vertex AI region | `global` |

## Manifests

Apply in order:

| File | Kind | Scope | Description |
|---|---|---|---|
| `00-llm-credentials.yaml` | Secret | Namespaced | Template only — use `kubectl create secret` to create from a credentials file |
| `01-llm-provider.yaml` | LLMProvider | Cluster | Vertex AI provider config |
| `02-agent-default.yaml` | Agent | Cluster | Default tier (required) |
| `02-agent-smart.yaml` | Agent | Cluster | Smart tier — extended timeouts |
| `02-agent-fast.yaml` | Agent | Cluster | Fast tier — haiku model |
| `03-approval-policy.yaml` | ApprovalPolicy | Cluster | Singleton — all stages Manual |
| `04-rds-policy-proposal.yaml` | Proposal | Namespaced | The prompt to the agent |
| `05-sandbox-template.yaml` | SandboxTemplate | Namespaced | Base template (plain sandbox) |
| `05-sandbox-template-openshell.yaml` | SandboxTemplate | Namespaced | Alternative with OpenShell supervisor |
| `openshell-policy.yaml` | (file) | N/A | Sandbox policy for OpenShell mode |

## Quick Deploy

```sh
# Set your values
export REGISTRY=quay.io/your-org
export GCP_PROJECT=your-gcp-project
export GCP_REGION=global
export KUBECONFIG=~/kubeconfigs/kubeconfig.your-cluster

# Create the credentials secret (key must be "credentials.json")
kubectl create secret generic vertex-ai-credentials \
    -n openshift-lightspeed \
    --from-file=credentials.json=~/.config/gcloud/application_default_credentials.json

# Substitute placeholders and apply
for f in 01-llm-provider.yaml 02-agent-default.yaml 02-agent-smart.yaml \
         02-agent-fast.yaml 03-approval-policy.yaml \
         05-sandbox-template.yaml 04-rds-policy-proposal.yaml; do
    sed "s|REPLACE_REGISTRY|${REGISTRY}|g; \
         s|REPLACE_GCP_PROJECT_ID|${GCP_PROJECT}|g; \
         s|REPLACE_GCP_REGION|${GCP_REGION}|g" deploy/$f | kubectl apply -f -
done

# Approve the analysis stage
kubectl patch proposalapproval rds-policy-explain -n openshift-lightspeed \
    --type=merge \
    -p '{"spec":{"stages":[{"type":"Analysis","decision":"Approved","analysis":{}}]}}'
```

## Monitoring

```sh
# Watch proposal status
kubectl get proposal rds-policy-explain -n openshift-lightspeed -w

# Stream sandbox agent logs
kubectl logs -n openshift-lightspeed ls-analysis-rds-policy-explain -f

# Read the analysis result
kubectl get analysisresult -n openshift-lightspeed
```
