from django.db import models

# Create your models here.


class VdiInstance(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    instance_id = models.CharField(max_length=255, null=True, blank=True)
    instance_type = models.CharField(max_length=255, null=True, blank=True)
    instance_state = models.CharField(max_length=255, null=True, blank=True)
    instance_public_ip = models.CharField(max_length=255, null=True, blank=True)
    instance_private_ip = models.CharField(max_length=255, null=True, blank=True)
    instance_key_name = models.CharField(max_length=255, null=True, blank=True)
    instance_security_group = models.CharField(max_length=255, null=True, blank=True)
    instance_subnet_id = models.CharField(max_length=255, null=True, blank=True)
    instance_vpc_id = models.CharField(max_length=255, null=True, blank=True)
    instance_ami_id = models.CharField(max_length=255, null=True, blank=True)
    instance_launch_time = models.DateTimeField()
    instance_termination_time = models.DateTimeField()
    instance_user_data = models.TextField(null=True, blank=True)
    instance_tags = models.TextField(null=True, blank=True)
    instance_monitoring = models.BooleanField(default=False, null=True, blank=True)
    instance_ebs_optimized = models.BooleanField(default=False, null=True, blank=True)
    instance_public_dns = models.CharField(max_length=255, null=True, blank=True)
    instance_private_dns = models.CharField(max_length=255, null=True, blank=True)
    instance_architecture = models.CharField(max_length=255, null=True, blank=True)
    instance_hypervisor = models.CharField(max_length=255, null=True, blank=True)
    instance_virtualization_type = models.CharField(max_length=255, null=True, blank=True)
    instance_root_device_type = models.CharField(max_length=255, null=True, blank=True)
    instance_root_device_name = models.CharField(max_length=255, null=True, blank=True)
    instance_block_device_mappings = models.TextField(blank=True, null=True)
    instance_iam_instance_profile = models.CharField(max_length=255, null=True, blank=True)
    instance_network_interfaces = models.TextField(blank=True, null=True)
    instance_state_transition_reason = models.TextField(blank=True, null=True)
    instance_state_reason = models.TextField(blank=True, null=True)
    instance_cpu_options = models.TextField(blank=True, null=True)
    instance_capacity_reservation_id = models.CharField(max_length=255, null=True, blank=True)
    instance_capacity_reservation_specification = models.TextField(blank=True, null=True)
    instance_metadata_options = models.TextField(blank=True, null=True)
    instance_enclave_options = models.TextField(blank=True, null=True)
    instance_elastic_gpu_associations = models.TextField(blank=True, null=True)
    instance_elastic_inference_accelerator_associations = models.TextField(blank=True, null=True)
    instance_outpost_arn = models.CharField(max_length=255, null=True, blank=True)
    instance_auto_scaling_group_associations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name