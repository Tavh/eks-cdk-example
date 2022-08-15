from aws_cdk import (Stack, aws_iam, aws_ec2, aws_eks)
from constructs import Construct

EKS_CLUSTER_NAME = 'tav-demo-cluster'
EKS_SERVICE_ROLE = 'tav-eksadmin'
MASTER_ROLE_NAME = 'tav-eks-master-role'


class EKSStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        master_role = self.get_role()
        cluster = self.get_eks_cluster(master_role)
        nodegroup = create_nodegroup(cluster)

    def get_eks_cluster(self, eks_role):
        return aws_eks.Cluster(self,
                               'prod',
                               cluster_name=EKS_CLUSTER_NAME,
                               version=aws_eks.KubernetesVersion.V1_21,
                               default_capacity=0,
                               masters_role=eks_role
                               )
    def get_role(self):
        role = aws_iam.Role(
            self,
            EKS_SERVICE_ROLE,
            assumed_by=aws_iam.AccountRootPrincipal(),
            role_name=MASTER_ROLE_NAME,
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name='AdministratorAccess')
            ]
        )

        eks_instance_profile = aws_iam.CfnInstanceProfile(
            self, 'instanceprofile', roles=[role.role_name], instance_profile_name=MASTER_ROLE_NAME
        ),

        return role

def create_nodegroup(cluster):
    return cluster.add_nodegroup_capacity('eks-nodegroup',
                                          instance_types=[
                                              aws_ec2.InstanceType('m4.large'),
                                          ],
                                          disk_size=25,
                                          min_size=2,
                                          max_size=3,
                                          ami_type=aws_eks.NodegroupAmiType.BOTTLEROCKET_X86_64,
                                          desired_size=2,
                                          remote_access=aws_eks.NodegroupRemoteAccess(
                                              ssh_key_name='eks-ssh-keypair'
                                          ),
                                          capacity_type=aws_eks.CapacityType.SPOT
                                          )