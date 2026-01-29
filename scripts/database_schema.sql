-- PA6.4 資料庫 Schema
-- 自動生成於: 2026-01-29
-- 使用說明: 在空白資料庫中執行此腳本以建立所有資料表

-- ============================================================================
-- 設定
-- ============================================================================

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- ============================================================================
-- 建立資料表
-- ============================================================================

-- sys_profiles

CREATE TABLE sys_profiles (
	id INTEGER DEFAULT 1 NOT NULL, 
	is_service BOOLEAN DEFAULT true NOT NULL, 
	sys_url VARCHAR(200) NOT NULL, 
	sys_ctitle VARCHAR(200) NOT NULL, 
	sys_etitle VARCHAR(200) NOT NULL, 
	sys_ccopyright VARCHAR(200) NOT NULL, 
	sys_ecopyright VARCHAR(200) NOT NULL, 
	sys_organization INTEGER DEFAULT 1 NOT NULL, 
	sys_mana_email VARCHAR(200) NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT sys_profile_pkey PRIMARY KEY (id), 
	CONSTRAINT sys_profile_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id), 
	CONSTRAINT sys_profile_sys_organization_fkey FOREIGN KEY(sys_organization) REFERENCES organizations (id)
)

;

-- organizations

CREATE TABLE organizations (
	id SERIAL NOT NULL, 
	org_code VARCHAR(200) NOT NULL, 
	org_name VARCHAR(200) NOT NULL, 
	org_type INTEGER NOT NULL, 
	contact_person VARCHAR(200) NOT NULL, 
	contact_email VARCHAR(200) NOT NULL, 
	contact_phone VARCHAR(200) NOT NULL, 
	address VARCHAR(200), 
	phone VARCHAR(200), 
	is_mana BOOLEAN DEFAULT false NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	memo VARCHAR(1000), 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT organizations_pkey PRIMARY KEY (id), 
	CONSTRAINT organizations_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id)
)

;

-- users

CREATE TABLE users (
	id SERIAL NOT NULL, 
	organization_id INTEGER NOT NULL, 
	account VARCHAR(100) NOT NULL, 
	username VARCHAR(200) NOT NULL, 
	password VARCHAR(200) NOT NULL, 
	department VARCHAR(200), 
	job_title VARCHAR(200), 
	phone VARCHAR(200), 
	user_role JSONB DEFAULT '[]'::jsonb NOT NULL, 
	last_login_at TIMESTAMP WITHOUT TIME ZONE, 
	last_login_ip VARCHAR(100), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT user_detail_pkey PRIMARY KEY (id), 
	CONSTRAINT user_detail_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id), 
	CONSTRAINT user_detail_organization_id_fkey FOREIGN KEY(organization_id) REFERENCES organizations (id)
)

;

-- user_roles

CREATE TABLE user_roles (
	id SERIAL NOT NULL, 
	role_cname VARCHAR(200) NOT NULL, 
	role_ename VARCHAR(200) NOT NULL, 
	description TEXT, 
	is_mana BOOLEAN DEFAULT false NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT user_roles_pkey PRIMARY KEY (id), 
	CONSTRAINT user_roles_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id)
)

;

-- system_functions

CREATE TABLE system_functions (
	id SERIAL NOT NULL, 
	func_code VARCHAR(200) NOT NULL, 
	upper_func_id INTEGER DEFAULT 0 NOT NULL, 
	func_cname VARCHAR(200) NOT NULL, 
	func_ename VARCHAR(200) NOT NULL, 
	func_type INTEGER NOT NULL, 
	func_order INTEGER NOT NULL, 
	func_icon VARCHAR(200), 
	module_code VARCHAR(200), 
	module_item JSONB DEFAULT '[]'::jsonb NOT NULL, 
	description TEXT, 
	is_mana BOOLEAN DEFAULT false NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT system_functions_pkey PRIMARY KEY (id), 
	CONSTRAINT fk_system_functions_editor FOREIGN KEY(edit_by) REFERENCES users (id)
)

;

-- role_rights

