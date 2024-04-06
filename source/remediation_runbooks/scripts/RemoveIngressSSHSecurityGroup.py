# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import json

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

boto_config = Config(retries={"mode": "standard", "max_attempts": 10})


def connect_to_ec2(boto_config):
    return boto3.client("ec2", config=boto_config)


def revoke_ssh_ingress_security_group(security_group_id, client):
    try:
        response = client.revoke_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': 'SSH access from all IPs'
                        },
                    ],
                },
            ],
        )
        print(f"Revoked SSH Ingress from Security Group: {security_group_id}")
        print(json.dumps(response, indent=2, default=str))
    except Exception as e:
        exit(f"FAILED: SSH Ingress was NOT revoked from Security Group: {security_group_id} - {str(e)}")


def remove_ingress_ssh_security_group(event, _):
    client = connect_to_ec2(boto_config)

    security_group_id = event.get("SecurityGroupId")
    if not security_group_id:
        exit("ERROR: SecurityGroupId is missing in the event.")

    revoke_ssh_ingress_security_group(security_group_id, client)


# Example usage:
# event = {"SecurityGroupId": "your_security_group_id_here"}
# remove_ingress_ssh_security_group(event, None)
