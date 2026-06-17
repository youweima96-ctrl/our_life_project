CREATE TABLE users (
  id VARCHAR PRIMARY KEY,
  nickname VARCHAR,
  avatar_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rooms (
  id VARCHAR PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  room_type VARCHAR(20) NOT NULL CHECK (room_type IN ('couple', 'friend', 'custom')),
  owner_user_id VARCHAR NOT NULL REFERENCES users(id),
  invite_code VARCHAR(16) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE room_members (
  room_id VARCHAR NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
  user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL DEFAULT 'member',
  joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (room_id, user_id)
);

CREATE TABLE ai_extractions (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR NOT NULL REFERENCES users(id),
  event_id VARCHAR,
  raw_content_hash VARCHAR(64) NOT NULL,
  prompt_version VARCHAR(80) NOT NULL,
  model_name VARCHAR(80) NOT NULL,
  output_json JSONB NOT NULL,
  user_action VARCHAR(20) NOT NULL DEFAULT 'pending',
  accuracy_feedback VARCHAR(20),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE life_events (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR NOT NULL REFERENCES users(id),
  room_id VARCHAR REFERENCES rooms(id),
  raw_content TEXT NOT NULL,
  event_type VARCHAR(40) NOT NULL,
  title VARCHAR(160) NOT NULL,
  summary TEXT NOT NULL,
  topic_tags JSONB NOT NULL DEFAULT '[]',
  emotion_tags JSONB NOT NULL DEFAULT '[]',
  need_tags JSONB NOT NULL DEFAULT '[]',
  visibility VARCHAR(20) NOT NULL CHECK (visibility IN ('private', 'summary_only', 'room_visible')),
  event_time TIMESTAMPTZ NOT NULL,
  review_status VARCHAR(20) NOT NULL DEFAULT 'unreviewed',
  source_type VARCHAR(20) NOT NULL DEFAULT 'text',
  ai_extraction_id VARCHAR REFERENCES ai_extractions(id),
  confirmed BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE ai_extractions
  ADD CONSTRAINT ai_extractions_event_id_fkey FOREIGN KEY (event_id) REFERENCES life_events(id);

CREATE INDEX idx_life_events_user_time ON life_events(user_id, event_time DESC);
CREATE INDEX idx_life_events_room_time ON life_events(room_id, event_time DESC);
CREATE INDEX idx_life_events_visibility ON life_events(visibility);

CREATE TABLE conflict_reviews (
  id VARCHAR PRIMARY KEY,
  event_id VARCHAR NOT NULL REFERENCES life_events(id),
  room_id VARCHAR REFERENCES rooms(id),
  creator_id VARCHAR NOT NULL REFERENCES users(id),
  user_view TEXT NOT NULL,
  partner_view TEXT,
  ai_review_json JSONB,
  status VARCHAR(30) NOT NULL DEFAULT 'draft',
  visibility VARCHAR(20) NOT NULL DEFAULT 'private',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE shared_decisions (
  id VARCHAR PRIMARY KEY,
  room_id VARCHAR NOT NULL REFERENCES rooms(id),
  source_event_id VARCHAR REFERENCES life_events(id),
  title VARCHAR(160) NOT NULL,
  content TEXT NOT NULL,
  owner_user_id VARCHAR REFERENCES users(id),
  due_date DATE,
  status VARCHAR(20) NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE reports (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR NOT NULL REFERENCES users(id),
  room_id VARCHAR REFERENCES rooms(id),
  report_type VARCHAR(40) NOT NULL,
  content_markdown TEXT NOT NULL,
  source_event_ids JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ai_call_logs (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR REFERENCES users(id),
  purpose VARCHAR(80) NOT NULL,
  prompt_version VARCHAR(80) NOT NULL,
  model_name VARCHAR(80) NOT NULL,
  input_hash VARCHAR(64) NOT NULL,
  output_json JSONB,
  status VARCHAR(20) NOT NULL,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

