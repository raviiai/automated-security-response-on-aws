import boto3
import time

###############################
## Function to fetch subnet id
################################

def fetch_subnet_id(instance_id, region):
    ec2_client = boto3.client('ec2', region_name=region)
    
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        subnet_id = response['Reservations'][0]['Instances'][0]['SubnetId']
        
        return subnet_id
    except Exception as e:
        # print(f"Error fetching Subnet ID: {e}")
        return None

###############################
## create and attach NIC
################################

def create_and_attach_nic(instance_id, subnet_id, region):
    ec2_client = boto3.client('ec2', region_name=region)
    
    try:
        response = ec2_client.create_network_interface(SubnetId=subnet_id)
        network_interface_id = response['NetworkInterface']['NetworkInterfaceId']
        
        ec2_client.attach_network_interface(
            NetworkInterfaceId=network_interface_id,
            InstanceId=instance_id,
            DeviceIndex=1
        )
        
        return network_interface_id
    except Exception as e:
        return None

###############################
## Fetch NIC (Original)
################################

def fetch_nic_at_device_0(instance_id, region):
    ec2_client = boto3.client('ec2', region_name=region)
    
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        nic_id = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'][0]['NetworkInterfaceId']
        
        
        return nic_id
    except Exception as e:
       
        return None

###############################
## Create and Attach EIP to instance
################################
def allocate_and_attach_eip(instance_id, network_interface_id, region):
    ec2_client = boto3.client('ec2', region_name=region)
    
    try:
        response = ec2_client.allocate_address(Domain='vpc')
        allocation_id = response['AllocationId']
        
        ec2_client.associate_address(
            AllocationId=allocation_id,
            NetworkInterfaceId=network_interface_id
        )
        
        
        return allocation_id
    except Exception as e:
     
        return None


###############################
## Remove EIP
################################

def remove_eip(allocation_id, region):
    ec2_client = boto3.client('ec2', region_name=region)
    
    try:
        ec2_client.release_address(AllocationId=allocation_id)
               
    except Exception as e:
        pass


###############################
## Detach NIC
################################

def detach_nic(instance_id, nic_id, region):
    # Create EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    # Describe NIC attachments
    response = ec2.describe_instances(InstanceIds=[instance_id])
    attachments = response['Reservations'][0]['Instances'][0]['NetworkInterfaces']
    
    attachment_id = None
    for attachment in attachments:
        if attachment['NetworkInterfaceId'] == nic_id:
            attachment_id = attachment['Attachment']['AttachmentId']
            break

    if attachment_id is None:
        return

    # Detach NIC
    ec2.detach_network_interface(
        AttachmentId=attachment_id,
        Force=True
    )



###############################
## Delete NIC
################################

def delete_nic(nic_id, region):
    # Create EC2 client
    ec2 = boto3.client('ec2', region_name=region)

    while True:
        try:
            # Describe NIC
            response = ec2.describe_network_interfaces(
                NetworkInterfaceIds=[nic_id]
            )
            nic = response['NetworkInterfaces'][0]
            
            # Check if NIC is available
            if nic['Status'] == 'available':
                # Delete NIC
                ec2.delete_network_interface(
                    NetworkInterfaceId=nic_id
                )
                # print("NIC {} deleted successfully.".format(nic_id))
                break  # Break the loop once the NIC is deleted
            else:
                # print("NIC {} is not available yet. Retrying in 10 seconds...".format(nic_id))
                time.sleep(10)  # Wait for 10 seconds before checking again
        except Exception as e:
            # print("Error deleting NIC {}: {}".format(nic_id, e))
            break  # Break the loop in case of an error



###############################
## Main Lambda Handler Function
################################

def lambda_handler(event, context):
    try:
        region_name= event['region']
        instance_id = event['instance_id']
        subnet_id = fetch_subnet_id(instance_id, region_name)
        if subnet_id:
            old_nic_id = fetch_nic_at_device_0(instance_id, region_name)
            if old_nic_id:
                new_nic_id = create_and_attach_nic(instance_id, subnet_id, region_name)
                # print(new_nic_id)
                eip_allocation_id = allocate_and_attach_eip(instance_id, old_nic_id, region_name)
                if eip_allocation_id:   
                    remove_eip(eip_allocation_id, region_name)
                if new_nic_id:
                    detach_nic(instance_id, new_nic_id, region_name)
                    # print(new_nic_id)
                    delete_nic(new_nic_id,region_name)

        return {
            'statusCode': 200,
            'body': f"EC2 instance {instance_id} Public IP removed successfully.."
        }

    except Exception as e:
        # Return error message if stopping the instance fails
        return {
            'statusCode': 500,
            'body': str(e)
        }

###############################
## TESTING
################################
# event = {
#     "instance_id": "i-0e511307f077d1547",
#     "region"  : "eu-west-2"
# }

# lambda_handler(event,None)