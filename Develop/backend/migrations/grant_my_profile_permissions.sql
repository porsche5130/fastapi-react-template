-- Grant my_profile permissions to all active user roles
-- Everyone should be able to view and update their own profile

-- Only insert permissions that don't exist
INSERT INTO role_rights (
    user_role_id,
    system_function_id,
    func_code,
    is_read,
    is_update,
    is_create,
    is_delete,
    is_print,
    is_file,
    edit_by
)
SELECT
    ur.id,              -- user_role_id
    sf.id,              -- system_function_id
    'my_profile',       -- func_code
    true,               -- is_read (everyone can read their profile)
    true,               -- is_update (everyone can update their profile)
    false,              -- is_create
    false,              -- is_delete
    false,              -- is_print
    false,              -- is_file
    1                   -- edit_by
FROM user_roles ur
CROSS JOIN system_functions sf
WHERE ur.is_active = true
  AND sf.func_code = 'my_profile'
  AND NOT EXISTS (
    SELECT 1 FROM role_rights rr
    WHERE rr.user_role_id = ur.id AND rr.func_code = 'my_profile'
  );
