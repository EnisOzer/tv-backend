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

def checkHatefulComment(comment: str):
    answer = askAi(f"Is the following comment hateful? Only answer with 'yes' or 'no'. {comment}'").lower()
    return answer == "yes" 

class Comment:
    def __init__(self, comment: str, upvotes: int, downvotes: int, date: str):
        self.comment = comment
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.date = date

def getTopComments(comments: list[Comment]): 
    sampleSize = 0.1 * len(comments) if len(comments) > 10 else len(comments)
    # sort comments by the number of upvotes (high upvotes first)
    upvotesComments = sorted(comments, key=lambda x: x.upvotes, reverse=True)
    
    # sort comments by the number of total votes (upvotes + downvotes)
    votesComments = sorted(comments, key=lambda x: x.upvotes + x.downvotes, reverse=True)
    
    # sort comments based on recency
    dateSortedComments = sorted(comments, key=lambda x: x.date, reverse=True)
    
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

def summariseComments(comments: list[Comment]):
    # making a numbered list out of the comments
    comments = getTopComments(comments)
    comments = "\n".join([f"{i+1}. {comment}" for i, comment in enumerate(comments)])
    return askAi(f"Summarise the following comments really well and concisly in a setnce, showing if there are different schools of thoughts (or different patterns): {comments}")

# comments = [
#     "Electricity network back to 100 state ownership. Even if by force.",
#     "Many statements are difficult, if not impossible, to answer with only yes or no, because reality is complicated.",
#     "Family poverty with children is svetism and means a low number of families with children. It is different from the poverty of families with children.",
#     "One of society's most important tasks is to ensure that companies compete with each other.",
#     "Language quotas are institutional nepotism.",
#     "These things should not be compared with each other",
#     "Schools should have teaching peace, i.e. less extra work for teachers.",
#     "The educational material of schools should be implemented on the principle of open source code.",
#     "Basic income support should be replaced by basic income.",
#     "The granting of dual citizenships to Russians should be stopped and those previously granted should be cancelled.",
#     "caregiver's fee tax-free",
#     "All NATO soldiers must also be subject to all Finnish laws, if they are in Finland. No exceptions for US citizens.",
#     "The prosperity of parties and the extra-parliamentary power of labor market organizations weaken democracy as a form of government.",
#     "Books must be exempted from VAT.",
#     "The pension should be tax-free income.",
#     "Democracy always tries to postpone solving problems until the next election.",
#     "The Polis platform's real-time information about the participants' behavior can enable opinion influencing with the help of bot networks.",
#     "Cheese comes on top of cold cuts",
#     "Fairness to honor.",
#     "Finland lacks a politically independent constitutional court.",
#     "At all levels of society, we should strive to act actively against racism, simply saying I'm not a racist is not enough.",
#     "Two occupational pension insurers are enough.",
#     "By including dialogic skills in the school curriculum, municipal work orientation, etc.",
#     "The employee must also have some rights. There are no slaves.",
#     "Consumer loans are unequivocally harmful from the point of view of the national economy"
# ]


# commentObjectList = [
#     Comment("Electricity network back to 100 state ownership. Even if by force.", 10, 2, "2022-01-01"),
#     Comment("Many statements are difficult, if not impossible, to answer with only yes or no, because reality is complicated.", 5, 1, "2022-01-02"),
#     Comment("Family poverty with children is svetism and means a low number of families with children. It is different from the poverty of families with children.", 3, 0, "2022-01-03"),
#     Comment("One of society's most important tasks is to ensure that companies compete with each other.", 7, 3, "2022-01-04"),
#     Comment("Language quotas are institutional nepotism.", 8, 4, "2022-01-05"),
#     Comment("These things should not be compared with each other", 2, 1, "2022-01-06"),
#     Comment("Schools should have teaching peace, i.e. less extra work for teachers.", 6, 2, "2022-01-07"),
#     Comment("The educational material of schools should be implemented on the principle of open source code.", 4, 1, "2022-01-08"),
#     Comment("Basic income support should be replaced by basic income.", 9, 3, "2022-01-09"),
#     Comment("The granting of dual citizenships to Russians should be stopped and those previously granted should be cancelled.", 10, 4, "2022-01-10"),
#     Comment("caregiver's fee tax-free", 5, 2, "2022-01-11"),
#     Comment("All NATO soldiers must also be subject to all Finnish laws, if they are in Finland. No exceptions for US citizens.", 7, 3, "2022-01-12"),
#     Comment("The prosperity of parties and the extra-parliamentary power of labor market organizations weaken democracy as a form of government.", 8, 4, "2022-01-13"),
#     Comment("Books must be exempted from VAT.", 6, 2, "2022-01-14"),
#     Comment("The pension should be tax-free income.", 9, 3, "2022-01-15"),
#     Comment("Democracy always tries to postpone solving problems until the next election.", 10, 4, "2022-01-16"),
#     Comment("The Polis platform's real-time information about the participants' behavior can enable opinion influencing with the help of bot networks.", 5, 2, "2022-01-17"),
#     Comment("Cheese comes on top of cold cuts", 7, 3, "2022-01-18"),
#     Comment("Fairness to honor.", 8, 4, "2022-01-19"),
#     Comment("Finland lacks a politically independent constitutional court.", 6, 2, "2022-01-20"),
#     Comment("At all levels of society, we should strive to act actively against racism, simply saying I'm not a racist is not enough.", 9, 3, "2022-01-21"),
#     Comment("Two occupational pension insurers are enough.", 10, 4, "2022-01-22"),
#     Comment("By including dialogic skills in the school curriculum, municipal work orientation, etc.", 5, 2, "2022-01-23"),
#     Comment("The employee must also have some rights. There are no slaves.", 7, 3, "2022-01-24"),
#     Comment("Consumer loans are unequivocally harmful from the point of view of the national economy", 8, 4, "2022-01-25")
# ]


# newComment = "The employee must also have some rights. There are no slaves."
# print(getSimilarComments(comments, newComment))
# topComments = getTopComments(commentObjectList)
# print (summariseComments(commentObjectList))