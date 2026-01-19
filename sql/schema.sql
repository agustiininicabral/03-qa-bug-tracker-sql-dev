CREATE TABLE IF NOT EXISTS bug (
  bug_id        INT PRIMARY KEY,
  created_date  DATE NOT NULL,
  resolved_date DATE,
  module        TEXT NOT NULL,
  severity      TEXT NOT NULL CHECK (severity IN ('Low','Medium','High','Critical')),
  status        TEXT NOT NULL CHECK (status IN ('Open','In Progress','Blocked','Resolved','Closed')),
  reported_by   TEXT NOT NULL,
  assigned_to   TEXT NOT NULL,
  title         TEXT NOT NULL,
  description   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_bug_status ON bug(status);
CREATE INDEX IF NOT EXISTS idx_bug_severity ON bug(severity);
CREATE INDEX IF NOT EXISTS idx_bug_created ON bug(created_date);