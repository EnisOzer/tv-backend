import logging
from fastapi import HTTPException
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import ActivityTopicResponse, SessionIdsActivityRequest, SessionIdsTopicsRequest, VoteRequest

logger = logging.getLogger(__name__)

def get_session_ids_topics_handler(request: SessionIdsTopicsRequest):
    session_id = request.session_id

    if not session_id:
        logger.error("Session id is required")
        raise HTTPException(status_code=400, detail="Session id isn't provided.")
    
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

def get_session_ids_activity_handler(request: SessionIdsActivityRequest):
    session_id, topic_id = request.session_id, request.topic_id

    if not session_id or not topic_id:
        logger.error("Session id and topic_id needed.")
        raise HTTPException(status_code=400, detail="Session id and topic_id needed.")
    
    logger.info("Getting activity info for session id %s for topic %s.", session_id, topic_id)
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            # Fetch all comment IDs for the given topic
            cursor.execute(
                "SELECT id FROM comment WHERE topic_id = %s",
                (topic_id,)
            )
            comments = cursor.fetchall()
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

def vote_handler(request: VoteRequest):
    comment_id, session_id, vote_type = request.comment_id, request.session_id, request.vote_type
    logger.info("Session id %s is voting for commentId %s with vote type %s.", session_id, comment_id, vote_type)
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            # Check if the comment exists
            cursor.execute(
                "SELECT id FROM comment WHERE id = %s",
                (comment_id,)
            )
            comment = cursor.fetchone()
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

    return {}