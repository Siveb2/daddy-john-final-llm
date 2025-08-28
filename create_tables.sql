-- Database initialization script for Chatbot API
-- Run this script in your Supabase SQL editor to create the required tables

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    title TEXT DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    token_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Create index on conversation_id for faster queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Create summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR NOT NULL,
    summary_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Create index on conversation_id for faster queries
CREATE INDEX IF NOT EXISTS idx_summaries_conversation_id ON summaries(conversation_id);

-- Verify tables were created
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('conversations', 'messages', 'summaries')
ORDER BY table_name, ordinal_position;
