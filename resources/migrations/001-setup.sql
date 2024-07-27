CREATE TABLE IF NOT EXISTS telemetry (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    created_at TIMESTAMP without time zone DEFAULT now(),
    updated_at TIMESTAMP without time zone,
    source TEXT NOT NULL,
    timestamp TIMESTAMP without time zone NOT NULL,
    data JSONB NOT NULL,
    PRIMARY KEY(source, timestamp)
);