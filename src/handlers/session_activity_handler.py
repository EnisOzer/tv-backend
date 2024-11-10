import logging
from fastapi import HTTPException
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import VoteRequest
from src.handlers.response_models import ActivityTopicResponse

logger = logging.getLogger(__name__)

def get_session_ids_topics_handler(session_id: str):
    logger.info("Getting topics that session id %s participated.", session_id)
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT c.topic_id
                FROM comment AS c
                JOIN vote AS v ON v.comment_id = c.id
                WHERE c.session_id = %s
                """,
                (session_id,)
            )
            topic_ids = [row[0] for row in cursor.fetchall()]

    return {"topics": topic_ids}

def get_session_ids_activity_handler(session_id: str, topic_id: str) -> ActivityTopicResponse:
    logger.info("Getting activity info for session id %s for topic %s.", session_id, topic_id)
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            # Fetch all comment IDs for the given topic
            cursor.execute(
                "SELECT id FROM comment WHERE topic_id = %s",
                (topic_id,)
            )
            comments = cursor.fetchall()
            if not comments:
                logger.error("No activity in session id %s for topic %s", session_id, topic_id)
                raise HTTPException(status_code=404, detail=f"No activity in session id {session_id} for topic {topic_id}")
            
            comment_ids_all = [row[0] for row in comments]

            # Fetch user votes for the comments related to the topic
            cursor.execute(
                """
                SELECT v.comment_id, v.vote_type
                FROM vote AS v
                WHERE v.voter_id = %s AND v.comment_id IN %s
                """,
                (session_id, tuple(comment_ids_all))
            )
            user_voted_comments = {row[0]: row[1] for row in cursor.fetchall()}

            # Separate the votes into categories
            comment_ids_up_voted = [comment_id for comment_id, vote_type in user_voted_comments.items() if vote_type == 'VOTE_UP']
            comment_ids_down_voted = [comment_id for comment_id, vote_type in user_voted_comments.items() if vote_type == 'VOTE_DOWN']
            comment_ids_skipped = [comment_id for comment_id, vote_type in user_voted_comments.items() if vote_type == 'SKIPPED']

    return ActivityTopicResponse(
        session_id=session_id,
        topic_id=topic_id,
        commentIDsUpVoted=comment_ids_up_voted,
        commentIDsDownVoted=comment_ids_down_voted,
        commentIDsSkipped=comment_ids_skipped,
    )

def vote_handler(request: VoteRequest) -> ActivityTopicResponse:
    comment_id, session_id, vote_type = request.comment_id, request.session_id, request.vote_type
    logger.info("Session id %s is voting for commentId %s with vote type %s.", session_id, comment_id, vote_type)
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            # Check if the comment exists
            cursor.execute(
                "SELECT id, topic_id FROM comment WHERE id = %s",
                (comment_id,)
            )
            result = cursor.fetchone()

            if not result:
                logger.error("Comment with id %s is not found", comment_id)
                raise HTTPException(status_code=404, detail="Comment not found.")
            
            comment = result[0]
            topic_id = result[1]

            if not comment:
                logger.error("Comment with id %s is not found", comment_id)
                raise HTTPException(status_code=404, detail="Comment not found.")

            # Check if the user already voted on this comment
            cursor.execute(
                "SELECT vote_type FROM vote WHERE comment_id = %s AND voter_id = %s",
                (comment_id, session_id)
            )
            existing_vote = cursor.fetchone()
            if existing_vote:
                # Update the vote if it already exists
                cursor.execute(
                    "UPDATE vote SET vote_type = %s WHERE comment_id = %s AND voter_id = %s",
                    (vote_type, comment_id, session_id)
                )
            else:
                # Insert a new vote if it doesn't exist
                cursor.execute(
                    "INSERT INTO vote (comment_id, voter_id, vote_type) VALUES (%s, %s, %s)",
                    (comment_id, session_id, vote_type)
                )
            connection.commit()

    return get_session_ids_activity_handler(SessionIdsActivityRequest(session_id=session_id, topic_id=topic_id))