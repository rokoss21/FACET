class FACETError(Exception):
    def __init__(self, code: str, message: str, line: int = None, col: int = None):
        self.code = code
        self.line = line
        self.col = col
        super().__init__(
            f"{code}: {message}" + (f" (line {line}, col {col})" if line is not None else "")
        )
