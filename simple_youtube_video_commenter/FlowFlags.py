class FlowFlag(object):

    def __init__(self, logging_level: str, auth_host_port, auth_host_name: str, noauth_local_webserver: bool):
        self.logging_level = logging_level
        self.auth_host_port = auth_host_port
        self.auth_host_name = auth_host_name
        self.noauth_local_webserver = noauth_local_webserver