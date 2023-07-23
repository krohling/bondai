import nltk
import numpy as np
from bondai.models.openai_wrapper import create_embedding, count_tokens

nltk.download("punkt")

MAX_EMBED_TOKENS = 250
SENTENCE_CONCAT_COUNT = 4

def cosine_similarity(vec1, vec2):
  dot_product = np.dot(vec1, vec2)
  norm1 = np.linalg.norm(vec1)
  norm2 = np.linalg.norm(vec2)
  return dot_product / (norm1 * norm2)

def split_text(text, max_length):
    result = []
    split = nltk.sent_tokenize(text)
    split = concatenate_strings(split, SENTENCE_CONCAT_COUNT)
    for s in split:
        if count_tokens(s) > max_length:
            split2 = s.split('\n')
            for s2 in split2:
                if count_tokens(s2) > max_length:
                    split3 = split_tokens(s2, max_length)
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

def split_tokens(input, max_length):
    if count_tokens(input) <= max_length: return input

    item = ''
    result = []
    for i, c in enumerate(input):
        item += c
        if count_tokens(item) >= max_length:
            result.append(item)
            item = ''
    
    return result


def semantic_search(query, text, max_tokens):
    if count_tokens(text) <= max_tokens: return text

    results = []
    sentences = split_text(text, MAX_EMBED_TOKENS)
    query_embedding = create_embedding(query)

    for i,s in enumerate(sentences):
        print(s)
        try:
            s_embedding = create_embedding(s)
            similarity = cosine_similarity(query_embedding, s_embedding)

            results.append({
                "sentence": s,
                "similarity": similarity,
                "order": i
            })
        except Exception as e:
            print(e)
    
    results.sort(key=lambda x: x['similarity'], reverse=True)

    filtered = []
    str_items = ''
    for r in results:
        if count_tokens(f"{str_items}\n\n{r['sentence']}") <= max_tokens:
            str_items += f"\n\n{r['sentence']}"
            filtered.append(r)
        else:
            break

    filtered.sort(key=lambda x: x['order'])
    filtered_str = map(lambda x: x['sentence'], filtered)
    output = '\n\n'.join(filtered_str)

    return output

    