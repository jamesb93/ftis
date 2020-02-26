class InvalidYamlError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class AnalyserNotFound(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class AnalyserParameterInvalid(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)