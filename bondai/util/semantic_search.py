import nltk
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

nltk.download("punkt", quiet=True)

EMBED_BATCH_SIZE = 16
MAX_EMBED_TOKENS = 250
MAX_EMBED_WORKERS = 5
SENTENCE_CONCAT_COUNT = 4

def cosine_similarity(vec1, vec2):
  dot_product = np.dot(vec1, vec2)
  norm1 = np.linalg.norm(vec1)
  norm2 = np.linalg.norm(vec2)
  return dot_product / (norm1 * norm2)

def split_text(embedding_model, text, max_length):
    result = []
    split = nltk.sent_tokenize(text)
    split = concatenate_strings(split, SENTENCE_CONCAT_COUNT)
    for s in split:
        if embedding_model.count_tokens(s) > max_length:
            split2 = s.split('\n')
            for s2 in split2:
                if embedding_model.count_tokens(s2) > max_length:
                    split3 = split_tokens(embedding_model, s2, max_length)
                    for s3 in split3:
                        result.append(s3)
                else:
                    result.append(s2)
        else:
            result.append(s)

    filtered_list = [s for s in result if s.strip()]
    return filtered_list

def concatenate_strings(arr, n):
    arr2 = []
    for i in range(0, len(arr), n):
        concat_str = ''.join(arr[i: i+n])
        arr2.append(concat_str)
    return arr2

def split_tokens(embedding_model, input, max_length):
    if embedding_model.count_tokens(input) <= max_length: return input

    item = ''
    result = []
    for i, c in enumerate(input):
        item += c
        if embedding_model.count_tokens(item) >= max_length:
            result.append(item)
            item = ''
    
    return result


def semantic_search(embedding_model, query, text, max_tokens):
    if embedding_model.count_tokens(text) <= max_tokens: return text

    results = []
    sentences = split_text(embedding_model, text, MAX_EMBED_TOKENS)
    query_embedding = embedding_model.create_embedding(query)
    
    # Split the sentences into batches of up to 16 sentences
    sentence_batches = [sentences[i:i+EMBED_BATCH_SIZE] for i in range(0, len(sentences), EMBED_BATCH_SIZE)]

    # Parallelize the calls to create_embedding using ThreadPoolExecutor
    with ThreadPoolExecutor(MAX_EMBED_WORKERS) as executor:
        future_to_batch = {executor.submit(embedding_model.create_embedding, batch): batch for batch in sentence_batches}
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_embeddings = future.result()
                for s, s_embedding in zip(batch, batch_embeddings):
                    similarity = cosine_similarity(query_embedding, s_embedding)
                    results.append({
                        "sentence": s,
                        "similarity": similarity,
                        "order": sentences.index(s)
                    })
            except Exception as e:
                print(e)

    results.sort(key=lambda x: x['similarity'], reverse=True)

    filtered = []
    str_items = ''
    for r in results:
        if embedding_model.count_tokens(f"{str_items}\n\n{r['sentence']}") <= max_tokens:
            str_items += f"\n\n{r['sentence']}"
            filtered.append(r)
        else:
            break

    filtered.sort(key=lambda x: x['order'])
    filtered_str = map(lambda x: x['sentence'], filtered)
    output = '\n\n'.join(filtered_str)

    return output

    