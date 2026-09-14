from pydantic import BaseModel

class DocumentUpload(BaseModel):
    pass

class IngestResponse(BaseModel):
    num_chunks: int
    collection_name: str
