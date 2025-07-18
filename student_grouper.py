from interest_data import canonical_interests 
import re
from textblob import TextBlob
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def text_cleaner(text, filler_words= {"i", "want", "to", "be", "a", "an", "the", "and", "my", "in", "of", "with", "for", "on", "like", "love", 'don', 'not', 'there'}):
    words = text.split()
    filtered_words = [word for word in words if word not in filler_words]
    filtered_text = " ".join(filtered_words)
    filtered_text = re.sub(r"[^\w\s]", "", filtered_text)  # remove punctuation
    filtered_text = re.sub(r"\d+", "", filtered_text)      # remove numbers
    blob_text = TextBlob(filtered_text.strip())
    return str(blob_text.correct())
    
canonical_embeddings = {}
for category, synonyms in canonical_interests.items():
    syn_embeddings = model.encode(synonyms, convert_to_tensor=True)
    avg_embedding = syn_embeddings.mean(dim=0)
    canonical_embeddings[category] = avg_embedding

def map_student_to_interest(major, interests, career_path, threshold=0, numCategories=3):
    # Combine all student inputs into one text
    student_text = text_cleaner(f"{major}. {interests}. {career_path}")

    student_embedding = model.encode(student_text, convert_to_tensor=True)

    # Compute cosine similarity with each canonical interest
    similarities = {}
    for category, embedding in canonical_embeddings.items():
        sim = util.pytorch_cos_sim(student_embedding, embedding).item()
        similarities[category] = sim

    print(dict(sorted(similarities.items(), key=lambda item: item[1])))

    best_categories = []
    for i in range(numCategories):
        if max(similarities.values()) > threshold:     best_categories.append(max(similarities,key=similarities.get))
        similarities.pop(max(similarities, key=similarities.get))


   # best_category = max(similarities, key=similarities.get)

    if len(best_categories) > 0:
        return best_categories
    else:
        return None  # or "other"


if __name__ == "__main__":
    student_major = "undecided"
    student_interests = "i dont know i like the environemnt "
    student_career_path = "maybe ranger ?"

    mapped_interest = map_student_to_interest(student_major, student_interests, student_career_path)
    print("Mapped interest category:", mapped_interest)
