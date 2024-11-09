-- DEFINITION OF DATABASE (PgSQL)


-- Create the database
CREATE DATABASE truevoice;

-- Connect to the database
\c truevoice;

-- Create schema
CREATE SCHEMA truevoice;

-- Create moderator
CREATE TABLE truevoice.moderator (
    username VARCHAR(255) PRIMARY KEY,  -- User name, can be any string, mail is not allowed
    password VARCHAR(255) NOT NULL      -- Password of user
);

-- Create Topic table
CREATE TABLE truevoice.topic (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                    -- Unique identifier for topic
    title VARCHAR(255) NOT NULL,                                      -- Topic title with a max length of 255 characters
    description TEXT,                                                 -- Description of topic
    completed BOOLEAN DEFAULT 'false',                                -- Indicates whether topic is completed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),                -- Exact timestamp when topic was created
    comment_count INT DEFAULT 0                                       -- Number of comments on that topic
);

-- Create Comment table
CREATE TABLE truevoice.comment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                         -- Unique identifier for comment
    topic_id UUID REFERENCES truevoice.topic(id) ON DELETE CASCADE,        -- Foreign key to Topic
    session_id VARCHAR(15) NOT NULL,                                       -- Session id
    content TEXT NOT NULL,                                                 -- Content of the comment
    approved BOOLEAN DEFAULT 'false',                                      -- Indicates whether comment is approved by moderator
    rejected BOOLEAN DEFAULT 'false',                                      -- Indicates whether comment is rejected by moderator
    created_at TIMESTAMP WITH TIME ZONE                                    -- Exact timestamp when comment is posted
);

-- Create an enumerated type for vote_type
CREATE TYPE vote_type_enum AS ENUM ('VOTE_UP', 'VOTE_DOWN', 'SKIPPED');

-- Create Vote table
CREATE TABLE truevoice.vote (
    comment_id UUID REFERENCES truevoice.comment(id) ON DELETE CASCADE,  -- Foreign key to Comment
    voter_id UUID NOT NULL,                                              -- Identifier for the user voting on the comment
    vote_type vote_type_enum NOT NULL,                                   -- Boolean to represent upvote/downvote (TRUE/FALSE)

    PRIMARY KEY (comment_id, voter_id)                                   -- Composite primary key to ensure each user votes only once per comment
);
