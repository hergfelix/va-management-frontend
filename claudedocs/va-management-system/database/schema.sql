-- ============================================
-- VA Management System - Database Schema
-- ============================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS monthly_payments CASCADE;
DROP TABLE IF EXISTS tiktok_accounts CASCADE;
DROP TABLE IF EXISTS creators CASCADE;
DROP TABLE IF EXISTS phones CASCADE;
DROP TABLE IF EXISTS vas CASCADE;
DROP TABLE IF EXISTS payment_groups CASCADE;

-- Payment Groups (Families/Friends)
CREATE TABLE payment_groups (
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL,
    leader_name VARCHAR(255) NOT NULL,
    leader_telegram VARCHAR(100),
    wallet_address VARCHAR(100) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'USDT',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- VAs (Employees)
CREATE TABLE vas (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    telegram_handle VARCHAR(100) NOT NULL,
    profile_photo_url VARCHAR(500),
    wallet_address VARCHAR(100),
    payment_group_id INTEGER REFERENCES payment_groups(id),
    monthly_base_salary DECIMAL(10,2) NOT NULL DEFAULT 500.00,
    va_type VARCHAR(50) NOT NULL DEFAULT 'social_media',  -- Types: social_media, editor, manager, specialist
    custom_salary DECIMAL(10,2),  -- Fixed salary for non-social-media VAs
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    onboarding_date DATE DEFAULT CURRENT_DATE,
    replacement_date DATE,
    replacement_reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phones (with Apple ID + Proxy)
CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(50),
    apple_id_email VARCHAR(255) NOT NULL,
    apple_id_password VARCHAR(255) NOT NULL,
    proxy_ip VARCHAR(50) NOT NULL,
    proxy_port INTEGER NOT NULL,
    proxy_username VARCHAR(100),
    proxy_password VARCHAR(255),
    assigned_to_va_id INTEGER REFERENCES vas(id),
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creators (Managed by VAs)
CREATE TABLE creators (
    id SERIAL PRIMARY KEY,
    creator_name VARCHAR(255) NOT NULL,
    niche VARCHAR(100),
    assigned_to_va_id INTEGER REFERENCES vas(id),
    social_media_channel_link VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TikTok Accounts (5 per Creator)
CREATE TABLE tiktok_accounts (
    id SERIAL PRIMARY KEY,
    creator_id INTEGER REFERENCES creators(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    login_email VARCHAR(255),
    login_password VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monthly Payments (Individual VA payments)
CREATE TABLE monthly_payments (
    id SERIAL PRIMARY KEY,
    va_id INTEGER REFERENCES vas(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL,
    base_salary DECIMAL(10,2) NOT NULL,
    bonus_amount DECIMAL(10,2) DEFAULT 0.00,
    penalty_amount DECIMAL(10,2) DEFAULT 0.00,
    bonus_reason TEXT,
    penalty_reason TEXT,
    total_amount DECIMAL(10,2) GENERATED ALWAYS AS (base_salary + bonus_amount - penalty_amount) STORED,
    paid BOOLEAN DEFAULT FALSE,
    payment_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(va_id, month)
);

-- Indexes for performance
CREATE INDEX idx_vas_status ON vas(status);
CREATE INDEX idx_vas_payment_group ON vas(payment_group_id);
CREATE INDEX idx_phones_assigned_va ON phones(assigned_to_va_id);
CREATE INDEX idx_creators_assigned_va ON creators(assigned_to_va_id);
CREATE INDEX idx_monthly_payments_month ON monthly_payments(month);
CREATE INDEX idx_monthly_payments_paid ON monthly_payments(paid);

-- Creator Cost Analysis View (for ROI tracking)
CREATE VIEW creator_monthly_costs AS
SELECT
    c.id AS creator_id,
    c.creator_name,
    c.niche,
    mp.month,
    v.full_name AS va_name,
    mp.total_amount AS va_cost,
    mp.paid
FROM creators c
JOIN vas v ON c.assigned_to_va_id = v.id
LEFT JOIN monthly_payments mp ON v.id = mp.va_id
WHERE v.status = 'active'
ORDER BY mp.month DESC, c.creator_name;
