import os
from typing import Any, List
from dotenv import load_dotenv
from llama_index.core.embeddings import BaseEmbedding
from openai import OpenAI
from logger.logging_config import logger

class InstructorEmbeddings(BaseEmbedding):

    def __init__(
        self,
        instructor_model_name: str = "embedding-2",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

    def get_embeding(self, query: str) -> List[float]:
        load_dotenv()
        glm_api_key = os.getenv("glm_api_key")
        client = OpenAI(api_key=glm_api_key, base_url="https://open.bigmodel.cn/api/paas/v4/")
        
        import time
        max_retries = 5
        retries = 0
        
        def get_single_embedding(text: str) -> List[float]:
            nonlocal retries
            while retries < max_retries:
                try:
                    response = client.embeddings.create(
                        model="embedding-2",
                        input=text
                    )
                    return response.data[0].embedding
                except Exception as e:
                    logger.error(f"An error occurred: {e}, query: {text}")
                    retries += 1
                    if retries >= max_retries:
                        raise e
                    time.sleep(2)  # Optional: wait for 2 seconds before retrying
        
        # Split the query into chunks of 512 characters
        chunks = [query[i:i + 512] for i in range(0, len(query), 512)]
        embeddings = []
        
        for chunk in chunks:
            embedding = get_single_embedding(chunk)
            embeddings.extend(embedding)
        
        return embeddings
    @classmethod
    def class_name(cls) -> str:
        return "instructor"

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self.get_embeding(query)
        return embeddings

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self.get_embeding(text)
        return embeddings

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings= []
        for text in texts:
            embedding= self.get_embeding(text)
            embeddings.append(embedding)
        return embeddings