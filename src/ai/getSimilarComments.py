from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
client = OpenAI()


def askAi(question):
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": question}],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
        "type": "text"
    }
    )

    return response.choices[0].message.content

def getSimilarComments(comments: list[str], newComment: str, threshold = .5):
    # Initialize the TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()
    comments.append(newComment)
    tfidf_matrix = vectorizer.fit_transform(comments)

    # Calculate pairwise cosine similarity between sentences
    cosine_similarities = cosine_similarity(tfidf_matrix)

    # Display similarity matrix
    print("Cosine Similarity Matrix:")
    print(cosine_similarities)
    # get the highest similarity items from the last row if they have a value larger than .15
    most_similar = cosine_similarities[-1][:-1].argsort()[::-1]
    # filter this to include elements with similarity > .15
    most_similar = [comments[i] for i in most_similar if cosine_similarities[-1][i] > threshold]


    answer = []
    for item in most_similar:
        explanation = askAi(f"explain shortly and to the point without any bullshit why the following two sentences are similar 1. '{item}', 2. '{comments[-1]}'")
        answer.append((item, explanation))
    
    return answer

comments = [
    "Electricity network back to 100 state ownership. Even if by force.",
    "Many statements are difficult, if not impossible, to answer with only yes or no, because reality is complicated.",
    "Family poverty with children is svetism and means a low number of families with children. It is different from the poverty of families with children.",
    "One of society's most important tasks is to ensure that companies compete with each other.",
    "Language quotas are institutional nepotism.",
    "These things should not be compared with each other",
    "Schools should have teaching peace, i.e. less extra work for teachers.",
    "The educational material of schools should be implemented on the principle of open source code.",
    "Basic income support should be replaced by basic income.",
    "The granting of dual citizenships to Russians should be stopped and those previously granted should be cancelled.",
    "caregiver's fee tax-free",
    "All NATO soldiers must also be subject to all Finnish laws, if they are in Finland. No exceptions for US citizens.",
    "The prosperity of parties and the extra-parliamentary power of labor market organizations weaken democracy as a form of government.",
    "Books must be exempted from VAT.",
    "The pension should be tax-free income.",
    "Democracy always tries to postpone solving problems until the next election.",
    "The Polis platform's real-time information about the participants' behavior can enable opinion influencing with the help of bot networks.",
    "Cheese comes on top of cold cuts",
    "Fairness to honor.",
    "Finland lacks a politically independent constitutional court.",
    "At all levels of society, we should strive to act actively against racism, simply saying I'm not a racist is not enough.",
    "Two occupational pension insurers are enough.",
    "By including dialogic skills in the school curriculum, municipal work orientation, etc.",
    "The employee must also have some rights. There are no slaves.",
    "Consumer loans are unequivocally harmful from the point of view of the national economy"
]

newComment = "The employee must also have some rights. There are no slaves."
print(getSimilarComments(comments, newComment))