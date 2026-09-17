#!/usr/bin/env bash
set -euo pipefail

# ============================================================
#  CREATE / REFRESH BUSINESS-SOLR INSTANCE TEMPLATES
#  Usage: ./create-templates.sh [dev|test|prod]   (default: test)
#  Backs up any existing template to <name>-old before recreating.
# ============================================================

ENV="${1:-test}"

PROJECT="k973yf"
PROJECT_ID="${PROJECT}-${ENV}"
APP="business"

NETWORK="default"
REGION="northamerica-northeast1"
ZONE="${REGION}-a"
TAGS="business-solr"
BOOT_DISK_IMAGE="cos-125-19216-104-74"
IMAGE_PROJECT="c4hnrd-tools"
IMAGE_REPO="vm-repo"

SERVICE_ACCOUNT="sa-solr-vm@${PROJECT_ID}.iam.gserviceaccount.com"

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATH_TO_STARTUP_SCRIPT="${SELF_DIR}/startupscript.txt"

LEADER_ROLE="leader"
FOLLOWER_ROLE="follower"
LEADER_IMAGE="business-solr-leader"
FOLLOWER_IMAGE="business-solr-follower"
LEADER_TEMPLATE="${APP}-solr-${LEADER_ROLE}-vm-tmpl-${ENV}"
FOLLOWER_TEMPLATE="${APP}-solr-${FOLLOWER_ROLE}-vm-tmpl-${ENV}"
DEVICE_NAME="${APP}-solr-disk-${ENV}"

SCOPES="https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/trace.append"

# ============================================================
#  ENVIRONMENT-SPECIFIC MACHINE TYPES
# ============================================================
case "$ENV" in
  dev)
    LABEL="Development"
    MACHINE_TYPE_LEADER="custom-1-6144"
    BOOT_DISK_SIZE_LEADER="10GiB"
    ;;
  test)
    LABEL="Test"
    MACHINE_TYPE_LEADER="custom-1-6144"
    BOOT_DISK_SIZE_LEADER="10GiB"
    MACHINE_TYPE_FOLLOWER="custom-1-5120"
    BOOT_DISK_SIZE_FOLLOWER="10GiB"
    ;;
  prod)
    LABEL="Production"
    MACHINE_TYPE_LEADER="custom-2-10240"
    BOOT_DISK_SIZE_LEADER="24GiB"
    MACHINE_TYPE_FOLLOWER="custom-1-8192-ext"
    BOOT_DISK_SIZE_FOLLOWER="16GiB"
    ;;
  *)
    echo "ERROR: Unknown ENV '$ENV' (expected dev / test / prod)" >&2
    exit 1
    ;;
esac

# ============================================================
#  COMPUTE JVM MEMORY (1/3 of machine RAM)
#  Handles standard families (e2-standard-N => N*4GiB) and
#  custom types (custom-*-MMMM => MMMM MB total, optional -ext).
# ============================================================
compute_jvm_mem() {
  local mt="$1"
  local g
  if [[ "$mt" =~ ^e2-standard-([0-9]+)$ ]]; then
    g=$(( ${BASH_REMATCH[1]} * 4 ))
  elif [[ "$mt" =~ ^custom-[0-9]+-([0-9]+)(-ext)?$ ]]; then
    g=$(( (${BASH_REMATCH[1]} / 1024) ))
  else
    echo "ERROR: Unsupported machine type for JVM compute: $mt" >&2
    exit 1
  fi
  g=$(( g / 3 ))
  echo "${g}g"
}

LEADER_JVM_MEM="$(compute_jvm_mem "$MACHINE_TYPE_LEADER")"
echo "Leader JVM mem: $LEADER_JVM_MEM (from $MACHINE_TYPE_LEADER)"
if [[ "$ENV" != "dev" ]]; then
  FOLLOWER_JVM_MEM="$(compute_jvm_mem "$MACHINE_TYPE_FOLLOWER")"
  echo "Follower JVM mem: $FOLLOWER_JVM_MEM (from $MACHINE_TYPE_FOLLOWER)"
fi

# ============================================================
#  HELPERS
# ============================================================
log() { echo -e "[$(date -u +%H:%M:%S)] $1"; }

