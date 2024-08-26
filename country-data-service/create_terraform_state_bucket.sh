#!/bin/bash

# Set variables
BUCKET_NAME="terraform-chalice-state-bucket-2"
REGION="us-west-2"
DYNAMODB_TABLE_NAME="terraform-state-lock"

# Check if the S3 bucket already exists
if aws s3api head-bucket --bucket $BUCKET_NAME --region $REGION 2>&1 | grep -q "404"; then
    # Create the S3 bucket
    aws s3api create-bucket \
        --bucket $BUCKET_NAME \
        --region $REGION \
        --create-bucket-configuration LocationConstraint=$REGION

    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket $BUCKET_NAME \
        --versioning-configuration Status=Enabled

    # Enable server-side encryption
    aws s3api put-bucket-encryption \
        --bucket $BUCKET_NAME \
        --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
else
    echo "Bucket $BUCKET_NAME already exists."
fi

# Check if the DynamoDB table already exists
if aws dynamodb describe-table --table-name $DYNAMODB_TABLE_NAME --region $REGION 2>&1 | grep -q "ResourceNotFoundException"; then
    # Create DynamoDB table for state locking
    aws dynamodb create-table \
        --table-name $DYNAMODB_TABLE_NAME \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region $REGION
else
    echo "Table $DYNAMODB_TABLE_NAME already exists."
fi
