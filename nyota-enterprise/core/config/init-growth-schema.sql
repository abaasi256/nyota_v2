-- Growth OS SEO & Content Tables
CREATE TABLE growth.keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(255) UNIQUE NOT NULL,
    search_volume INTEGER DEFAULT 0,
    difficulty INTEGER DEFAULT 0,
    current_rank INTEGER DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'DISCOVERED',
    last_crawled TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE growth.content_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword_id UUID REFERENCES growth.keywords(id),
    title VARCHAR(255) NOT NULL,
    markdown_content TEXT,
    status VARCHAR(20) DEFAULT 'DRAFTED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Growth OS Permissions Matrix
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA growth TO os_growth;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA growth TO os_growth;
