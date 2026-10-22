from fastapi import Query


class Paginacao:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Registros a pular"),
        limit: int = Query(50, ge=1, le=200, description="Máximo de registros"),
    ):
        self.skip = skip
        self.limit = limit