CREATE TABLE role_rights (
	id SERIAL NOT NULL, 
	user_role_id INTEGER NOT NULL, 
	system_function_id INTEGER NOT NULL, 
	func_code VARCHAR(20) NOT NULL, 
	is_create BOOLEAN DEFAULT false NOT NULL, 
	is_read BOOLEAN DEFAULT false NOT NULL, 
	is_update BOOLEAN DEFAULT false NOT NULL, 
	is_delete BOOLEAN DEFAULT false NOT NULL, 
	is_print BOOLEAN DEFAULT false NOT NULL, 
	is_file BOOLEAN DEFAULT false NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT role_rights_pkey PRIMARY KEY (id), 
	CONSTRAINT role_rights_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id), 
	CONSTRAINT role_rights_system_function_id_fkey FOREIGN KEY(system_function_id) REFERENCES system_functions (id), 
	CONSTRAINT role_rights_user_role_id_fkey FOREIGN KEY(user_role_id) REFERENCES user_roles (id)
)

;

-- user_logs

CREATE TABLE user_logs (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	system_function_id INTEGER NOT NULL, 
	module_item VARCHAR(50) NOT NULL, 
	data_id INTEGER, 
	session_id VARCHAR(36), 
	look_data JSONB DEFAULT '{}'::jsonb NOT NULL, 
	change_data JSONB DEFAULT '{}'::jsonb NOT NULL, 
	action_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	err_detail VARCHAR(2000), 
	CONSTRAINT user_logs_pkey PRIMARY KEY (id), 
	CONSTRAINT user_logs_user_id_fkey FOREIGN KEY(user_id) REFERENCES users (id)
)

;

-- system_codes

CREATE TABLE system_codes (
	id SERIAL NOT NULL, 
	code_etype VARCHAR(100) NOT NULL, 
	code_ctype VARCHAR(200) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	code_cname VARCHAR(300) NOT NULL, 
	code_ename VARCHAR(300), 
	"order" INTEGER DEFAULT 0 NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	note1 VARCHAR(500), 
	note2 VARCHAR(500), 
	note3 VARCHAR(500), 
	note4 VARCHAR(500), 
	note5 VARCHAR(500), 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	CONSTRAINT system_codes_pkey PRIMARY KEY (id), 
	CONSTRAINT system_codes_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id)
)

;

-- system_notifications

CREATE TABLE system_notifications (
	id SERIAL NOT NULL, 
	notice_csubject VARCHAR(200) NOT NULL, 
	notice_esubject VARCHAR(200) NOT NULL, 
	notice_cdescription TEXT NOT NULL, 
	notice_edescription TEXT NOT NULL, 
	notice_start_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	notice_end_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP + '3 days'::interval) NOT NULL, 
	notice_order INTEGER DEFAULT 0 NOT NULL, 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
	CONSTRAINT system_notifications_pkey PRIMARY KEY (id), 
	CONSTRAINT fk_system_notifications_edit_by FOREIGN KEY(edit_by) REFERENCES users (id)
)

;

-- notification_closedates

CREATE TABLE notification_closedates (
	id SERIAL NOT NULL, 
	closed_at DATE DEFAULT CURRENT_DATE NOT NULL, 
	edit_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	CONSTRAINT notification_closedates_pkey PRIMARY KEY (id), 
	CONSTRAINT notification_closedates_edit_by_fkey FOREIGN KEY(edit_by) REFERENCES users (id)
)

;

-- notification_read_today

CREATE TABLE notification_read_today (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	notification_id INTEGER NOT NULL, 
	read_date DATE DEFAULT CURRENT_DATE NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	CONSTRAINT notification_read_today_pkey PRIMARY KEY (id), 
	CONSTRAINT fk_notification_read_today_notification FOREIGN KEY(notification_id) REFERENCES system_notifications (id), 
	CONSTRAINT fk_notification_read_today_user FOREIGN KEY(user_id) REFERENCES users (id)
)

;

-- file_attachments

