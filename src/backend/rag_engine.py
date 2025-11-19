import time
from typing import Dict, List

from dotenv import load_dotenv
from moorcheh_sdk import MoorchehClient
from moorcheh_sdk.exceptions import APIError, AuthenticationError, InvalidInputError

load_dotenv()


class RAGEngine:
    def __init__(
        self,
        namespace: str,
        user_id: str = None,
        db=None,
    ):
        self.client = MoorchehClient()
        self.namespace = namespace
        self.user_id = user_id
        self.db = db
        self.chunk_ids = 0
        self.chunk_ids_to_clear = []

    def list_namespaces(self):
        return self.client.list_namespaces()

    def clear_namespace(self):
        namespaces = self.list_namespaces()
        for namespace in namespaces["namespaces"]:
            if namespace["namespace_name"] == self.namespace:
                try:
                    self.client.delete_namespace(
                        namespace_name=namespace["namespace_name"]
                    )
                except Exception as e:
                    print(
                        f"Error deleting namespace {namespace['namespace_name']}: {e}"
                    )
                break

    def create_namespace(self):
        self.client.create_namespace(namespace_name=self.namespace, type="text")

    def add_documents(self, chunks: List[Dict]):
        if not chunks:
            return

        try:
            file_boundaries = []
            current_file = None
            start_idx = 0

            for idx, chunk in enumerate(chunks):
                filename = chunk.get("source", "unknown")
                if filename != current_file:
                    if current_file is not None:
                        file_boundaries.append((current_file, start_idx, idx))
                    current_file = filename
                    start_idx = idx

            if current_file is not None:
                file_boundaries.append((current_file, start_idx, len(chunks)))

            response = self.client.upload_documents(
                namespace_name=self.namespace,
                documents=chunks,
            )
            self.chunk_ids += response["queued_documents"]
            document_ids = response["document_ids"]
            self.chunk_ids_to_clear.extend(document_ids)

            if self.db and self.user_id and document_ids:
                for filename, start_idx, end_idx in file_boundaries:
                    file_document_ids = document_ids[start_idx:end_idx]
                    if file_document_ids:
                        self.db.add_documents(self.user_id, file_document_ids, filename)

            return response
        except InvalidInputError as e:
            raise e
        except AuthenticationError as e:
            raise e
        except APIError as e:
            raise e
        except Exception as e:
            raise e

    def clear_documents(self, ids: List[str | int]):
        try:
            response = self.client.delete_documents(
                namespace_name=self.namespace, ids=ids
            )
            self.chunk_ids -= len(ids)
            self.chunk_ids_to_clear = [
                id for id in self.chunk_ids_to_clear if id not in ids
            ]
            return response
        except Exception as e:
            print(f"Error clearing documents from namespace {self.namespace}: {e}")
            raise e

    def reset_namespace(self):
        try:
            if self.db and self.user_id:
                user_document_ids = self.db.get_user_document_ids(self.user_id)
                if user_document_ids:
                    response = self.client.delete_documents(
                        namespace_name=self.namespace, ids=user_document_ids
                    )
                    deleted_ids = response.get("deleted_ids", [])
                    self.chunk_ids_to_clear = [
                        id for id in self.chunk_ids_to_clear if id not in deleted_ids
                    ]
                    self.chunk_ids -= len(deleted_ids)
                    self.db.delete_user_documents(self.user_id)
                    return response
                else:
                    self.chunk_ids_to_clear = []
                    self.chunk_ids = 0
                    return {"deleted_ids": []}
            else:
                response = self.client.delete_documents(
                    self.namespace, self.chunk_ids_to_clear
                )
                deleted_ids = response.get("deleted_ids", [])
                self.chunk_ids_to_clear = [
                    id for id in self.chunk_ids_to_clear if id not in deleted_ids
                ]
                self.chunk_ids -= len(deleted_ids)
                return response
        except Exception as e:
            print(f"Error resetting namespace {self.namespace}: {e}")
            raise e

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        start_time = time.perf_counter()
        results = self.client.search(
            namespaces=[self.namespace], query=query, top_k=top_k
        )
        end_time = time.perf_counter()
        elapsed_seconds = end_time - start_time
        time_taken = int(elapsed_seconds * 1000)

        filtered_results = results["results"]
        if self.user_id:
            filtered_results = [
                result
                for result in filtered_results
                if result.get("metadata", {}).get("user_id") == self.user_id
            ]

        return {
            "results": filtered_results,
            "time_taken": time_taken,
        }

    def get_chunk_count(self) -> int:
        if self.db and self.user_id:
            return self.db.get_user_document_count(self.user_id)
        return self.chunk_ids
