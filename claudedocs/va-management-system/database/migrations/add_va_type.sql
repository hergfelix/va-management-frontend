-- ============================================
-- Migration: Add VA Type System
-- Date: 2025-10-24
-- ============================================

-- Add va_type column to vas table
-- Types: 'social_media' (default), 'editor', 'manager', 'specialist'
ALTER TABLE vas
ADD COLUMN IF NOT EXISTS va_type VARCHAR(50) DEFAULT 'social_media' NOT NULL;

-- Add custom_salary column for non-social-media VAs
-- When va_type != 'social_media', this overrides the monthly_base_salary payment stages
ALTER TABLE vas
ADD COLUMN IF NOT EXISTS custom_salary DECIMAL(10,2);

-- Update existing VAs to social_media type
UPDATE vas
SET va_type = 'social_media'
WHERE va_type IS NULL OR va_type = '';

-- Create index for faster filtering by type
CREATE INDEX IF NOT EXISTS idx_vas_type ON vas(va_type);

-- Add comments for documentation
COMMENT ON COLUMN vas.va_type IS 'Type of VA: social_media (3-stage progression), editor, manager, specialist (fixed salary)';
COMMENT ON COLUMN vas.custom_salary IS 'Custom fixed salary for non-social-media VAs. Overrides payment stages when va_type != social_media';
