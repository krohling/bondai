import nltk
import faiss
import numpy as np
from typing import List
from bondai.models import EmbeddingModel
from concurrent.futures import ThreadPoolExecutor, as_completed

nltk.download("punkt", quiet=True)

EMBED_BATCH_SIZE = 16
MAX_EMBED_WORKERS = 5
SENTENCE_CONCAT_COUNT = 4


def split_text(
    embedding_model: EmbeddingModel, text: str, max_chunk_length: int = None
) -> List[str]:
    if not max_chunk_length:
        max_chunk_length = embedding_model.max_tokens

    result = []
    split = nltk.sent_tokenize(text)
    split = concatenate_strings(split, SENTENCE_CONCAT_COUNT)
    for s in split:
        if embedding_model.count_tokens(s) > max_chunk_length:
            split2 = s.split("\n")
            for s2 in split2:
                if embedding_model.count_tokens(s2) > max_chunk_length:
                    split3 = split_tokens(embedding_model, s2, max_chunk_length)
                    for s3 in split3:
                        result.append(s3)
                else:
                    result.append(s2)
        else:
            result.append(s)

    filtered_list = [s for s in result if s.strip()]
    return filtered_list


def concatenate_strings(arr: List[str], n: int) -> List[str]:
    arr2 = []
    for i in range(0, len(arr), n):
        concat_str = "".join(arr[i : i + n])
        arr2.append(concat_str)
    return arr2


def split_tokens(
    embedding_model: EmbeddingModel, input: str, max_length: int
) -> List[str]:
    if embedding_model.count_tokens(input) <= max_length:
        return input

    item = ""
    result = []
    for i, c in enumerate(input):
        item += c
        if embedding_model.count_tokens(item) >= max_length:
            result.append(item)
            item = ""

    return result


def semantic_search(
    embedding_model: EmbeddingModel, query: str, text: str, max_tokens: int
) -> str:
    if embedding_model.count_tokens(text) <= max_tokens:
        return text

    sentences = split_text(embedding_model, text)
    query_embedding = embedding_model.create_embedding(query)
    query_embedding = np.array(query_embedding).astype("float32")

    # Convert embeddings to FAISS compatible format (they need to be normalized)
    faiss.normalize_L2(query_embedding)

    # Create a FAISS index
    index = faiss.IndexFlatIP(
        query_embedding.shape[1]
    )  # IndexFlatIP is for inner product (which is equivalent to cosine similarity when vectors are normalized)

    # Split the sentences into batches of up to EMBED_BATCH_SIZE sentences
    sentence_batches = [
        sentences[i : i + EMBED_BATCH_SIZE]
        for i in range(0, len(sentences), EMBED_BATCH_SIZE)
    ]

    # Store embeddings and their corresponding sentences
    embeddings_list = []
    sentences_list = []

    # Parallelize the calls to create_embedding using ThreadPoolExecutor
    with ThreadPoolExecutor(MAX_EMBED_WORKERS) as executor:
        future_to_batch = {
            executor.submit(embedding_model.create_embedding, batch): batch
            for batch in sentence_batches
        }
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_embeddings = future.result()
                embeddings_list.extend(batch_embeddings)
                sentences_list.extend(batch)
            except Exception as e:
                print(e)

    embeddings_list = [
        np.array(embedding).astype("float32") for embedding in embeddings_list
    ]
    # Add all sentence embeddings to the index
    embeddings_array = np.vstack(embeddings_list)
    faiss.normalize_L2(embeddings_array)  # Normalize the embeddings
    index.add(embeddings_array)  # Add to FAISS index

    # Query the index for the top N most similar sentences
    D, I = index.search(
        query_embedding, len(sentences_list)
    )  # Search for all sentences

    # Sort results by similarity
    sorted_results = sorted(
        zip(I[0], D[0], sentences_list), key=lambda x: x[1], reverse=True
    )

    filtered = []
    str_items = ""
    for idx, _, sentence in sorted_results:
        if embedding_model.count_tokens(f"{str_items}\n\n{sentence}") <= max_tokens:
            str_items += f"\n\n{sentence}"
            filtered.append(sentence)
        else:
            break

    output = "\n\n".join(filtered)

    return output
