class InvalidYamlError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class OutputNotFound(Exception):
    def __init__(self, analyser: str):
        super().__init__(f"Output not found or errored for {analyser}")


class InvalidSource(Exception):
    def __init__(self, source: str):
        super().__init__(f"{source} does not exist or is invalid")


class NoCorpusSource(Exception):
    def __init__(self, source: str):
        super().__init__(f"{source} does not exist or is invalid")


class BadCorpusSource(Exception):
    def __init__(self):
        super().__init__("The corpus source is not PURE")  # TODO make this more descriptive


class AnalyserNotFound(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class AnalyserParameterInvalid(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


class NotYetImplemented(Exception):
    def __init__(self):
        super().__init__("This function is not implemented yet")


class ChainIOError(Exception):
    def __init__(self, analyser1, analyser2):
        super().__init__(
            f"""
        Incompatible types
        {analyser1.name} input: {analyser1.input_type}
        {analyser2.name} output: {analyser2.output_type}
        """
        )


class SourceIOError(Exception):
    def __init__(self):
        super().__init__(f"The source and first analyser type are incompatible")


class EmptyWorkables(Exception):
    def __init__(self):
        super().__init__(f"No workables were passed to the proc")
