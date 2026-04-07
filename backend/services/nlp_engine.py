from sentence_transformers import SentenceTransformer, util
from services.jd_processor import chunk_text

model = SentenceTransformer('all-MiniLM-L6-v2')
def compute_chunked_similarity(resume_text, jd_text):
    jd_chunks = chunk_text(jd_text)

    resume_vec = model.encode(resume_text, convert_to_tensor=True)

    max_score = 0

    for chunk in jd_chunks:
        chunk_vec = model.encode(chunk, convert_to_tensor=True)
        score = util.cos_sim(resume_vec, chunk_vec)

        max_score = max(max_score, float(score[0][0]))

    return max_score