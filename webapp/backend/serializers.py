from rest_framework import serializers

from .models import Application, LambdaInstance, Server, PrivateNetwork


class LambdaInstanceApplicationConnectionListingField(serializers.RelatedField):
    """
    Class that defines the way that connections between lambda instances and application will
    be represented.
    """

    def to_internal_value(self, data):
        pass

    def to_representation(self, value):
        lambda_instance_id = value.lambda_instance.uuid
        started = value.started

        return {"id": lambda_instance_id, "started": started}


class ApplicationSerializer(serializers.ModelSerializer):
    """
    A serializer for Application objects.
    """

    lambda_instances = LambdaInstanceApplicationConnectionListingField(many=True, read_only=True)

    class Meta:
        model = Application
        fields = ('uuid', 'name', 'path', 'type', 'description', 'failure_message', 'status',
                  'lambda_instances')


class ServerSerializer(serializers.ModelSerializer):
    """
    A serializer for Server objects.
    """

    class Meta:
        model = Server
        fields = ('id', 'hostname', 'cpus', 'ram', 'disk', 'pub_ip', 'pub_ip_id', 'priv_ip')


class PrivateNetworkSerializer(serializers.ModelSerializer):
    """
    A serializer for PrivateNetwork objects.
    """

    class Meta:
        model = PrivateNetwork
        fields = ('id', 'subnet', 'gateway')


class LambdaInstanceSerializer(serializers.ModelSerializer):
    """
    A serializer for LambdaInstance objects.
    """

    servers = ServerSerializer(many=True, read_only=True)
    private_network = PrivateNetworkSerializer(many=True, read_only=True)
    applications = LambdaInstanceApplicationConnectionListingField(many=True, read_only=True)

    class Meta:
        model = LambdaInstance
        fields = ('id', 'uuid', 'name', 'instance_info', 'status', 'failure_message', 'servers',
                  'private_network', 'master_node', 'started_batch', 'started_streaming',
                  'applications')


class LambdaInstanceInfo(serializers.Serializer):
    """
    Serializer to parse Lambda Instance specs and validate them
    Each of the declared function in this class acts as a validator for the field it refers to in
    its name validator_<field_name>()
    """

    instance_name = serializers.CharField()
    master_name = serializers.CharField()
    project_name = serializers.CharField()
    ip_allocation = serializers.CharField(default='master')
    slaves = serializers.IntegerField()
    vcpus_master = serializers.IntegerField()
    vcpus_slave = serializers.IntegerField()
    ram_master = serializers.IntegerField()
    ram_slave = serializers.IntegerField()
    disk_master = serializers.IntegerField()
    disk_slave = serializers.IntegerField()
    network_request = serializers.IntegerField(default=1)
    public_key_name = serializers.ListField(required=False, default=None)

    # Allowed values for fields
    allowed = {
        "vcpus": [2, 4, 8],
        "disks": [5, 10, 20, 40, 60, 80, 100],
        "ram": [512, 1024, 2048, 4096, 6144, 8192],
        "disk_types": [u'drbd', u'ext_vlmc'],
        "ip_allocation": ['all', 'none', 'master']
    }

    def validate_vcpus_master(self, value):
        if value not in self.allowed['vcpus']:
            raise serializers.ValidationError("Wrong Number of master vcpus, "
                                              "available choices {}.".format(self.allowed['vcpus']))
        return value

    def validate_vcpus_slave(self, value):
        if value not in self.allowed['vcpus']:
            raise serializers.ValidationError("Wrong Number of slave vcpus, "
                                              "available choices {}.".format(self.allowed['vcpus']))
        return value

    def validate_ram_master(self, value):
        if value not in self.allowed['ram']:
            raise serializers.ValidationError("Wrong Amount of master ram, "
                                              "available choices {}.".format(self.allowed['ram']))
        return value

    def validate_ram_slave(self, value):
        if value not in self.allowed['ram']:
            raise serializers.ValidationError("Wrong Amount of slave ram, "
                                              "available choices {}.".format(self.allowed['ram']))
        return value

    def validate_disk_master(self, value):
        if value not in self.allowed['disks']:
            raise serializers.ValidationError("Wrong Size of master disk, "
                                              "available choices {}.".format(self.allowed['disks']))
        return value

    def validate_disk_slave(self, value):
        if value not in self.allowed['disks']:
            raise serializers.ValidationError("Wrong Size of slave disk, "
                                              "available choices {}.".format(self.allowed['disks']))
        return value

    def validate_ip_allocation(self, value):
        if value not in self.allowed['ip_allocation']:
            raise serializers. \
                ValidationError("Wrong choice for ip_allocation, "
                                "available choices {}.".format(self.allowed['ip_allocation']))
        return value

    def validate(self, data):
        return data
