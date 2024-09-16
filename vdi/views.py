from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import VdiInstance
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# AWS Configuration
AWS_REGION = "ap-south-1"  # Adjust to your region
AMI_ID = "ami-053284fc22a2c3f82"  # Windows Server 2019 AMI ID
INSTANCE_TYPE = "t2.micro"
KEY_NAME = "vdi"
SECURITY_GROUP_NAME = "launch-wizard-1"  # Use an existing security group
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""

# Using AWS credentials loaded from settings
ec2_client = boto3.client(
    'ec2',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

ec2_resource = boto3.resource(
    'ec2',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Helper function to create a security group for RDP
def create_security_group():
    try:
        response = ec2_client.create_security_group(
            GroupName=SECURITY_GROUP_NAME,
            Description="Security group for Windows RDP access"
        )
        print(response)
        security_group_id = response["GroupId"]

        # Add RDP access to security group (port 3389)
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[{
                'IpProtocol': 'tcp',
                'FromPort': 3389,
                'ToPort': 3389,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}],  # Allow all IPs
            }]
        )
        return security_group_id
    except ClientError as e:
        print(f"Security group creation failed: {e}")
        return None


# Class-based view to create an instance
class CreateInstanceView(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        try:
            security_group_id = "sg-08ff58819f64a19f7"  # Assume existing security group
            
            # Launch a Windows EC2 instance
            instance_data = ec2_client.run_instances(
                ImageId=AMI_ID,
                InstanceType=INSTANCE_TYPE,
                KeyName=KEY_NAME,
                MinCount=1,
                MaxCount=1,
                SecurityGroupIds=[security_group_id],
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': name}]
                }]
            )
            instance_id = instance_data['Instances'][0]['InstanceId']

            # Wait for the instance to be ready
            instance = ec2_resource.Instance(instance_id)
            instance.wait_until_running()
            instance.load()  # Reload to get public IP

            # Save instance information to the database
            vdi_instance = VdiInstance.objects.create(
                name=name,
                instance_id=instance.instance_id,
                instance_type=INSTANCE_TYPE,
                instance_state=instance.state['Name'],
                instance_public_ip=instance.public_ip_address,
                instance_private_ip=instance.private_ip_address,
                instance_key_name=KEY_NAME,
                instance_security_group=security_group_id,
                instance_ami_id=AMI_ID,
                instance_launch_time=timezone.now(),
                instance_public_dns=instance.public_dns_name,
                instance_private_dns=instance.private_dns_name
            )

            return Response({
                'message': 'Windows VDI Instance created!',
                'instance_id': instance_id,
                'public_ip': instance.public_ip_address
            }, status=status.HTTP_201_CREATED)

        except NoCredentialsError:
            return Response({"error": "AWS credentials not found"}, status=status.HTTP_403_FORBIDDEN)
        except ClientError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Class-based view to stop an instance
class StopInstanceView(APIView):
    def post(self, request, *args, **kwargs):
        instance_id = request.data.get('instance_id')
        if not instance_id:
            return Response({'error': 'Instance ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = ec2_resource.Instance(instance_id)
            instance.stop()
            instance.wait_until_stopped()

            # Update instance state in the database
            VdiInstance.objects.filter(instance_id=instance_id).update(instance_state='stopped')

            return Response({'message': f'Instance {instance_id} stopped'}, status=status.HTTP_200_OK)

        except ClientError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Class-based view to delete an instance
class DeleteInstanceView(APIView):
    def post(self, request, *args, **kwargs):
        instance_id = request.data.get('instance_id')
        if not instance_id:
            return Response({'error': 'Instance ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instance = ec2_resource.Instance(instance_id)
            instance.terminate()
            instance.wait_until_terminated()

            # Update termination time in the database
            VdiInstance.objects.filter(instance_id=instance_id).update(
                instance_state='terminated',
                instance_termination_time=timezone.now()
            )

            return Response({'message': f'Instance {instance_id} terminated'}, status=status.HTTP_200_OK)

        except ClientError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
