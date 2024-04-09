# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import boto3
from botocore.config import Config


def connect_to_dynamodb(region, boto_config):
    return boto3.client("dynamodb", region_name=region, config=boto_config)


def enable_deletion_protection(event, _):
    """
    Remediates DynamoDB.6 by enabling deletion protection
    On success returns a string map
    On failure returns NoneType
    """
    boto_config = Config(retries={"mode": "standard"})

    dynamodb_client = connect_to_dynamodb(event["region"], boto_config)

    try:
        response = dynamodb_client.list_tables()
        tables = response.get("TableNames", [])

        for table in tables:
            response = dynamodb_client.describe_table(TableName=table)
            deletion_protection = response["Table"].get("DeletionProtectionEnabled", False)

            if not deletion_protection:
                dynamodb_client.update_table(
                    TableName=table,
                    DeletionProtectionEnabled=True
                )
                print(f"Enabled deletion protection for table {table}")
            else:
                print(f"Deletion protection already enabled for table {table}")

        return {
            "response": {
                "message": "Deletion protection enabled for DynamoDB tables",
                "status": "Success",
            }
        }
    except Exception as e:
        exit(f"Error enabling deletion protection: {str(e)}")


# if __name__ == "__main__":
#     event = {
#         "region": "eu-west-2",  # Specify the region where your DynamoDB tables are located
#     }
#     enable_deletion_protection(event, None)
