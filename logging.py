class Logger():
    """
    Class to print out formatted logs
    """

    MSG = 0
    CONNECTION = 1
    WARNING = 2
    ERROR = 3

    log_format = [
            '[ ] {}',  # MSG
            '[ ] {host} - {method} {path} {version} - {code} {code_info}',  # CONNECTION
            '[W] {}',  # WARNING
            '[E] {}'  # ERROR
    ]

    # log_format = {
    #         'msg': '[ ] {}',
    #         'connection': '[ ] {host} - {method} {path} {version}',
    #         'warning': '[W] {}',
    #         'error': '[E] {}'
    # }

    def __init__(self):
        pass

    def log(self, data, msg_type=0):
        if type(data) == dict:
            print(self.log_format[msg_type].format(**data))
        else:
            print(self.log_format[msg_type].format(data))
        # if msg_type == self.MSG:
        #     print(data)
        # elif msg_type == self.CONNECTION:
        #     print(log_format['connection'].format(data))
