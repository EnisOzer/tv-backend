from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

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

def getSimilarComments(comments: list[str], newComment: str, threshold = .15):
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

def checkHatefulComment(comment: str):
    answer = askAi(f"Is the following comment hateful? Only answer with 'yes' or 'no'. {comment}'").lower()
    assert(answer in ["yes", "no"])
    return answer == "yes" 

class Comment:
    def __init__(self, comment_id: str, comment: str, topic_id: str, session_id: str, up_votes: int, down_votes: int, skipped_times: int, timestamp: str):
        self.comment_id = comment_id
        self.comment = comment
        self.up_votes = up_votes
        self.down_votes = down_votes
        self.timestamp = timestamp
        self.topic_id = topic_id
        self.session_id = session_id

def _getTopComments(comments: list[Comment]): 
    sampleSize = 0.1 * len(comments) if len(comments) > 10 else len(comments)
    # sort comments by the number of upvotes (high upvotes first)
    upvotesComments = sorted(comments, key=lambda x: x.up_votes, reverse=True)
    
    # sort comments by the number of total votes (up_votes + down_votes)
    votesComments = sorted(comments, key=lambda x: x.up_votes + x.down_votes, reverse=True)
    
    # sort comments based on recency
    dateSortedComments = sorted(comments, key=lambda x: x.timestamp, reverse=True)
    
    # while the answer size is less than the sample size, keep adding comments (by taking the next top comment from each list)
    comments = []
    i = 0
    while len(comments) < sampleSize:
        if i < len(votesComments):
            comments.append(upvotesComments[i].comment)
        if i < len(votesComments) and len(comments) < sampleSize:
            comments.append(votesComments[i].comment)
        if i < len(dateSortedComments) and len(comments) < sampleSize:
            comments.append(dateSortedComments[i].comment)
        i += 1

    return comments

def summariseTopComments(comments: list[Comment]):
    # making a numbered list out of the comments
    comments = _getTopComments(comments)
    comments = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(comments)])
    return askAi(f"Summarise the following comments really well and concisly in a setnce, showing if there are different schools of thoughts (or different patterns): {comments}")


def _optimal_k_silhouette(tfidf_matrix, max_k=10):
    silhouette_scores = []
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=0)
        labels = kmeans.fit_predict(tfidf_matrix)
        score = silhouette_score(tfidf_matrix, labels)
        silhouette_scores.append((k, score))

    # Find the k with the highest silhouette score
    k_opt, _ = max(silhouette_scores, key=lambda x: x[1])
    return k_opt

def clusterComments(comments: list[Comment]):
    # Step 1: Convert comments to TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words='english')  # 'english' stop words to ignore common words
    tfidf_matrix = vectorizer.fit_transform(comments)

    # Step 2: Define the number of clusters (k) - adjust based on data
    # k = _optimal_k_silhouette(tfidf_matrix, max_k = len(comments))
    k = 2

    # Step 3: Apply K-means clustering
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans.fit(tfidf_matrix)
    labels = kmeans.labels_

    # Step 4: Organize comments by cluster
    clusters = {}
    for comment, label in zip(comments, labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(comment)

    clusters = [cluster for cluster in clusters.values()]

    return clusters

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


commentObjectList = [
    Comment("887d46cb-1d43-4326-9e05-26a79500e24a", "Electricity network back to 100 state ownership. Even if by force.", "1", "1", 10, 2, 0, "2022-01-01"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24b", "Many statements are difficult, if not impossible, to answer with only yes or no, because reality is complicated.", "1", "1", 5, 1, 0, "2022-01-02"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24c", "Family poverty with children is svetism and means a low number of families with children. It is different from the poverty of families with children.", "1", "1", 7, 3, 0, "2022-01-03"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24d", "One of society's most important tasks is to ensure that companies compete with each other.", "1", "1", 8, 4, 0, "2022-01-04"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24e", "Language quotas are institutional nepotism.", "1", "1", 9, 5, 0, "2022-01-05"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24f", "These things should not be compared with each other", "1", "1", 6, 2, 0, "2022-01-06"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24g", "Schools should have teaching peace, i.e. less extra work for teachers.", "1", "1", 7, 3, 0, "2022-01-07"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24h", "The educational material of schools should be implemented on the principle of open source code.", "1", "1", 8, 4, 0, "2022-01-08"),
    Comment("887d46cb-1d43-4326-9e05-26a79500e24j", "Basic income support should be replaced by basic income.", "1", "1", 9, 5, 0, "2022-01-09"),
]

clusterComments(comments)

# newComment = "The employee must also have some rights. There are no slaves."
# print(getSimilarComments(comments, newComment))
# topComments = _getTopComments(commentObjectList)
# print (summariseTopComments(commentObjectList))