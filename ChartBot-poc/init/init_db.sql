-- 1️⃣ Users Table
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    lan_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2️⃣ Projects Table
CREATE TABLE Projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3️⃣ AdGroups Table
CREATE TABLE AdGroups (
    adgroup_id SERIAL PRIMARY KEY,
    adgroup_name VARCHAR(255) NOT NULL,
    project_id INT NOT NULL,
    approver_emails TEXT, -- 'john@abc.com,alex@abc.com,meena@abc.com'
    approver_lanids TEXT,  -- 'johan41,alexdo8,meenaol89'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
);

-- 4️⃣ UserProjectAssignment Table
CREATE TABLE UserProjectAssignment (
    assignment_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    project_id INT NOT NULL,
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (project_id) REFERENCES Projects(project_id)
);

-- 5️⃣ UserAdGroupAccess Table
CREATE TABLE UserAdGroupAccess (
    user_id INT NOT NULL,
    adgroup_id INT NOT NULL,
    access_granted BOOLEAN DEFAULT TRUE,
    grant_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoke_date TIMESTAMP NULL,
    PRIMARY KEY (user_id, adgroup_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (adgroup_id) REFERENCES AdGroups(adgroup_id)
);

-- 6️⃣ AdGroupAccessRequests Table
-- Note: Using VARCHAR instead of ENUM for PostgreSQL compatibility
CREATE TABLE AdGroupAccessRequests (
    request_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    adgroup_id INT NOT NULL,
    request_type VARCHAR(20) NOT NULL CHECK (request_type IN ('grant', 'revoke')),
    request_source VARCHAR(20) DEFAULT 'chatbot' CHECK (request_source IN ('chatbot', 'bappas', 'admin')),
    request_status VARCHAR(20) DEFAULT 'pending' CHECK (request_status IN ('pending', 'approved', 'rejected', 'cancelled')),
    approver_lanid VARCHAR(50),
    approver_email VARCHAR(255),
    requester_lanid VARCHAR(50),
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decision_date TIMESTAMP NULL,
    comments TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (adgroup_id) REFERENCES AdGroups(adgroup_id)
);

-- 7️⃣ AccessHistory Table
-- Note: Using VARCHAR instead of ENUM for PostgreSQL compatibility
CREATE TABLE AccessHistory (
    history_id SERIAL PRIMARY KEY,
    user_id INT,
    adgroup_id INT,
    action VARCHAR(20) NOT NULL CHECK (action IN ('grant', 'revoke', 'request', 'approval')),
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_by VARCHAR(50), -- LAN ID or system
    comments TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (adgroup_id) REFERENCES AdGroups(adgroup_id)
);

-- 8️⃣ SystemApprovers Table
-- Note: Using VARCHAR instead of ENUM for PostgreSQL compatibility
CREATE TABLE SystemApprovers (
    approver_id SERIAL PRIMARY KEY,
    lan_id VARCHAR(50) UNIQUE,
    full_name VARCHAR(255),
    email VARCHAR(255),
    role VARCHAR(20) DEFAULT 'approver' CHECK (role IN ('approver', 'admin', 'hr')),
    is_active BOOLEAN DEFAULT TRUE
);

-- 9️⃣ NotificationQueue Table
-- Note: Using VARCHAR instead of ENUM for PostgreSQL compatibility
CREATE TABLE NotificationQueue (
    notification_id SERIAL PRIMARY KEY,
    recipient_email VARCHAR(255),
    recipient_lanid VARCHAR(50),
    message_title VARCHAR(255),
    message_body TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL
);

-- Insert sample data into Users table
INSERT INTO Users (full_name, first_name, last_name, lan_id, email, is_active) VALUES
('Sanjyot Dharankar', 'Sanjyot', 'Dharankar', 'sdharan1', 'sanjyot@example.com', TRUE),
('Aditi Gupta', 'Aditi', 'Gupta', 'agupta2', 'aditi@example.com', TRUE),
('System Admin', 'System', 'Admin', 'admin1', 'admin@example.com', TRUE),
('HR Manager', 'HR', 'Manager', 'hr1', 'hr@example.com', TRUE);

-- Insert sample data into Projects table
INSERT INTO Projects (project_name, description, is_active) VALUES
('Project Alpha', 'A project focused on AI research.', TRUE),
('Project Beta', 'A project focused on cloud infrastructure.', TRUE),
('DET', 'Data Engineering Team', TRUE),
('CART', 'Cart Analysis Project', TRUE),
('OAP', 'Order Analytics Platform', TRUE),
('PMBA', 'Product Management Business Analytics', TRUE),
('EO', 'E-commerce Operations', TRUE);

-- Insert sample data into AdGroups table
INSERT INTO AdGroups (adgroup_name, project_id, approver_emails, approver_lanids, is_active) VALUES
('AI Research Group', 1, 'john@abc.com,alex@abc.com,meena@abc.com', 'johan41,alexdo8,meenaol89', TRUE),
('Cloud Dev Team', 2, 'alice@xyz.com,paul@xyz.com', 'alicep7,paulb23', TRUE),
('DET_Developers', 3, 'det-manager@example.com', 'manager1', TRUE),
('DET_Admins', 3, 'det-admin@example.com', 'admin1', TRUE),
('CART_Analysts', 4, 'cart-lead@example.com', 'lead1', TRUE),
('OAP_Users', 5, 'oap-admin@example.com', 'admin2', TRUE),
('PMBA_Access', 6, 'pmba-manager@example.com', 'manager2', TRUE),
('EO_Team', 7, 'eo-director@example.com', 'director1', TRUE);

-- Insert sample data into SystemApprovers table
INSERT INTO SystemApprovers (lan_id, full_name, email, role, is_active) VALUES
('admin1', 'System Administrator', 'admin@example.com', 'admin', TRUE),
('hr1', 'HR Manager', 'hr@example.com', 'hr', TRUE),
('manager1', 'Project Manager One', 'manager1@example.com', 'approver', TRUE),
('manager2', 'Project Manager Two', 'manager2@example.com', 'approver', TRUE);

-- Create indexes for better performance
CREATE INDEX idx_user_project_assignment_user_id ON UserProjectAssignment(user_id);
CREATE INDEX idx_user_project_assignment_project_id ON UserProjectAssignment(project_id);
CREATE INDEX idx_user_ad_group_access_user_id ON UserAdGroupAccess(user_id);
CREATE INDEX idx_user_ad_group_access_adgroup_id ON UserAdGroupAccess(adgroup_id);
CREATE INDEX idx_ad_group_access_requests_user_id ON AdGroupAccessRequests(user_id);
CREATE INDEX idx_ad_group_access_requests_status ON AdGroupAccessRequests(request_status);
CREATE INDEX idx_access_history_user_id ON AccessHistory(user_id);
CREATE INDEX idx_access_history_action_date ON AccessHistory(action_date);
CREATE INDEX idx_notification_queue_status ON NotificationQueue(status);