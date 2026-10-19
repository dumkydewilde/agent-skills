CREATE TABLE project (id TEXT PRIMARY KEY, name TEXT);
CREATE TABLE session_v2 (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    directory TEXT,
    title TEXT,
    time_created INTEGER
);
CREATE TABLE session_message (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    type TEXT,
    seq INTEGER,
    time_created INTEGER,
    data TEXT
);

INSERT INTO project VALUES ('prj_synthetic', 'sample-app');
INSERT INTO session_v2 VALUES (
    'ses_synthetic_v2', 'prj_synthetic', '/work/sample-app',
    'Synthetic session title', 1760000000000
);
INSERT INTO session_message VALUES (
    'msg_synthetic_user', 'ses_synthetic_v2', 'user', 1, 1760000000001,
    '{"text":"Synthetic sunflower lookup phrase","time":{"created":1760000000001}}'
);
INSERT INTO session_message VALUES (
    'msg_synthetic_assistant', 'ses_synthetic_v2', 'assistant', 2, 1760000000002,
    '{"content":[{"type":"text","text":"Synthetic assistant answer"},{"type":"reasoning","text":"Synthetic hidden reasoning"},{"type":"tool","state":{"output":"Synthetic tool output"}}],"time":{"created":1760000000002}}'
);
