-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    lan_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AD Groups Table
CREATE TABLE IF NOT EXISTS ad_groups (
    ad_group_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    ad_group_name VARCHAR(200) NOT NULL,
    approver_email VARCHAR(100),
    approver_lan_id VARCHAR(50) NOT NULL,
    is_access_group BOOLEAN DEFAULT TRUE,
    UNIQUE(project_id, ad_group_name)
);

-- SCD Access Table
CREATE TABLE IF NOT EXISTS user_project_access (
    access_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    project_id INTEGER REFERENCES projects(project_id),
    access_type VARCHAR(20) CHECK (access_type IN ('GRANTED', 'REQUESTED', 'REVOKED')),
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP,
    requested_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    action_type VARCHAR(50),
    user_lan_id VARCHAR(50),
    project_code VARCHAR(50),
    ad_groups TEXT,
    performed_by VARCHAR(100),
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20)
);

-- Insert sample data
INSERT INTO projects (project_name, description) VALUES 
('det', 'Data Engineering Team'),
('cart', 'Cart Analysis Project'),
('oap', 'Operations Analytics Platform'),
('pmba', 'Project Management Business Analytics'),
('eo', 'Executive Operations');

INSERT INTO ad_groups (project_id, ad_group_name, approver_email, approver_lan_id) VALUES 
(1, 'det_developers', 'det_lead@company.com', 'detlead1'),
(1, 'det_admins', 'det_admin@company.com', 'detadmin1'),
(2, 'cart_users', 'cart_lead@company.com', 'cartlead1'),
(3, 'oap_analysts', 'oap_lead@company.com', 'oaplead1'),
(4, 'pmba_access', 'pmba_lead@company.com', 'pmbalead1');