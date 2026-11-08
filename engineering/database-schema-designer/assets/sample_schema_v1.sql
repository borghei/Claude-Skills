-- Version 1 of a small multi-tenant task tracker (PostgreSQL).
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    email VARCHAR(320) NOT NULL UNIQUE,
    display_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_organization_id ON users (organization_id);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id),
    assignee_id UUID REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tasks_organization_id ON tasks (organization_id);
CREATE INDEX idx_tasks_assignee_id ON tasks (assignee_id);
