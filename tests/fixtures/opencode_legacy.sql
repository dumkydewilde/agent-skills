CREATE TABLE project (id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE session (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    directory TEXT,
    title TEXT,
    time_created INTEGER
);
CREATE TABLE message (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    time_created INTEGER,
    data TEXT
);
CREATE TABLE part (
    id TEXT PRIMARY KEY,
    message_id TEXT,
    session_id TEXT,
    time_created INTEGER,
    data TEXT
);

INSERT INTO project VALUES ('prj_synthetic_legacy', 'legacy-app');
INSERT INTO session VALUES (
    'ses_synthetic_legacy', 'prj_synthetic_legacy', '/work/legacy-app',
    'Synthetic legacy title', 1750000000000
);
INSERT INTO message VALUES (
    'msg_synthetic_legacy_user', 'ses_synthetic_legacy', 1750000000001,
    '{"role":"user","time":{"created":1750000000001}}'
);
INSERT INTO part VALUES (
    'part_synthetic_legacy_text', 'msg_synthetic_legacy_user',
    'ses_synthetic_legacy', 1750000000002,
    '{"type":"text","text":"Synthetic legacy search phrase"}'
);
INSERT INTO part VALUES (
    'part_synthetic_legacy_tool', 'msg_synthetic_legacy_user',
    'ses_synthetic_legacy', 1750000000003,
    '{"type":"tool","text":"Synthetic legacy tool data"}'
);
