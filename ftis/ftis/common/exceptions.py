class InvalidYamlError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AnalyserNotFound(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AnalyserParameterInvalid(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AnalyserExists(Exception):
    def __init__(self):
        super().__init__("This analyser already exists")


class BinError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class NotYetImplemented(Exception):
    def __init__(self):
        super().__init__("This function is not implemented yet")


class ChainIOError(Exception):
    def __init__(self, analyser1, analyser2):
        super().__init__(f"""
        Incompatible types
        {analyser1.name} input: {analyser1.input_type}
        {analyser2.name} output: {analyser2.output_type}
        """)


class SourceIOError(Exception):
    def __init__(self):
        super().__init__(
            f"The source and first analyser type are incompatible")
