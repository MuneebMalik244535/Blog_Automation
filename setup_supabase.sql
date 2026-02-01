-- Create blogs table for the blog generation API
CREATE TABLE IF NOT EXISTS blogs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add RLS (Row Level Security) policies
ALTER TABLE blogs ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read blogs
CREATE POLICY "Enable read access for all users" ON blogs
    FOR SELECT USING (true);

-- Allow anyone to insert blogs
CREATE POLICY "Enable insert access for all users" ON blogs
    FOR INSERT WITH CHECK (true);

-- Allow anyone to update their own blogs
CREATE POLICY "Enable update access for all users" ON blogs
    FOR UPDATE USING (true);

-- Allow anyone to delete their own blogs
CREATE POLICY "Enable delete access for all users" ON blogs
    FOR DELETE USING (true);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_blogs_created_at ON blogs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blogs_title ON blogs USING gin(to_tsvector('english', title));