CREATE TABLE file_attachments (
	id SERIAL NOT NULL, 
	original_name VARCHAR(500) NOT NULL, 
	storage_path VARCHAR(1000) NOT NULL, 
	file_size BIGINT NOT NULL, 
	mime_type VARCHAR(200) NOT NULL, 
	file_hash VARCHAR(64) NOT NULL, 
	category VARCHAR(50) NOT NULL, 
	business_type VARCHAR(50), 
	related_table VARCHAR(100), 
	related_id INTEGER, 
	access_level VARCHAR(20) DEFAULT 'private'::character varying NOT NULL, 
	is_public BOOLEAN DEFAULT false NOT NULL, 
	allowed_roles TEXT[], 
	allowed_users INTEGER[], 
	is_temp BOOLEAN DEFAULT true NOT NULL, 
	confirmed_at TIMESTAMP WITHOUT TIME ZONE, 
	download_count INTEGER DEFAULT 0 NOT NULL, 
	last_downloaded_at TIMESTAMP WITHOUT TIME ZONE, 
	version INTEGER DEFAULT 1 NOT NULL, 
	previous_version_id INTEGER, 
	thumbnail_path VARCHAR(1000), 
	file_metadata JSONB, 
	description TEXT, 
	tags TEXT[], 
	expires_at TIMESTAMP WITHOUT TIME ZONE, 
	org_id INTEGER DEFAULT 1 NOT NULL, 
	uploaded_by INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	CONSTRAINT file_attachments_pkey PRIMARY KEY (id), 
	CONSTRAINT fk_file_attachments_org FOREIGN KEY(org_id) REFERENCES organizations (id), 
	CONSTRAINT fk_file_attachments_previous FOREIGN KEY(previous_version_id) REFERENCES file_attachments (id), 
	CONSTRAINT fk_file_attachments_uploaded_by FOREIGN KEY(uploaded_by) REFERENCES users (id)
)

;

-- ============================================================================
-- 建立索引
-- ============================================================================

CREATE INDEX idx_organizations_active ON organizations (is_active);
CREATE INDEX idx_organizations_mana ON organizations (is_mana);
CREATE INDEX idx_organizations_code ON organizations (org_code);
CREATE INDEX idx_users_active ON users (is_active);
CREATE INDEX idx_users_org ON users (organization_id);
CREATE INDEX idx_users_account ON users (account);
CREATE INDEX idx_user_roles_active ON user_roles (is_active);
CREATE INDEX idx_system_functions_order ON system_functions (func_order);
CREATE INDEX idx_system_functions_upper ON system_functions (upper_func_id);
CREATE INDEX idx_system_functions_module ON system_functions (module_code);
CREATE INDEX idx_system_functions_active ON system_functions (is_active);
CREATE INDEX idx_system_functions_type ON system_functions (func_type);
CREATE INDEX idx_system_functions_code ON system_functions (func_code);
CREATE INDEX idx_role_rights_role ON role_rights (user_role_id);
CREATE INDEX idx_role_rights_function ON role_rights (system_function_id);
CREATE INDEX idx_user_logs_session ON user_logs (session_id);
CREATE INDEX idx_user_logs_data_id ON user_logs (data_id);
CREATE INDEX idx_user_logs_module ON user_logs (module_item);
CREATE INDEX idx_user_logs_user ON user_logs (user_id);
CREATE INDEX idx_user_logs_function ON user_logs (system_function_id);
CREATE INDEX idx_user_logs_action_at ON user_logs (action_at);
CREATE INDEX idx_system_codes_type ON system_codes (code_etype, code_ctype);
CREATE INDEX idx_system_codes_order ON system_codes ("order");
CREATE INDEX idx_system_codes_active ON system_codes (is_active);
CREATE INDEX idx_system_codes_code ON system_codes (code);
CREATE INDEX idx_notifications_order ON system_notifications (notice_order);
CREATE INDEX idx_notifications_time ON system_notifications (notice_start_at, notice_end_at);
CREATE INDEX idx_notifications_active ON system_notifications (is_active);
CREATE INDEX idx_notification_closedates_edit_by ON notification_closedates (edit_by);
CREATE INDEX idx_notification_closedates_closed_at ON notification_closedates (closed_at);
CREATE INDEX idx_notification_closedates_edit_by_closed_at ON notification_closedates (edit_by, closed_at);
CREATE INDEX idx_notification_read_today_date ON notification_read_today (read_date);
CREATE INDEX idx_notification_read_today_notification ON notification_read_today (notification_id);
CREATE INDEX idx_notification_read_today_user ON notification_read_today (user_id);
CREATE INDEX idx_file_attachments_category ON file_attachments (category);
CREATE INDEX idx_file_attachments_access ON file_attachments (access_level);
CREATE INDEX idx_file_attachments_temp ON file_attachments (is_temp, created_at);
CREATE INDEX idx_file_attachments_org ON file_attachments (org_id);
CREATE INDEX idx_file_attachments_expires ON file_attachments (expires_at) WHERE (expires_at IS NOT NULL);
CREATE INDEX idx_file_attachments_hash ON file_attachments (file_hash);
CREATE INDEX idx_file_attachments_business ON file_attachments (business_type, related_id);
CREATE INDEX idx_file_attachments_uploader ON file_attachments (uploaded_by);

-- Schema 導出完成