# Back up an existing template to <name>-old, then remove the original.
# gcloud has no template-clone flag, so the copy is rebuilt from the
# current template's own config (describe -> explicit create flags).
backup_instance_template() {
  local name="$1"
  if ! gcloud compute instance-templates describe "$name" \
       --project="$PROJECT_ID" &>/dev/null; then
    return
  fi
  log "Template '$name' exists — backing up to '${name}-old'..."
  gcloud compute instance-templates delete "${name}-old" \
    --project="$PROJECT_ID" --quiet 2>/dev/null || true

  local tmpdir json_file
  tmpdir="$(mktemp -d)"
  json_file="${tmpdir}/tmpl.json"
  gcloud compute instance-templates describe "$name" \
    --project="$PROJECT_ID" --format=json > "$json_file"

  local machine_type image disk_size disk_type device_name has_nat nic
  machine_type="$(python3 -c 'import json,sys;j=json.load(sys.stdin);print(j["properties"]["machineType"])' < "$json_file")"
  image="$(python3 -c 'import json,sys;j=json.load(sys.stdin);print(j["properties"]["disks"][0]["initializeParams"]["sourceImage"])' < "$json_file")"
  disk_size="$(python3 -c 'import json,sys;j=json.load(sys.stdin);print(j["properties"]["disks"][0]["initializeParams"]["diskSizeGb"])' < "$json_file")"
  disk_type="$(python3 -c 'import json,sys;j=json.load(sys.stdin);print(j["properties"]["disks"][0]["initializeParams"]["diskType"])' < "$json_file")"
  device_name="$(python3 -c 'import json,sys;j=json.load(sys.stdin);print(j["properties"]["disks"][0]["deviceName"])' < "$json_file")"
  has_nat="$(python3 -c 'import json,sys;j=json.load(sys.stdin);print("yes" if j["properties"]["networkInterfaces"][0].get("accessConfigs") else "no")' < "$json_file")"

  local startup_file other_meta
  startup_file="${tmpdir}/startup.sh"
  other_meta="$(python3 -c 'import json,sys;j=json.load(open(sys.argv[1]));o=open(sys.argv[2],"w");p=[i["key"]+"="+i["value"] for i in j["properties"]["metadata"].get("items",[]) if i["key"]!="startup-script"];[o.write(i["value"]) for i in j["properties"]["metadata"].get("items",[]) if i["key"]=="startup-script"];o.close();print(",".join(p))' "$json_file" "$startup_file")"

  if [[ "$has_nat" == "no" ]]; then
    nic="network=projects/${PROJECT_ID}/global/networks/${NETWORK},stack-type=IPV4_ONLY,no-address"
  else
    nic="network=projects/${PROJECT_ID}/global/networks/${NETWORK},stack-type=IPV4_ONLY"
  fi

  local extra_meta=()
  if [[ -n "$other_meta" ]]; then
    extra_meta=(--metadata="$other_meta")
  fi

  gcloud compute instance-templates create "${name}-old" \
    --project="$PROJECT_ID" \
    --machine-type="$machine_type" \
    --network-interface="$nic" \
    --metadata-from-file=startup-script="$startup_file" \
    "${extra_meta[@]}" \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --scopes="$SCOPES" \
    --tags="$TAGS" \
    --create-disk=auto-delete=yes,boot=yes,device-name="$DEVICE_NAME",image="$image",mode=rw,size="${disk_size}GB",type="$disk_type" \
    --shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --quiet

  rm -rf "$tmpdir"

  gcloud compute instance-templates delete "$name" \
    --project="$PROJECT_ID" --quiet
}

create_template() {
  local tmpl="$1"
  local role="$2"
  local machine_type="$3"
  local boot_disk_size="$4"
  local jvm_mem="$5"
  local image="$6"
  local cache_opts="${7:-}"

  local metadata="google-logging-enabled=true,role=${role},env=${ENV},label=${LABEL},jvm_mem=${jvm_mem},image=${image},image_project=${IMAGE_PROJECT},image_repo=${IMAGE_REPO},zone=${ZONE},block-project-ssh-keys=TRUE"
  if [[ -n "$cache_opts" ]]; then
    metadata="${metadata},${cache_opts}"
  fi

  log "Creating template: $tmpl ($role, ${machine_type})"
  gcloud compute instance-templates create "$tmpl" \
    --project="$PROJECT_ID" \
    --machine-type="$machine_type" \
    --network-interface=network=projects/${PROJECT_ID}/global/networks/${NETWORK},stack-type=IPV4_ONLY \
    --metadata-from-file=startup-script="$PATH_TO_STARTUP_SCRIPT" \
    --metadata="$metadata" \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account="$SERVICE_ACCOUNT" \
    --scopes="$SCOPES" \
    --tags="$TAGS" \
    --create-disk=auto-delete=yes,boot=yes,device-name="$DEVICE_NAME",image=projects/cos-cloud/global/images/$BOOT_DISK_IMAGE,mode=rw,size="$boot_disk_size",type=pd-ssd \
    --shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring
}

# ============================================================
#  CREATE TEMPLATES
# ============================================================
log "=== Creating business-solr instance templates for ${ENV} in ${PROJECT_ID} ==="

if [[ ! -f "$PATH_TO_STARTUP_SCRIPT" ]]; then
  echo "ERROR: Startup script not found at $PATH_TO_STARTUP_SCRIPT" >&2
  exit 1
fi

backup_instance_template "$LEADER_TEMPLATE"
create_template "$LEADER_TEMPLATE" "$LEADER_ROLE" \
  "$MACHINE_TYPE_LEADER" "$BOOT_DISK_SIZE_LEADER" \
  "$LEADER_JVM_MEM" "$LEADER_IMAGE"

if [[ "$ENV" != "dev" ]]; then
  backup_instance_template "$FOLLOWER_TEMPLATE"
  create_template "$FOLLOWER_TEMPLATE" "$FOLLOWER_ROLE" \
    "$MACHINE_TYPE_FOLLOWER" "$BOOT_DISK_SIZE_FOLLOWER" \
    "$FOLLOWER_JVM_MEM" "$FOLLOWER_IMAGE"
fi

log "✔ Done. Templates created for ${ENV}."