import boto3

def connect_to_ec2():
    return boto3.client("ec2")


def revoke_ssh_ingress_security_group(security_group_id):
    try:
        client = connect_to_ec2()
        response = client.revoke_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
                    'Ipv6Ranges': [{'CidrIpv6': '::/0'}]
                }
            ]
        )
        print(f"Revoked SSH Ingress from Security Group: {security_group_id}")
        print(response)
    except Exception as e:
        exit(f"FAILED: SSH Ingress was NOT revoked from Security Group: {security_group_id} - {str(e)}")


def remove_ingress_ssh_security_group(event, _):
    security_group_id = event.get("SecurityGroupId")
    if not security_group_id:
        exit("ERROR: SecurityGroupId is missing in the event.")

    revoke_ssh_ingress_security_group(security_group_id)


# Example usage:
# if __name__ == "__main__":
#     event = {"SecurityGroupId": "sg-08f973a5f2eb7cb6e"}
#     remove_ingress_ssh_security_group(event, None)
