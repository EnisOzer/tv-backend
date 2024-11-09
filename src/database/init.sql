-- DEFINITION OF DATABASE (PgSQL)


-- Create the database
CREATE DATABASE truevoice;

-- Connect to the database
\c truevoice;

-- Create schema
CREATE SCHEMA truevoice;

-- Create Topic table
CREATE TABLE truevoice.topic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),      -- Unique identifier for topic
    name VARCHAR(255) NOT NULL,                         -- Topic name with a max length of 255 characters
    description TEXT,                                   -- Description of topic
    created_at TIMESTAMP WITH TIME ZONE,                -- Exact timestamp when topic was created
    moderator_email VARCHAR(255)                        -- Moderator username who created this topic
);

-- Create Comment table
CREATE TABLE truevoice.comment (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                 -- Unique identifier for comment
    topic_id UUID REFERENCES truevoice.topic(id) ON DELETE CASCADE,  -- Foreign key to Topic
    user_session_id VARCHAR(15) NOT NULL,                                  -- Session id
    content TEXT NOT NULL,                                                 -- Content of the comment
    approved BOOLEAN DEFAULT 'false',                                      -- Indicates whether comment is approved by moderator
    rejected BOOLEAN DEFAULT 'false',                                      -- Indicates whether comment is rejected by moderator
    created_at TIMESTAMP WITH TIME ZONE                      -- Exact timestamp when comment is posted
);

-- Create Vote table
CREATE TABLE truevoice.vote (
    comment_id UUID REFERENCES truevoice.comment(comment_id) ON DELETE CASCADE,  -- Foreign key to Comment
    voter_id UUID NOT NULL,                    -- Identifier for the user voting on the comment
    voted_up BOOLEAN NOT NULL,                     -- Boolean to represent upvote/downvote (TRUE/FALSE)

    PRIMARY KEY (comment_id, voter_id)         -- Composite primary key to ensure each user votes only once per comment
);
