-- DEFINITION OF DATABASE (PgSQL)


-- Create the database
CREATE DATABASE truevoice;

-- Connect to the database
\c truevoice;

-- Create schema
CREATE SCHEMA truevoice;

-- There are 2 roles of user in a system, standard and moderator
CREATE TYPE user_role AS ENUM ('standard', 'moderator');


-- Crate user
-- User is used only to save history of activities if user wants to have that feature
CREATE TABLE truevoice.user (
    username VARCHAR(255) PRIMARY KEY,     -- User name, can be any string, mail is not allowed
    role user_role DEFAULT 'standard',  -- Role of user
    password VARCHAR(255) NOT NULL      -- Password of user
);

-- Create Topic table
CREATE TABLE truevoice.topic (
    topic_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  -- Unique identifier for topic
    topic_name VARCHAR(255) NOT NULL                      -- Topic name with a max length of 255 characters
);

-- Create Comment table
CREATE TABLE truevoice.comment (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),                 -- Unique identifier for comment
    topic_id UUID REFERENCES truevoice.topic(topic_id) ON DELETE CASCADE,  -- Foreign key to Topic
    user_id VARCHAR(255) REFERENCES truevoice.user(username) ON DELETE SET NULL,  -- Foreign key to Topic
    content TEXT NOT NULL,                                                 -- Content of the comment
    approved BOOLEAN DEFAULT 'false',                                      -- Indicates whether comment is approved by moderator
    rejected BOOLEAN DEFAULT 'false'                                       -- Indicates whether comment is rejected by moderator
);

-- Create Vote table
CREATE TABLE truevoice.vote (
    comment_id UUID REFERENCES truevoice.comment(comment_id) ON DELETE CASCADE,  -- Foreign key to Comment
    voter_id UUID NOT NULL,                    -- Identifier for the user voting on the comment
    voted_up BOOLEAN NOT NULL,                     -- Boolean to represent upvote/downvote (TRUE/FALSE)

    PRIMARY KEY (comment_id, voter_id)         -- Composite primary key to ensure each user votes only once per comment
);
