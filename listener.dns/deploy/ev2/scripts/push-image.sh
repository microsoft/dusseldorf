#!/bin/bash
set -e

if [ -z ${DESTINATION_ACR_NAME+x} ]; then
    echo "DESTINATION_ACR_NAME is unset, unable to continue"
    exit 1;
fi

if [ -z ${TARBALL_IMAGE_FILE_SAS+x} ]; then
    echo "TARBALL_IMAGE_FILE_SAS is unset, unable to continue"
    exit 1;
fi

if [ -z ${IMAGE_NAME+x} ]; then
    echo "IMAGE_NAME is unset, unable to continue"
    exit 1;
fi

if [ -z ${TAG_NAME+x} ]; then
    echo "TAG_NAME is unset, unable to continue"
    exit 1;
fi

if [ -z ${DESTINATION_FILE_NAME+x} ]; then
    echo "DESTINATION_FILE_NAME is unset, unable to continue"
    exit 1;
fi

echo "Folder Contents"
ls

dnf update
dnf install -y zip unzip wget gzip

echo "Login cli using managed identity"
az login --identity

TMP_FOLDER=$(mktemp -d)
cd $TMP_FOLDER

echo "Downloading docker tarball image from $TARBALL_IMAGE_FILE_SAS"
wget -O $DESTINATION_FILE_NAME "$TARBALL_IMAGE_FILE_SAS"

echo "Getting acr credentials"
TOKEN_QUERY_RES=$(az acr login -n "$DESTINATION_ACR_NAME" -t)
TOKEN=$(echo "$TOKEN_QUERY_RES" | jq -r '.accessToken')
DESTINATION_ACR=$(echo "$TOKEN_QUERY_RES" | jq -r '.loginServer')
/package/unarchive/src/Shell/crane auth login "$DESTINATION_ACR" -u "00000000-0000-0000-0000-000000000000" -p "$TOKEN"

DEST_IMAGE_FULL_NAME="$DESTINATION_ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG_NAME"

if [[ "$DESTINATION_FILE_NAME" == *"tar.gz"* ]]; then
  gunzip $DESTINATION_FILE_NAME
fi

echo "Pushing file $TARBALL_IMAGE_FILE to $DEST_IMAGE_FULL_NAME"
/package/unarchive/src/Shell/crane push *.tar "$DEST_IMAGE_FULL_NAME"
