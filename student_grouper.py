from interest_data import canonical_interests 

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

# 1. Define canonical interests & their synonyms
"""canonical_interests = {
    "biology": ["biology", "bio", "biological sciences", "life sciences", "animal science"],
    "computer_science": ["computer science", "CS", "software", "programming", "AI", "machine learning"],
    "engineering": ["engineering", "mechanical engineering", "electrical engineering", "civil engineering", "aerospace"],
    # Add more categories here
}"""

# 2. Precompute canonical category embeddings (average over synonyms)
canonical_embeddings = {}
for category, synonyms in canonical_interests.items():
    syn_embeddings = model.encode(synonyms, convert_to_tensor=True)
    avg_embedding = syn_embeddings.mean(dim=0)
    canonical_embeddings[category] = avg_embedding

def map_student_to_interest(major, interests, career_path, threshold=0.65):
    # Combine all student inputs into one text
    student_text = f"{major}. {interests}. {career_path}"

    student_embedding = model.encode(student_text, convert_to_tensor=True)

    # Compute cosine similarity with each canonical interest
    similarities = {}
    for category, embedding in canonical_embeddings.items():
        sim = util.pytorch_cos_sim(student_embedding, embedding).item()
        similarities[category] = sim

    # Pick the best match over threshold
    best_category = max(similarities, key=similarities.get)
    if similarities[best_category]:
        return best_category
    else:
        return None  # or "other"

# Example usage
student_major = "Bio"
student_interests = "I love animals and plant blogy"
student_career_path = "I want to be a veterinarian"

mapped_interest = map_student_to_interest(student_major, student_interests, student_career_path)
print("Mapped interest category:", mapped_interest)
