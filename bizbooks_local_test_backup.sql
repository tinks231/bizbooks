--
-- PostgreSQL database dump
--

\restrict xlAk8vsp5LEapeABurHDvXijW7LTKzi82a81dtHg6eB13N0ypfckS9psmJeBZcy

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.7 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP EVENT TRIGGER IF EXISTS pgrst_drop_watch;
DROP EVENT TRIGGER IF EXISTS pgrst_ddl_watch;
DROP EVENT TRIGGER IF EXISTS issue_pg_net_access;
DROP EVENT TRIGGER IF EXISTS issue_pg_graphql_access;
DROP EVENT TRIGGER IF EXISTS issue_pg_cron_access;
DROP EVENT TRIGGER IF EXISTS issue_graphql_placeholder;
DROP PUBLICATION IF EXISTS supabase_realtime;
ALTER TABLE IF EXISTS ONLY storage.vector_indexes DROP CONSTRAINT IF EXISTS vector_indexes_bucket_id_fkey;
ALTER TABLE IF EXISTS ONLY storage.s3_multipart_uploads_parts DROP CONSTRAINT IF EXISTS s3_multipart_uploads_parts_upload_id_fkey;
ALTER TABLE IF EXISTS ONLY storage.s3_multipart_uploads_parts DROP CONSTRAINT IF EXISTS s3_multipart_uploads_parts_bucket_id_fkey;
ALTER TABLE IF EXISTS ONLY storage.s3_multipart_uploads DROP CONSTRAINT IF EXISTS s3_multipart_uploads_bucket_id_fkey;
ALTER TABLE IF EXISTS ONLY storage.prefixes DROP CONSTRAINT IF EXISTS "prefixes_bucketId_fkey";
ALTER TABLE IF EXISTS ONLY storage.objects DROP CONSTRAINT IF EXISTS "objects_bucketId_fkey";
ALTER TABLE IF EXISTS ONLY public.vendors DROP CONSTRAINT IF EXISTS vendors_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.vendor_payments DROP CONSTRAINT IF EXISTS vendor_payments_vendor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.vendor_payments DROP CONSTRAINT IF EXISTS vendor_payments_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transfers DROP CONSTRAINT IF EXISTS transfers_to_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transfers DROP CONSTRAINT IF EXISTS transfers_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transfers DROP CONSTRAINT IF EXISTS transfers_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.transfers DROP CONSTRAINT IF EXISTS transfers_initiated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.transfers DROP CONSTRAINT IF EXISTS transfers_from_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tasks DROP CONSTRAINT IF EXISTS tasks_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tasks DROP CONSTRAINT IF EXISTS tasks_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.tasks DROP CONSTRAINT IF EXISTS tasks_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.tasks DROP CONSTRAINT IF EXISTS tasks_assigned_to_fkey;
ALTER TABLE IF EXISTS ONLY public.task_updates DROP CONSTRAINT IF EXISTS task_updates_updated_by_fkey;
ALTER TABLE IF EXISTS ONLY public.task_updates DROP CONSTRAINT IF EXISTS task_updates_task_id_fkey;
ALTER TABLE IF EXISTS ONLY public.task_media DROP CONSTRAINT IF EXISTS task_media_uploaded_by_fkey;
ALTER TABLE IF EXISTS ONLY public.task_media DROP CONSTRAINT IF EXISTS task_media_task_id_fkey;
ALTER TABLE IF EXISTS ONLY public.task_materials DROP CONSTRAINT IF EXISTS task_materials_task_id_fkey;
ALTER TABLE IF EXISTS ONLY public.task_materials DROP CONSTRAINT IF EXISTS task_materials_added_by_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_plans DROP CONSTRAINT IF EXISTS subscription_plans_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_payments DROP CONSTRAINT IF EXISTS subscription_payments_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_payments DROP CONSTRAINT IF EXISTS subscription_payments_subscription_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_payments DROP CONSTRAINT IF EXISTS subscription_payments_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_deliveries DROP CONSTRAINT IF EXISTS subscription_deliveries_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_deliveries DROP CONSTRAINT IF EXISTS subscription_deliveries_subscription_id_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_deliveries DROP CONSTRAINT IF EXISTS subscription_deliveries_delivered_by_fkey;
ALTER TABLE IF EXISTS ONLY public.subscription_deliveries DROP CONSTRAINT IF EXISTS subscription_deliveries_assigned_to_fkey;
ALTER TABLE IF EXISTS ONLY public.stocks DROP CONSTRAINT IF EXISTS stocks_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stocks DROP CONSTRAINT IF EXISTS stocks_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stocks DROP CONSTRAINT IF EXISTS stocks_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_movements DROP CONSTRAINT IF EXISTS stock_movements_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_movements DROP CONSTRAINT IF EXISTS stock_movements_transfer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_movements DROP CONSTRAINT IF EXISTS stock_movements_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_movements DROP CONSTRAINT IF EXISTS stock_movements_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.stock_movements DROP CONSTRAINT IF EXISTS stock_movements_material_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sites DROP CONSTRAINT IF EXISTS sites_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales_orders DROP CONSTRAINT IF EXISTS sales_orders_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales_orders DROP CONSTRAINT IF EXISTS sales_orders_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales_order_items DROP CONSTRAINT IF EXISTS sales_order_items_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales_order_items DROP CONSTRAINT IF EXISTS sales_order_items_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales_order_items DROP CONSTRAINT IF EXISTS sales_order_items_sales_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public.sales_order_items DROP CONSTRAINT IF EXISTS sales_order_items_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.salary_slips DROP CONSTRAINT IF EXISTS salary_slips_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.salary_slips DROP CONSTRAINT IF EXISTS salary_slips_payroll_payment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.salary_slips DROP CONSTRAINT IF EXISTS salary_slips_employee_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_requests DROP CONSTRAINT IF EXISTS purchase_requests_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_requests DROP CONSTRAINT IF EXISTS purchase_requests_employee_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_requests DROP CONSTRAINT IF EXISTS purchase_requests_created_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_requests DROP CONSTRAINT IF EXISTS purchase_requests_created_expense_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bills DROP CONSTRAINT IF EXISTS purchase_bills_vendor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bills DROP CONSTRAINT IF EXISTS purchase_bills_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bills DROP CONSTRAINT IF EXISTS purchase_bills_purchase_request_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bill_items DROP CONSTRAINT IF EXISTS purchase_bill_items_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bill_items DROP CONSTRAINT IF EXISTS purchase_bill_items_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bill_items DROP CONSTRAINT IF EXISTS purchase_bill_items_purchase_bill_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bill_items DROP CONSTRAINT IF EXISTS purchase_bill_items_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.payroll_payments DROP CONSTRAINT IF EXISTS payroll_payments_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.payroll_payments DROP CONSTRAINT IF EXISTS payroll_payments_paid_from_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.payroll_payments DROP CONSTRAINT IF EXISTS payroll_payments_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.payment_allocations DROP CONSTRAINT IF EXISTS payment_allocations_purchase_bill_id_fkey;
ALTER TABLE IF EXISTS ONLY public.payment_allocations DROP CONSTRAINT IF EXISTS payment_allocations_payment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_transactions DROP CONSTRAINT IF EXISTS loyalty_transactions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_transactions DROP CONSTRAINT IF EXISTS loyalty_transactions_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_transactions DROP CONSTRAINT IF EXISTS loyalty_transactions_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_transactions DROP CONSTRAINT IF EXISTS loyalty_transactions_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_programs DROP CONSTRAINT IF EXISTS loyalty_programs_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.items DROP CONSTRAINT IF EXISTS items_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.items DROP CONSTRAINT IF EXISTS items_item_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.items DROP CONSTRAINT IF EXISTS items_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stocks DROP CONSTRAINT IF EXISTS item_stocks_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stocks DROP CONSTRAINT IF EXISTS item_stocks_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stocks DROP CONSTRAINT IF EXISTS item_stocks_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stock_movements DROP CONSTRAINT IF EXISTS item_stock_movements_to_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stock_movements DROP CONSTRAINT IF EXISTS item_stock_movements_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stock_movements DROP CONSTRAINT IF EXISTS item_stock_movements_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stock_movements DROP CONSTRAINT IF EXISTS item_stock_movements_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_stock_movements DROP CONSTRAINT IF EXISTS item_stock_movements_from_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_images DROP CONSTRAINT IF EXISTS item_images_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_groups DROP CONSTRAINT IF EXISTS item_groups_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_categories DROP CONSTRAINT IF EXISTS item_categories_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_categories DROP CONSTRAINT IF EXISTS item_categories_parent_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.item_categories DROP CONSTRAINT IF EXISTS item_categories_group_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_sales_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_delivery_challan_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_sales_order_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_delivery_challan_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_commissions DROP CONSTRAINT IF EXISTS invoice_commissions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_commissions DROP CONSTRAINT IF EXISTS invoice_commissions_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_commissions DROP CONSTRAINT IF EXISTS invoice_commissions_agent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustments DROP CONSTRAINT IF EXISTS inventory_adjustments_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustment_lines DROP CONSTRAINT IF EXISTS inventory_adjustment_lines_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustment_lines DROP CONSTRAINT IF EXISTS inventory_adjustment_lines_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustment_lines DROP CONSTRAINT IF EXISTS inventory_adjustment_lines_adjustment_id_fkey;
ALTER TABLE IF EXISTS ONLY public.expenses DROP CONSTRAINT IF EXISTS expenses_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.expenses DROP CONSTRAINT IF EXISTS expenses_category_id_fkey;
ALTER TABLE IF EXISTS ONLY public.expense_categories DROP CONSTRAINT IF EXISTS expense_categories_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.employees DROP CONSTRAINT IF EXISTS employees_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.employees DROP CONSTRAINT IF EXISTS employees_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_day_notes DROP CONSTRAINT IF EXISTS delivery_day_notes_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challans DROP CONSTRAINT IF EXISTS delivery_challans_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challans DROP CONSTRAINT IF EXISTS delivery_challans_sales_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challans DROP CONSTRAINT IF EXISTS delivery_challans_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challan_items DROP CONSTRAINT IF EXISTS delivery_challan_items_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challan_items DROP CONSTRAINT IF EXISTS delivery_challan_items_sales_order_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challan_items DROP CONSTRAINT IF EXISTS delivery_challan_items_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challan_items DROP CONSTRAINT IF EXISTS delivery_challan_items_delivery_challan_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customers DROP CONSTRAINT IF EXISTS customers_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customers DROP CONSTRAINT IF EXISTS customers_default_delivery_employee_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_subscriptions DROP CONSTRAINT IF EXISTS customer_subscriptions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_subscriptions DROP CONSTRAINT IF EXISTS customer_subscriptions_plan_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_subscriptions DROP CONSTRAINT IF EXISTS customer_subscriptions_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_orders DROP CONSTRAINT IF EXISTS customer_orders_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_orders DROP CONSTRAINT IF EXISTS customer_orders_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_orders DROP CONSTRAINT IF EXISTS customer_orders_fulfilled_by_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_orders DROP CONSTRAINT IF EXISTS customer_orders_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_order_items DROP CONSTRAINT IF EXISTS customer_order_items_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_order_items DROP CONSTRAINT IF EXISTS customer_order_items_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_loyalty_points DROP CONSTRAINT IF EXISTS customer_loyalty_points_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.customer_loyalty_points DROP CONSTRAINT IF EXISTS customer_loyalty_points_customer_id_fkey;
ALTER TABLE IF EXISTS ONLY public.commission_agents DROP CONSTRAINT IF EXISTS commission_agents_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.commission_agents DROP CONSTRAINT IF EXISTS commission_agents_employee_id_fkey;
ALTER TABLE IF EXISTS ONLY public.commission_agents DROP CONSTRAINT IF EXISTS commission_agents_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.attendance DROP CONSTRAINT IF EXISTS attendance_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.attendance DROP CONSTRAINT IF EXISTS attendance_site_id_fkey;
ALTER TABLE IF EXISTS ONLY public.attendance DROP CONSTRAINT IF EXISTS attendance_employee_id_fkey;
ALTER TABLE IF EXISTS ONLY public.account_transactions DROP CONSTRAINT IF EXISTS account_transactions_tenant_id_fkey;
ALTER TABLE IF EXISTS ONLY public.account_transactions DROP CONSTRAINT IF EXISTS account_transactions_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.account_transactions DROP CONSTRAINT IF EXISTS account_transactions_account_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.sso_domains DROP CONSTRAINT IF EXISTS sso_domains_sso_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.sessions DROP CONSTRAINT IF EXISTS sessions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.sessions DROP CONSTRAINT IF EXISTS sessions_oauth_client_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.saml_relay_states DROP CONSTRAINT IF EXISTS saml_relay_states_sso_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.saml_relay_states DROP CONSTRAINT IF EXISTS saml_relay_states_flow_state_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.saml_providers DROP CONSTRAINT IF EXISTS saml_providers_sso_provider_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_session_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.one_time_tokens DROP CONSTRAINT IF EXISTS one_time_tokens_user_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_consents DROP CONSTRAINT IF EXISTS oauth_consents_user_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_consents DROP CONSTRAINT IF EXISTS oauth_consents_client_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_authorizations DROP CONSTRAINT IF EXISTS oauth_authorizations_user_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_authorizations DROP CONSTRAINT IF EXISTS oauth_authorizations_client_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.mfa_factors DROP CONSTRAINT IF EXISTS mfa_factors_user_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.mfa_challenges DROP CONSTRAINT IF EXISTS mfa_challenges_auth_factor_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.mfa_amr_claims DROP CONSTRAINT IF EXISTS mfa_amr_claims_session_id_fkey;
ALTER TABLE IF EXISTS ONLY auth.identities DROP CONSTRAINT IF EXISTS identities_user_id_fkey;
DROP TRIGGER IF EXISTS update_objects_updated_at ON storage.objects;
DROP TRIGGER IF EXISTS prefixes_delete_hierarchy ON storage.prefixes;
DROP TRIGGER IF EXISTS prefixes_create_hierarchy ON storage.prefixes;
DROP TRIGGER IF EXISTS objects_update_create_prefix ON storage.objects;
DROP TRIGGER IF EXISTS objects_insert_create_prefix ON storage.objects;
DROP TRIGGER IF EXISTS objects_delete_delete_prefix ON storage.objects;
DROP TRIGGER IF EXISTS enforce_bucket_name_length_trigger ON storage.buckets;
DROP TRIGGER IF EXISTS tr_check_filters ON realtime.subscription;
DROP INDEX IF EXISTS storage.vector_indexes_name_bucket_id_idx;
DROP INDEX IF EXISTS storage.objects_bucket_id_level_idx;
DROP INDEX IF EXISTS storage.name_prefix_search;
DROP INDEX IF EXISTS storage.idx_prefixes_lower_name;
DROP INDEX IF EXISTS storage.idx_objects_lower_name;
DROP INDEX IF EXISTS storage.idx_objects_bucket_id_name;
DROP INDEX IF EXISTS storage.idx_name_bucket_level_unique;
DROP INDEX IF EXISTS storage.idx_multipart_uploads_list;
DROP INDEX IF EXISTS storage.buckets_analytics_unique_name_idx;
DROP INDEX IF EXISTS storage.bucketid_objname;
DROP INDEX IF EXISTS storage.bname;
DROP INDEX IF EXISTS realtime.subscription_subscription_id_entity_filters_key;
DROP INDEX IF EXISTS realtime.messages_inserted_at_topic_index;
DROP INDEX IF EXISTS realtime.ix_realtime_subscription_entity;
DROP INDEX IF EXISTS public.loyalty_programs_tenant_id_unique;
DROP INDEX IF EXISTS public.ix_transfers_tenant_id;
DROP INDEX IF EXISTS public.ix_tenants_subdomain;
DROP INDEX IF EXISTS public.ix_tasks_tenant_id;
DROP INDEX IF EXISTS public.ix_tasks_site_id;
DROP INDEX IF EXISTS public.ix_tasks_assigned_to;
DROP INDEX IF EXISTS public.ix_task_updates_task_id;
DROP INDEX IF EXISTS public.ix_task_media_task_id;
DROP INDEX IF EXISTS public.ix_task_materials_task_id;
DROP INDEX IF EXISTS public.ix_subscription_deliveries_delivery_date;
DROP INDEX IF EXISTS public.ix_stocks_tenant_id;
DROP INDEX IF EXISTS public.ix_stock_movements_tenant_id;
DROP INDEX IF EXISTS public.ix_sites_tenant_id;
DROP INDEX IF EXISTS public.ix_purchase_requests_tenant_id;
DROP INDEX IF EXISTS public.ix_materials_tenant_id;
DROP INDEX IF EXISTS public.ix_items_tenant_id;
DROP INDEX IF EXISTS public.ix_item_stocks_tenant_id;
DROP INDEX IF EXISTS public.ix_item_stock_movements_tenant_id;
DROP INDEX IF EXISTS public.ix_item_groups_tenant_id;
DROP INDEX IF EXISTS public.ix_item_categories_tenant_id;
DROP INDEX IF EXISTS public.ix_invoices_tenant_id;
DROP INDEX IF EXISTS public.ix_inventory_adjustments_tenant_id;
DROP INDEX IF EXISTS public.ix_expenses_tenant_id;
DROP INDEX IF EXISTS public.ix_expenses_expense_date;
DROP INDEX IF EXISTS public.ix_expense_categories_tenant_id;
DROP INDEX IF EXISTS public.ix_employees_tenant_id;
DROP INDEX IF EXISTS public.ix_bank_accounts_tenant_id;
DROP INDEX IF EXISTS public.ix_bank_accounts_is_default;
DROP INDEX IF EXISTS public.ix_bank_accounts_is_active;
DROP INDEX IF EXISTS public.ix_attendance_tenant_id;
DROP INDEX IF EXISTS public.ix_account_transactions_transaction_type;
DROP INDEX IF EXISTS public.ix_account_transactions_transaction_date;
DROP INDEX IF EXISTS public.ix_account_transactions_tenant_id;
DROP INDEX IF EXISTS public.ix_account_transactions_reference_type;
DROP INDEX IF EXISTS public.ix_account_transactions_reference_id;
DROP INDEX IF EXISTS public.ix_account_transactions_account_id;
DROP INDEX IF EXISTS public.idx_vendors_tenant_active;
DROP INDEX IF EXISTS public.idx_vendor_payments_vendor;
DROP INDEX IF EXISTS public.idx_vendor_payments_tenant;
DROP INDEX IF EXISTS public.idx_vendor_payments_date;
DROP INDEX IF EXISTS public.idx_tenant_vendor;
DROP INDEX IF EXISTS public.idx_tenant_transfer;
DROP INDEX IF EXISTS public.idx_tenant_stock;
DROP INDEX IF EXISTS public.idx_tenant_status;
DROP INDEX IF EXISTS public.idx_tenant_site;
DROP INDEX IF EXISTS public.idx_tenant_paid_date;
DROP INDEX IF EXISTS public.idx_tenant_movement;
DROP INDEX IF EXISTS public.idx_tenant_material;
DROP INDEX IF EXISTS public.idx_tenant_employee_date;
DROP INDEX IF EXISTS public.idx_tenant_employee;
DROP INDEX IF EXISTS public.idx_tenant_attendance;
DROP INDEX IF EXISTS public.idx_tenant_agent_paid;
DROP INDEX IF EXISTS public.idx_tenant_active;
DROP INDEX IF EXISTS public.idx_task_update_task;
DROP INDEX IF EXISTS public.idx_task_status;
DROP INDEX IF EXISTS public.idx_task_media_task;
DROP INDEX IF EXISTS public.idx_task_material_task;
DROP INDEX IF EXISTS public.idx_task_employee;
DROP INDEX IF EXISTS public.idx_subscription_plans_tenant_active;
DROP INDEX IF EXISTS public.idx_subscription_plans_tenant;
DROP INDEX IF EXISTS public.idx_subscription_payments_tenant_date;
DROP INDEX IF EXISTS public.idx_subscription_payments_tenant;
DROP INDEX IF EXISTS public.idx_subscription_payments_subscription;
DROP INDEX IF EXISTS public.idx_subscription_payments_date;
DROP INDEX IF EXISTS public.idx_subscription_deliveries_tenant;
DROP INDEX IF EXISTS public.idx_subscription_deliveries_subscription;
DROP INDEX IF EXISTS public.idx_subscription_deliveries_date;
DROP INDEX IF EXISTS public.idx_sales_orders_tenant_status;
DROP INDEX IF EXISTS public.idx_sales_orders_tenant_date;
DROP INDEX IF EXISTS public.idx_salary_slips_tenant;
DROP INDEX IF EXISTS public.idx_salary_slips_employee;
DROP INDEX IF EXISTS public.idx_purchase_bills_vendor;
DROP INDEX IF EXISTS public.idx_purchase_bills_tenant_status;
DROP INDEX IF EXISTS public.idx_purchase_bills_tenant_payment;
DROP INDEX IF EXISTS public.idx_purchase_bills_tenant_date;
DROP INDEX IF EXISTS public.idx_purchase_bills_tenant;
DROP INDEX IF EXISTS public.idx_purchase_bills_status;
DROP INDEX IF EXISTS public.idx_purchase_bills_payment_status;
DROP INDEX IF EXISTS public.idx_purchase_bills_bill_date;
DROP INDEX IF EXISTS public.idx_purchase_bill_items_item;
DROP INDEX IF EXISTS public.idx_purchase_bill_items_bill;
DROP INDEX IF EXISTS public.idx_payroll_payments_tenant;
DROP INDEX IF EXISTS public.idx_payment_allocations_payment;
DROP INDEX IF EXISTS public.idx_payment_allocations_bill;
DROP INDEX IF EXISTS public.idx_password_reset_token;
DROP INDEX IF EXISTS public.idx_password_reset_expires;
DROP INDEX IF EXISTS public.idx_loyalty_transactions_type;
DROP INDEX IF EXISTS public.idx_loyalty_transactions_invoice;
DROP INDEX IF EXISTS public.idx_loyalty_transactions_customer;
DROP INDEX IF EXISTS public.idx_loyalty_points_customer;
DROP INDEX IF EXISTS public.idx_items_tenant_track;
DROP INDEX IF EXISTS public.idx_items_tenant_group;
DROP INDEX IF EXISTS public.idx_items_tenant_category;
DROP INDEX IF EXISTS public.idx_items_tenant_active;
DROP INDEX IF EXISTS public.idx_items_mrp;
DROP INDEX IF EXISTS public.idx_items_barcode;
DROP INDEX IF EXISTS public.idx_item_tenant;
DROP INDEX IF EXISTS public.idx_item_stock_tenant;
DROP INDEX IF EXISTS public.idx_item_stock_item;
DROP INDEX IF EXISTS public.idx_item_sku;
DROP INDEX IF EXISTS public.idx_item_movement_tenant;
DROP INDEX IF EXISTS public.idx_item_movement_site;
DROP INDEX IF EXISTS public.idx_item_movement_item;
DROP INDEX IF EXISTS public.idx_item_category;
DROP INDEX IF EXISTS public.idx_invoices_tenant_status;
DROP INDEX IF EXISTS public.idx_invoices_tenant_payment;
DROP INDEX IF EXISTS public.idx_invoices_tenant_date;
DROP INDEX IF EXISTS public.idx_invoices_loyalty;
DROP INDEX IF EXISTS public.idx_invoice_tenant;
DROP INDEX IF EXISTS public.idx_invoice_number;
DROP INDEX IF EXISTS public.idx_invoice_item_invoice;
DROP INDEX IF EXISTS public.idx_group_tenant;
DROP INDEX IF EXISTS public.idx_expenses_tenant_date;
DROP INDEX IF EXISTS public.idx_expenses_tenant_category;
DROP INDEX IF EXISTS public.idx_expense_tenant_date;
DROP INDEX IF EXISTS public.idx_expense_category;
DROP INDEX IF EXISTS public.idx_employee_requests;
DROP INDEX IF EXISTS public.idx_delivery_challans_tenant_date;
DROP INDEX IF EXISTS public.idx_deliveries_assigned_employee;
DROP INDEX IF EXISTS public.idx_customers_tenant_active;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_tenant_status;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_tenant;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_plan;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_period_end;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_due_soon;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_due_date;
DROP INDEX IF EXISTS public.idx_customer_subscriptions_customer;
DROP INDEX IF EXISTS public.idx_customer_phone_pin;
DROP INDEX IF EXISTS public.idx_customer_order_status;
DROP INDEX IF EXISTS public.idx_customer_order_invoice;
DROP INDEX IF EXISTS public.idx_customer_order_date;
DROP INDEX IF EXISTS public.idx_category_tenant;
DROP INDEX IF EXISTS public.idx_category_group;
DROP INDEX IF EXISTS public.idx_bank_accounts_type;
DROP INDEX IF EXISTS public.idx_bank_accounts_tenant;
DROP INDEX IF EXISTS public.idx_bank_accounts_default;
DROP INDEX IF EXISTS public.idx_adjustment_tenant;
DROP INDEX IF EXISTS public.idx_account_transactions_type;
DROP INDEX IF EXISTS public.idx_account_transactions_tenant;
DROP INDEX IF EXISTS public.idx_account_transactions_reference;
DROP INDEX IF EXISTS public.idx_account_transactions_account;
DROP INDEX IF EXISTS auth.users_is_anonymous_idx;
DROP INDEX IF EXISTS auth.users_instance_id_idx;
DROP INDEX IF EXISTS auth.users_instance_id_email_idx;
DROP INDEX IF EXISTS auth.users_email_partial_key;
DROP INDEX IF EXISTS auth.user_id_created_at_idx;
DROP INDEX IF EXISTS auth.unique_phone_factor_per_user;
DROP INDEX IF EXISTS auth.sso_providers_resource_id_pattern_idx;
DROP INDEX IF EXISTS auth.sso_providers_resource_id_idx;
DROP INDEX IF EXISTS auth.sso_domains_sso_provider_id_idx;
DROP INDEX IF EXISTS auth.sso_domains_domain_idx;
DROP INDEX IF EXISTS auth.sessions_user_id_idx;
DROP INDEX IF EXISTS auth.sessions_oauth_client_id_idx;
DROP INDEX IF EXISTS auth.sessions_not_after_idx;
DROP INDEX IF EXISTS auth.saml_relay_states_sso_provider_id_idx;
DROP INDEX IF EXISTS auth.saml_relay_states_for_email_idx;
DROP INDEX IF EXISTS auth.saml_relay_states_created_at_idx;
DROP INDEX IF EXISTS auth.saml_providers_sso_provider_id_idx;
DROP INDEX IF EXISTS auth.refresh_tokens_updated_at_idx;
DROP INDEX IF EXISTS auth.refresh_tokens_session_id_revoked_idx;
DROP INDEX IF EXISTS auth.refresh_tokens_parent_idx;
DROP INDEX IF EXISTS auth.refresh_tokens_instance_id_user_id_idx;
DROP INDEX IF EXISTS auth.refresh_tokens_instance_id_idx;
DROP INDEX IF EXISTS auth.recovery_token_idx;
DROP INDEX IF EXISTS auth.reauthentication_token_idx;
DROP INDEX IF EXISTS auth.one_time_tokens_user_id_token_type_key;
DROP INDEX IF EXISTS auth.one_time_tokens_token_hash_hash_idx;
DROP INDEX IF EXISTS auth.one_time_tokens_relates_to_hash_idx;
DROP INDEX IF EXISTS auth.oauth_consents_user_order_idx;
DROP INDEX IF EXISTS auth.oauth_consents_active_user_client_idx;
DROP INDEX IF EXISTS auth.oauth_consents_active_client_idx;
DROP INDEX IF EXISTS auth.oauth_clients_deleted_at_idx;
DROP INDEX IF EXISTS auth.oauth_auth_pending_exp_idx;
DROP INDEX IF EXISTS auth.mfa_factors_user_id_idx;
DROP INDEX IF EXISTS auth.mfa_factors_user_friendly_name_unique;
DROP INDEX IF EXISTS auth.mfa_challenge_created_at_idx;
DROP INDEX IF EXISTS auth.idx_user_id_auth_method;
DROP INDEX IF EXISTS auth.idx_auth_code;
DROP INDEX IF EXISTS auth.identities_user_id_idx;
DROP INDEX IF EXISTS auth.identities_email_idx;
DROP INDEX IF EXISTS auth.flow_state_created_at_idx;
DROP INDEX IF EXISTS auth.factor_id_created_at_idx;
DROP INDEX IF EXISTS auth.email_change_token_new_idx;
DROP INDEX IF EXISTS auth.email_change_token_current_idx;
DROP INDEX IF EXISTS auth.confirmation_token_idx;
DROP INDEX IF EXISTS auth.audit_logs_instance_id_idx;
ALTER TABLE IF EXISTS ONLY storage.vector_indexes DROP CONSTRAINT IF EXISTS vector_indexes_pkey;
ALTER TABLE IF EXISTS ONLY storage.s3_multipart_uploads DROP CONSTRAINT IF EXISTS s3_multipart_uploads_pkey;
ALTER TABLE IF EXISTS ONLY storage.s3_multipart_uploads_parts DROP CONSTRAINT IF EXISTS s3_multipart_uploads_parts_pkey;
ALTER TABLE IF EXISTS ONLY storage.prefixes DROP CONSTRAINT IF EXISTS prefixes_pkey;
ALTER TABLE IF EXISTS ONLY storage.objects DROP CONSTRAINT IF EXISTS objects_pkey;
ALTER TABLE IF EXISTS ONLY storage.migrations DROP CONSTRAINT IF EXISTS migrations_pkey;
ALTER TABLE IF EXISTS ONLY storage.migrations DROP CONSTRAINT IF EXISTS migrations_name_key;
ALTER TABLE IF EXISTS ONLY storage.buckets_vectors DROP CONSTRAINT IF EXISTS buckets_vectors_pkey;
ALTER TABLE IF EXISTS ONLY storage.buckets DROP CONSTRAINT IF EXISTS buckets_pkey;
ALTER TABLE IF EXISTS ONLY storage.buckets_analytics DROP CONSTRAINT IF EXISTS buckets_analytics_pkey;
ALTER TABLE IF EXISTS ONLY realtime.schema_migrations DROP CONSTRAINT IF EXISTS schema_migrations_pkey;
ALTER TABLE IF EXISTS ONLY realtime.subscription DROP CONSTRAINT IF EXISTS pk_subscription;
ALTER TABLE IF EXISTS ONLY realtime.messages DROP CONSTRAINT IF EXISTS messages_pkey;
ALTER TABLE IF EXISTS ONLY public.vendors DROP CONSTRAINT IF EXISTS vendors_pkey;
ALTER TABLE IF EXISTS ONLY public.vendor_payments DROP CONSTRAINT IF EXISTS vendor_payments_pkey;
ALTER TABLE IF EXISTS ONLY public.vendor_payments DROP CONSTRAINT IF EXISTS vendor_payments_payment_number_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_username_key;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.items DROP CONSTRAINT IF EXISTS uq_tenant_sku;
ALTER TABLE IF EXISTS ONLY public.subscription_deliveries DROP CONSTRAINT IF EXISTS uq_subscription_delivery_date;
ALTER TABLE IF EXISTS ONLY public.items DROP CONSTRAINT IF EXISTS uq_items_barcode_tenant;
ALTER TABLE IF EXISTS ONLY public.delivery_day_notes DROP CONSTRAINT IF EXISTS uq_delivery_day_note_tenant_date;
ALTER TABLE IF EXISTS ONLY public.vendors DROP CONSTRAINT IF EXISTS unique_vendor_code_per_tenant;
ALTER TABLE IF EXISTS ONLY public.employees DROP CONSTRAINT IF EXISTS unique_tenant_pin;
ALTER TABLE IF EXISTS ONLY public.payroll_payments DROP CONSTRAINT IF EXISTS unique_tenant_payroll;
ALTER TABLE IF EXISTS ONLY public.commission_agents DROP CONSTRAINT IF EXISTS unique_tenant_employee_agent;
ALTER TABLE IF EXISTS ONLY public.commission_agents DROP CONSTRAINT IF EXISTS unique_tenant_agent_code;
ALTER TABLE IF EXISTS ONLY public.customer_orders DROP CONSTRAINT IF EXISTS unique_order_number_per_tenant;
ALTER TABLE IF EXISTS ONLY public.invoice_commissions DROP CONSTRAINT IF EXISTS unique_invoice_commission;
ALTER TABLE IF EXISTS ONLY public.customers DROP CONSTRAINT IF EXISTS unique_customer_code_per_tenant;
ALTER TABLE IF EXISTS ONLY public.transfers DROP CONSTRAINT IF EXISTS transfers_pkey;
ALTER TABLE IF EXISTS ONLY public.tenants DROP CONSTRAINT IF EXISTS tenants_pkey;
ALTER TABLE IF EXISTS ONLY public.tenants DROP CONSTRAINT IF EXISTS tenants_admin_email_key;
ALTER TABLE IF EXISTS ONLY public.tasks DROP CONSTRAINT IF EXISTS tasks_pkey;
ALTER TABLE IF EXISTS ONLY public.task_updates DROP CONSTRAINT IF EXISTS task_updates_pkey;
ALTER TABLE IF EXISTS ONLY public.task_media DROP CONSTRAINT IF EXISTS task_media_pkey;
ALTER TABLE IF EXISTS ONLY public.task_materials DROP CONSTRAINT IF EXISTS task_materials_pkey;
ALTER TABLE IF EXISTS ONLY public.subscription_plans DROP CONSTRAINT IF EXISTS subscription_plans_pkey;
ALTER TABLE IF EXISTS ONLY public.subscription_payments DROP CONSTRAINT IF EXISTS subscription_payments_pkey;
ALTER TABLE IF EXISTS ONLY public.subscription_deliveries DROP CONSTRAINT IF EXISTS subscription_deliveries_pkey;
ALTER TABLE IF EXISTS ONLY public.stocks DROP CONSTRAINT IF EXISTS stocks_pkey;
ALTER TABLE IF EXISTS ONLY public.stock_movements DROP CONSTRAINT IF EXISTS stock_movements_pkey;
ALTER TABLE IF EXISTS ONLY public.sites DROP CONSTRAINT IF EXISTS sites_pkey;
ALTER TABLE IF EXISTS ONLY public.sales_orders DROP CONSTRAINT IF EXISTS sales_orders_pkey;
ALTER TABLE IF EXISTS ONLY public.sales_orders DROP CONSTRAINT IF EXISTS sales_orders_order_number_key;
ALTER TABLE IF EXISTS ONLY public.sales_order_items DROP CONSTRAINT IF EXISTS sales_order_items_pkey;
ALTER TABLE IF EXISTS ONLY public.salary_slips DROP CONSTRAINT IF EXISTS salary_slips_pkey;
ALTER TABLE IF EXISTS ONLY public.purchase_requests DROP CONSTRAINT IF EXISTS purchase_requests_pkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bills DROP CONSTRAINT IF EXISTS purchase_bills_pkey;
ALTER TABLE IF EXISTS ONLY public.purchase_bills DROP CONSTRAINT IF EXISTS purchase_bills_bill_number_key;
ALTER TABLE IF EXISTS ONLY public.purchase_bill_items DROP CONSTRAINT IF EXISTS purchase_bill_items_pkey;
ALTER TABLE IF EXISTS ONLY public.payroll_payments DROP CONSTRAINT IF EXISTS payroll_payments_pkey;
ALTER TABLE IF EXISTS ONLY public.payment_allocations DROP CONSTRAINT IF EXISTS payment_allocations_pkey;
ALTER TABLE IF EXISTS ONLY public.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_token_key;
ALTER TABLE IF EXISTS ONLY public.password_reset_tokens DROP CONSTRAINT IF EXISTS password_reset_tokens_pkey;
ALTER TABLE IF EXISTS ONLY public.materials DROP CONSTRAINT IF EXISTS materials_pkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_transactions DROP CONSTRAINT IF EXISTS loyalty_transactions_pkey;
ALTER TABLE IF EXISTS ONLY public.loyalty_programs DROP CONSTRAINT IF EXISTS loyalty_programs_pkey;
ALTER TABLE IF EXISTS ONLY public.items DROP CONSTRAINT IF EXISTS items_pkey;
ALTER TABLE IF EXISTS ONLY public.item_stocks DROP CONSTRAINT IF EXISTS item_stocks_pkey;
ALTER TABLE IF EXISTS ONLY public.item_stock_movements DROP CONSTRAINT IF EXISTS item_stock_movements_pkey;
ALTER TABLE IF EXISTS ONLY public.item_images DROP CONSTRAINT IF EXISTS item_images_pkey;
ALTER TABLE IF EXISTS ONLY public.item_groups DROP CONSTRAINT IF EXISTS item_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.item_categories DROP CONSTRAINT IF EXISTS item_categories_pkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_commissions DROP CONSTRAINT IF EXISTS invoice_commissions_pkey;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustments DROP CONSTRAINT IF EXISTS inventory_adjustments_pkey;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustment_lines DROP CONSTRAINT IF EXISTS inventory_adjustment_lines_pkey;
ALTER TABLE IF EXISTS ONLY public.expenses DROP CONSTRAINT IF EXISTS expenses_pkey;
ALTER TABLE IF EXISTS ONLY public.expense_categories DROP CONSTRAINT IF EXISTS expense_categories_pkey;
ALTER TABLE IF EXISTS ONLY public.employees DROP CONSTRAINT IF EXISTS employees_pkey;
ALTER TABLE IF EXISTS ONLY public.delivery_day_notes DROP CONSTRAINT IF EXISTS delivery_day_notes_pkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challans DROP CONSTRAINT IF EXISTS delivery_challans_pkey;
ALTER TABLE IF EXISTS ONLY public.delivery_challans DROP CONSTRAINT IF EXISTS delivery_challans_challan_number_key;
ALTER TABLE IF EXISTS ONLY public.delivery_challan_items DROP CONSTRAINT IF EXISTS delivery_challan_items_pkey;
ALTER TABLE IF EXISTS ONLY public.customers DROP CONSTRAINT IF EXISTS customers_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_subscriptions DROP CONSTRAINT IF EXISTS customer_subscriptions_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_orders DROP CONSTRAINT IF EXISTS customer_orders_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_order_items DROP CONSTRAINT IF EXISTS customer_order_items_pkey;
ALTER TABLE IF EXISTS ONLY public.customer_loyalty_points DROP CONSTRAINT IF EXISTS customer_loyalty_points_pkey;
ALTER TABLE IF EXISTS ONLY public.commission_agents DROP CONSTRAINT IF EXISTS commission_agents_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_pkey;
ALTER TABLE IF EXISTS ONLY public.attendance DROP CONSTRAINT IF EXISTS attendance_pkey;
ALTER TABLE IF EXISTS ONLY public.account_transactions DROP CONSTRAINT IF EXISTS account_transactions_pkey;
ALTER TABLE IF EXISTS ONLY public.tasks DROP CONSTRAINT IF EXISTS _tenant_task_number_uc;
ALTER TABLE IF EXISTS ONLY public.stocks DROP CONSTRAINT IF EXISTS _tenant_material_site_uc;
ALTER TABLE IF EXISTS ONLY public.item_stocks DROP CONSTRAINT IF EXISTS _tenant_item_site_uc;
ALTER TABLE IF EXISTS ONLY public.inventory_adjustments DROP CONSTRAINT IF EXISTS _tenant_adjustment_number_uc;
ALTER TABLE IF EXISTS ONLY auth.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY auth.users DROP CONSTRAINT IF EXISTS users_phone_key;
ALTER TABLE IF EXISTS ONLY auth.sso_providers DROP CONSTRAINT IF EXISTS sso_providers_pkey;
ALTER TABLE IF EXISTS ONLY auth.sso_domains DROP CONSTRAINT IF EXISTS sso_domains_pkey;
ALTER TABLE IF EXISTS ONLY auth.sessions DROP CONSTRAINT IF EXISTS sessions_pkey;
ALTER TABLE IF EXISTS ONLY auth.schema_migrations DROP CONSTRAINT IF EXISTS schema_migrations_pkey;
ALTER TABLE IF EXISTS ONLY auth.saml_relay_states DROP CONSTRAINT IF EXISTS saml_relay_states_pkey;
ALTER TABLE IF EXISTS ONLY auth.saml_providers DROP CONSTRAINT IF EXISTS saml_providers_pkey;
ALTER TABLE IF EXISTS ONLY auth.saml_providers DROP CONSTRAINT IF EXISTS saml_providers_entity_id_key;
ALTER TABLE IF EXISTS ONLY auth.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_token_unique;
ALTER TABLE IF EXISTS ONLY auth.refresh_tokens DROP CONSTRAINT IF EXISTS refresh_tokens_pkey;
ALTER TABLE IF EXISTS ONLY auth.one_time_tokens DROP CONSTRAINT IF EXISTS one_time_tokens_pkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_consents DROP CONSTRAINT IF EXISTS oauth_consents_user_client_unique;
ALTER TABLE IF EXISTS ONLY auth.oauth_consents DROP CONSTRAINT IF EXISTS oauth_consents_pkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_clients DROP CONSTRAINT IF EXISTS oauth_clients_pkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_authorizations DROP CONSTRAINT IF EXISTS oauth_authorizations_pkey;
ALTER TABLE IF EXISTS ONLY auth.oauth_authorizations DROP CONSTRAINT IF EXISTS oauth_authorizations_authorization_id_key;
ALTER TABLE IF EXISTS ONLY auth.oauth_authorizations DROP CONSTRAINT IF EXISTS oauth_authorizations_authorization_code_key;
ALTER TABLE IF EXISTS ONLY auth.mfa_factors DROP CONSTRAINT IF EXISTS mfa_factors_pkey;
ALTER TABLE IF EXISTS ONLY auth.mfa_factors DROP CONSTRAINT IF EXISTS mfa_factors_last_challenged_at_key;
ALTER TABLE IF EXISTS ONLY auth.mfa_challenges DROP CONSTRAINT IF EXISTS mfa_challenges_pkey;
ALTER TABLE IF EXISTS ONLY auth.mfa_amr_claims DROP CONSTRAINT IF EXISTS mfa_amr_claims_session_id_authentication_method_pkey;
ALTER TABLE IF EXISTS ONLY auth.instances DROP CONSTRAINT IF EXISTS instances_pkey;
ALTER TABLE IF EXISTS ONLY auth.identities DROP CONSTRAINT IF EXISTS identities_provider_id_provider_unique;
ALTER TABLE IF EXISTS ONLY auth.identities DROP CONSTRAINT IF EXISTS identities_pkey;
ALTER TABLE IF EXISTS ONLY auth.flow_state DROP CONSTRAINT IF EXISTS flow_state_pkey;
ALTER TABLE IF EXISTS ONLY auth.audit_log_entries DROP CONSTRAINT IF EXISTS audit_log_entries_pkey;
ALTER TABLE IF EXISTS ONLY auth.mfa_amr_claims DROP CONSTRAINT IF EXISTS amr_id_pk;
ALTER TABLE IF EXISTS public.vendors ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.vendor_payments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.transfers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.tenants ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.tasks ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.task_updates ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.task_media ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.task_materials ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.subscription_plans ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.subscription_payments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.subscription_deliveries ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.stocks ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.stock_movements ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sites ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sales_orders ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sales_order_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.salary_slips ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.purchase_requests ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.purchase_bills ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.purchase_bill_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.payroll_payments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.payment_allocations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.password_reset_tokens ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.materials ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.loyalty_transactions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.loyalty_programs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.item_stocks ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.item_stock_movements ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.item_images ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.item_groups ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.item_categories ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoices ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice_commissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.inventory_adjustments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.inventory_adjustment_lines ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.expenses ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.expense_categories ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.employees ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.delivery_day_notes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.delivery_challans ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.delivery_challan_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_subscriptions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_orders ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_order_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.customer_loyalty_points ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.commission_agents ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bank_accounts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.attendance ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.account_transactions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS auth.refresh_tokens ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS storage.vector_indexes;
DROP TABLE IF EXISTS storage.s3_multipart_uploads_parts;
DROP TABLE IF EXISTS storage.s3_multipart_uploads;
DROP TABLE IF EXISTS storage.prefixes;
DROP TABLE IF EXISTS storage.objects;
DROP TABLE IF EXISTS storage.migrations;
DROP TABLE IF EXISTS storage.buckets_vectors;
DROP TABLE IF EXISTS storage.buckets_analytics;
DROP TABLE IF EXISTS storage.buckets;
DROP TABLE IF EXISTS realtime.subscription;
DROP TABLE IF EXISTS realtime.schema_migrations;
DROP TABLE IF EXISTS realtime.messages;
DROP SEQUENCE IF EXISTS public.vendors_id_seq;
DROP TABLE IF EXISTS public.vendors;
DROP SEQUENCE IF EXISTS public.vendor_payments_id_seq;
DROP TABLE IF EXISTS public.vendor_payments;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP SEQUENCE IF EXISTS public.transfers_id_seq;
DROP TABLE IF EXISTS public.transfers;
DROP SEQUENCE IF EXISTS public.tenants_id_seq;
DROP TABLE IF EXISTS public.tenants;
DROP SEQUENCE IF EXISTS public.tasks_id_seq;
DROP TABLE IF EXISTS public.tasks;
DROP SEQUENCE IF EXISTS public.task_updates_id_seq;
DROP TABLE IF EXISTS public.task_updates;
DROP SEQUENCE IF EXISTS public.task_media_id_seq;
DROP TABLE IF EXISTS public.task_media;
DROP SEQUENCE IF EXISTS public.task_materials_id_seq;
DROP TABLE IF EXISTS public.task_materials;
DROP SEQUENCE IF EXISTS public.subscription_plans_id_seq;
DROP TABLE IF EXISTS public.subscription_plans;
DROP SEQUENCE IF EXISTS public.subscription_payments_id_seq;
DROP TABLE IF EXISTS public.subscription_payments;
DROP SEQUENCE IF EXISTS public.subscription_deliveries_id_seq;
DROP TABLE IF EXISTS public.subscription_deliveries;
DROP SEQUENCE IF EXISTS public.stocks_id_seq;
DROP TABLE IF EXISTS public.stocks;
DROP SEQUENCE IF EXISTS public.stock_movements_id_seq;
DROP TABLE IF EXISTS public.stock_movements;
DROP SEQUENCE IF EXISTS public.sites_id_seq;
DROP TABLE IF EXISTS public.sites;
DROP SEQUENCE IF EXISTS public.sales_orders_id_seq;
DROP TABLE IF EXISTS public.sales_orders;
DROP SEQUENCE IF EXISTS public.sales_order_items_id_seq;
DROP TABLE IF EXISTS public.sales_order_items;
DROP SEQUENCE IF EXISTS public.salary_slips_id_seq;
DROP TABLE IF EXISTS public.salary_slips;
DROP SEQUENCE IF EXISTS public.purchase_requests_id_seq;
DROP TABLE IF EXISTS public.purchase_requests;
DROP SEQUENCE IF EXISTS public.purchase_bills_id_seq;
DROP TABLE IF EXISTS public.purchase_bills;
DROP SEQUENCE IF EXISTS public.purchase_bill_items_id_seq;
DROP TABLE IF EXISTS public.purchase_bill_items;
DROP SEQUENCE IF EXISTS public.payroll_payments_id_seq;
DROP TABLE IF EXISTS public.payroll_payments;
DROP SEQUENCE IF EXISTS public.payment_allocations_id_seq;
DROP TABLE IF EXISTS public.payment_allocations;
DROP SEQUENCE IF EXISTS public.password_reset_tokens_id_seq;
DROP TABLE IF EXISTS public.password_reset_tokens;
DROP SEQUENCE IF EXISTS public.materials_id_seq;
DROP TABLE IF EXISTS public.materials;
DROP SEQUENCE IF EXISTS public.loyalty_transactions_id_seq;
DROP TABLE IF EXISTS public.loyalty_transactions;
DROP SEQUENCE IF EXISTS public.loyalty_programs_id_seq;
DROP TABLE IF EXISTS public.loyalty_programs;
DROP SEQUENCE IF EXISTS public.items_id_seq;
DROP TABLE IF EXISTS public.items;
DROP SEQUENCE IF EXISTS public.item_stocks_id_seq;
DROP TABLE IF EXISTS public.item_stocks;
DROP SEQUENCE IF EXISTS public.item_stock_movements_id_seq;
DROP TABLE IF EXISTS public.item_stock_movements;
DROP SEQUENCE IF EXISTS public.item_images_id_seq;
DROP TABLE IF EXISTS public.item_images;
DROP SEQUENCE IF EXISTS public.item_groups_id_seq;
DROP TABLE IF EXISTS public.item_groups;
DROP SEQUENCE IF EXISTS public.item_categories_id_seq;
DROP TABLE IF EXISTS public.item_categories;
DROP SEQUENCE IF EXISTS public.invoices_id_seq;
DROP TABLE IF EXISTS public.invoices;
DROP SEQUENCE IF EXISTS public.invoice_items_id_seq;
DROP TABLE IF EXISTS public.invoice_items;
DROP SEQUENCE IF EXISTS public.invoice_commissions_id_seq;
DROP TABLE IF EXISTS public.invoice_commissions;
DROP SEQUENCE IF EXISTS public.inventory_adjustments_id_seq;
DROP TABLE IF EXISTS public.inventory_adjustments;
DROP SEQUENCE IF EXISTS public.inventory_adjustment_lines_id_seq;
DROP TABLE IF EXISTS public.inventory_adjustment_lines;
DROP SEQUENCE IF EXISTS public.expenses_id_seq;
DROP TABLE IF EXISTS public.expenses;
DROP SEQUENCE IF EXISTS public.expense_categories_id_seq;
DROP TABLE IF EXISTS public.expense_categories;
DROP SEQUENCE IF EXISTS public.employees_id_seq;
DROP TABLE IF EXISTS public.employees;
DROP SEQUENCE IF EXISTS public.delivery_day_notes_id_seq;
DROP TABLE IF EXISTS public.delivery_day_notes;
DROP SEQUENCE IF EXISTS public.delivery_challans_id_seq;
DROP TABLE IF EXISTS public.delivery_challans;
DROP SEQUENCE IF EXISTS public.delivery_challan_items_id_seq;
DROP TABLE IF EXISTS public.delivery_challan_items;
DROP SEQUENCE IF EXISTS public.customers_id_seq;
DROP TABLE IF EXISTS public.customers;
DROP SEQUENCE IF EXISTS public.customer_subscriptions_id_seq;
DROP TABLE IF EXISTS public.customer_subscriptions;
DROP SEQUENCE IF EXISTS public.customer_orders_id_seq;
DROP TABLE IF EXISTS public.customer_orders;
DROP SEQUENCE IF EXISTS public.customer_order_items_id_seq;
DROP TABLE IF EXISTS public.customer_order_items;
DROP SEQUENCE IF EXISTS public.customer_loyalty_points_id_seq;
DROP TABLE IF EXISTS public.customer_loyalty_points;
DROP SEQUENCE IF EXISTS public.commission_agents_id_seq;
DROP TABLE IF EXISTS public.commission_agents;
DROP SEQUENCE IF EXISTS public.bank_accounts_id_seq;
DROP TABLE IF EXISTS public.bank_accounts;
DROP SEQUENCE IF EXISTS public.attendance_id_seq;
DROP TABLE IF EXISTS public.attendance;
DROP SEQUENCE IF EXISTS public.account_transactions_id_seq;
DROP TABLE IF EXISTS public.account_transactions;
DROP TABLE IF EXISTS auth.users;
DROP TABLE IF EXISTS auth.sso_providers;
DROP TABLE IF EXISTS auth.sso_domains;
DROP TABLE IF EXISTS auth.sessions;
DROP TABLE IF EXISTS auth.schema_migrations;
DROP TABLE IF EXISTS auth.saml_relay_states;
DROP TABLE IF EXISTS auth.saml_providers;
DROP SEQUENCE IF EXISTS auth.refresh_tokens_id_seq;
DROP TABLE IF EXISTS auth.refresh_tokens;
DROP TABLE IF EXISTS auth.one_time_tokens;
DROP TABLE IF EXISTS auth.oauth_consents;
DROP TABLE IF EXISTS auth.oauth_clients;
DROP TABLE IF EXISTS auth.oauth_authorizations;
DROP TABLE IF EXISTS auth.mfa_factors;
DROP TABLE IF EXISTS auth.mfa_challenges;
DROP TABLE IF EXISTS auth.mfa_amr_claims;
DROP TABLE IF EXISTS auth.instances;
DROP TABLE IF EXISTS auth.identities;
DROP TABLE IF EXISTS auth.flow_state;
DROP TABLE IF EXISTS auth.audit_log_entries;
DROP FUNCTION IF EXISTS storage.update_updated_at_column();
DROP FUNCTION IF EXISTS storage.search_v2(prefix text, bucket_name text, limits integer, levels integer, start_after text, sort_order text, sort_column text, sort_column_after text);
DROP FUNCTION IF EXISTS storage.search_v1_optimised(prefix text, bucketname text, limits integer, levels integer, offsets integer, search text, sortcolumn text, sortorder text);
DROP FUNCTION IF EXISTS storage.search_legacy_v1(prefix text, bucketname text, limits integer, levels integer, offsets integer, search text, sortcolumn text, sortorder text);
DROP FUNCTION IF EXISTS storage.search(prefix text, bucketname text, limits integer, levels integer, offsets integer, search text, sortcolumn text, sortorder text);
DROP FUNCTION IF EXISTS storage.prefixes_insert_trigger();
DROP FUNCTION IF EXISTS storage.prefixes_delete_cleanup();
DROP FUNCTION IF EXISTS storage.operation();
DROP FUNCTION IF EXISTS storage.objects_update_prefix_trigger();
DROP FUNCTION IF EXISTS storage.objects_update_level_trigger();
DROP FUNCTION IF EXISTS storage.objects_update_cleanup();
DROP FUNCTION IF EXISTS storage.objects_insert_prefix_trigger();
DROP FUNCTION IF EXISTS storage.objects_delete_cleanup();
DROP FUNCTION IF EXISTS storage.lock_top_prefixes(bucket_ids text[], names text[]);
DROP FUNCTION IF EXISTS storage.list_objects_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer, start_after text, next_token text);
DROP FUNCTION IF EXISTS storage.list_multipart_uploads_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer, next_key_token text, next_upload_token text);
DROP FUNCTION IF EXISTS storage.get_size_by_bucket();
DROP FUNCTION IF EXISTS storage.get_prefixes(name text);
DROP FUNCTION IF EXISTS storage.get_prefix(name text);
DROP FUNCTION IF EXISTS storage.get_level(name text);
DROP FUNCTION IF EXISTS storage.foldername(name text);
DROP FUNCTION IF EXISTS storage.filename(name text);
DROP FUNCTION IF EXISTS storage.extension(name text);
DROP FUNCTION IF EXISTS storage.enforce_bucket_name_length();
DROP FUNCTION IF EXISTS storage.delete_prefix_hierarchy_trigger();
DROP FUNCTION IF EXISTS storage.delete_prefix(_bucket_id text, _name text);
DROP FUNCTION IF EXISTS storage.delete_leaf_prefixes(bucket_ids text[], names text[]);
DROP FUNCTION IF EXISTS storage.can_insert_object(bucketid text, name text, owner uuid, metadata jsonb);
DROP FUNCTION IF EXISTS storage.add_prefixes(_bucket_id text, _name text);
DROP FUNCTION IF EXISTS realtime.topic();
DROP FUNCTION IF EXISTS realtime.to_regrole(role_name text);
DROP FUNCTION IF EXISTS realtime.subscription_check_filters();
DROP FUNCTION IF EXISTS realtime.send(payload jsonb, event text, topic text, private boolean);
DROP FUNCTION IF EXISTS realtime.quote_wal2json(entity regclass);
DROP FUNCTION IF EXISTS realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer);
DROP FUNCTION IF EXISTS realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]);
DROP FUNCTION IF EXISTS realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text);
DROP FUNCTION IF EXISTS realtime."cast"(val text, type_ regtype);
DROP FUNCTION IF EXISTS realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]);
DROP FUNCTION IF EXISTS realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text);
DROP FUNCTION IF EXISTS realtime.apply_rls(wal jsonb, max_record_bytes integer);
DROP FUNCTION IF EXISTS pgbouncer.get_auth(p_usename text);
DROP FUNCTION IF EXISTS extensions.set_graphql_placeholder();
DROP FUNCTION IF EXISTS extensions.pgrst_drop_watch();
DROP FUNCTION IF EXISTS extensions.pgrst_ddl_watch();
DROP FUNCTION IF EXISTS extensions.grant_pg_net_access();
DROP FUNCTION IF EXISTS extensions.grant_pg_graphql_access();
DROP FUNCTION IF EXISTS extensions.grant_pg_cron_access();
DROP FUNCTION IF EXISTS auth.uid();
DROP FUNCTION IF EXISTS auth.role();
DROP FUNCTION IF EXISTS auth.jwt();
DROP FUNCTION IF EXISTS auth.email();
DROP TYPE IF EXISTS storage.buckettype;
DROP TYPE IF EXISTS realtime.wal_rls;
DROP TYPE IF EXISTS realtime.wal_column;
DROP TYPE IF EXISTS realtime.user_defined_filter;
DROP TYPE IF EXISTS realtime.equality_op;
DROP TYPE IF EXISTS realtime.action;
DROP TYPE IF EXISTS auth.one_time_token_type;
DROP TYPE IF EXISTS auth.oauth_response_type;
DROP TYPE IF EXISTS auth.oauth_registration_type;
DROP TYPE IF EXISTS auth.oauth_client_type;
DROP TYPE IF EXISTS auth.oauth_authorization_status;
DROP TYPE IF EXISTS auth.factor_type;
DROP TYPE IF EXISTS auth.factor_status;
DROP TYPE IF EXISTS auth.code_challenge_method;
DROP TYPE IF EXISTS auth.aal_level;
DROP EXTENSION IF EXISTS "uuid-ossp";
DROP EXTENSION IF EXISTS supabase_vault;
DROP EXTENSION IF EXISTS pgcrypto;
DROP EXTENSION IF EXISTS pg_stat_statements;
DROP EXTENSION IF EXISTS pg_graphql;
DROP SCHEMA IF EXISTS vault;
DROP SCHEMA IF EXISTS storage;
DROP SCHEMA IF EXISTS realtime;
DROP SCHEMA IF EXISTS pgbouncer;
DROP SCHEMA IF EXISTS graphql_public;
DROP SCHEMA IF EXISTS graphql;
DROP SCHEMA IF EXISTS extensions;
DROP SCHEMA IF EXISTS auth;
--
-- Name: auth; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA auth;


--
-- Name: extensions; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA extensions;


--
-- Name: graphql; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA graphql;


--
-- Name: graphql_public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA graphql_public;


--
-- Name: pgbouncer; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA pgbouncer;


--
-- Name: realtime; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA realtime;


--
-- Name: storage; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA storage;


--
-- Name: vault; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA vault;


--
-- Name: pg_graphql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_graphql WITH SCHEMA graphql;


--
-- Name: EXTENSION pg_graphql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_graphql IS 'pg_graphql: GraphQL support';


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA extensions;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: supabase_vault; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS supabase_vault WITH SCHEMA vault;


--
-- Name: EXTENSION supabase_vault; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION supabase_vault IS 'Supabase Vault Extension';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA extensions;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: aal_level; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.aal_level AS ENUM (
    'aal1',
    'aal2',
    'aal3'
);


--
-- Name: code_challenge_method; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.code_challenge_method AS ENUM (
    's256',
    'plain'
);


--
-- Name: factor_status; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.factor_status AS ENUM (
    'unverified',
    'verified'
);


--
-- Name: factor_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.factor_type AS ENUM (
    'totp',
    'webauthn',
    'phone'
);


--
-- Name: oauth_authorization_status; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_authorization_status AS ENUM (
    'pending',
    'approved',
    'denied',
    'expired'
);


--
-- Name: oauth_client_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_client_type AS ENUM (
    'public',
    'confidential'
);


--
-- Name: oauth_registration_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_registration_type AS ENUM (
    'dynamic',
    'manual'
);


--
-- Name: oauth_response_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.oauth_response_type AS ENUM (
    'code'
);


--
-- Name: one_time_token_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE auth.one_time_token_type AS ENUM (
    'confirmation_token',
    'reauthentication_token',
    'recovery_token',
    'email_change_token_new',
    'email_change_token_current',
    'phone_change_token'
);


--
-- Name: action; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.action AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE',
    'TRUNCATE',
    'ERROR'
);


--
-- Name: equality_op; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.equality_op AS ENUM (
    'eq',
    'neq',
    'lt',
    'lte',
    'gt',
    'gte',
    'in'
);


--
-- Name: user_defined_filter; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.user_defined_filter AS (
	column_name text,
	op realtime.equality_op,
	value text
);


--
-- Name: wal_column; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.wal_column AS (
	name text,
	type_name text,
	type_oid oid,
	value jsonb,
	is_pkey boolean,
	is_selectable boolean
);


--
-- Name: wal_rls; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE realtime.wal_rls AS (
	wal jsonb,
	is_rls_enabled boolean,
	subscription_ids uuid[],
	errors text[]
);


--
-- Name: buckettype; Type: TYPE; Schema: storage; Owner: -
--

CREATE TYPE storage.buckettype AS ENUM (
    'STANDARD',
    'ANALYTICS',
    'VECTOR'
);


--
-- Name: email(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.email() RETURNS text
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.email', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'email')
  )::text
$$;


--
-- Name: FUNCTION email(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION auth.email() IS 'Deprecated. Use auth.jwt() -> ''email'' instead.';


--
-- Name: jwt(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.jwt() RETURNS jsonb
    LANGUAGE sql STABLE
    AS $$
  select 
    coalesce(
        nullif(current_setting('request.jwt.claim', true), ''),
        nullif(current_setting('request.jwt.claims', true), '')
    )::jsonb
$$;


--
-- Name: role(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.role() RETURNS text
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.role', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
  )::text
$$;


--
-- Name: FUNCTION role(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION auth.role() IS 'Deprecated. Use auth.jwt() -> ''role'' instead.';


--
-- Name: uid(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION auth.uid() RETURNS uuid
    LANGUAGE sql STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
  )::uuid
$$;


--
-- Name: FUNCTION uid(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION auth.uid() IS 'Deprecated. Use auth.jwt() -> ''sub'' instead.';


--
-- Name: grant_pg_cron_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.grant_pg_cron_access() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  IF EXISTS (
    SELECT
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_cron'
  )
  THEN
    grant usage on schema cron to postgres with grant option;

    alter default privileges in schema cron grant all on tables to postgres with grant option;
    alter default privileges in schema cron grant all on functions to postgres with grant option;
    alter default privileges in schema cron grant all on sequences to postgres with grant option;

    alter default privileges for user supabase_admin in schema cron grant all
        on sequences to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on tables to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on functions to postgres with grant option;

    grant all privileges on all tables in schema cron to postgres with grant option;
    revoke all on table cron.job from postgres;
    grant select on table cron.job to postgres with grant option;
  END IF;
END;
$$;


--
-- Name: FUNCTION grant_pg_cron_access(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.grant_pg_cron_access() IS 'Grants access to pg_cron';


--
-- Name: grant_pg_graphql_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.grant_pg_graphql_access() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $_$
DECLARE
    func_is_graphql_resolve bool;
BEGIN
    func_is_graphql_resolve = (
        SELECT n.proname = 'resolve'
        FROM pg_event_trigger_ddl_commands() AS ev
        LEFT JOIN pg_catalog.pg_proc AS n
        ON ev.objid = n.oid
    );

    IF func_is_graphql_resolve
    THEN
        -- Update public wrapper to pass all arguments through to the pg_graphql resolve func
        DROP FUNCTION IF EXISTS graphql_public.graphql;
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language sql
        as $$
            select graphql.resolve(
                query := query,
                variables := coalesce(variables, '{}'),
                "operationName" := "operationName",
                extensions := extensions
            );
        $$;

        -- This hook executes when `graphql.resolve` is created. That is not necessarily the last
        -- function in the extension so we need to grant permissions on existing entities AND
        -- update default permissions to any others that are created after `graphql.resolve`
        grant usage on schema graphql to postgres, anon, authenticated, service_role;
        grant select on all tables in schema graphql to postgres, anon, authenticated, service_role;
        grant execute on all functions in schema graphql to postgres, anon, authenticated, service_role;
        grant all on all sequences in schema graphql to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on tables to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on functions to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on sequences to postgres, anon, authenticated, service_role;

        -- Allow postgres role to allow granting usage on graphql and graphql_public schemas to custom roles
        grant usage on schema graphql_public to postgres with grant option;
        grant usage on schema graphql to postgres with grant option;
    END IF;

END;
$_$;


--
-- Name: FUNCTION grant_pg_graphql_access(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.grant_pg_graphql_access() IS 'Grants access to pg_graphql';


--
-- Name: grant_pg_net_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.grant_pg_net_access() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_net'
  )
  THEN
    IF NOT EXISTS (
      SELECT 1
      FROM pg_roles
      WHERE rolname = 'supabase_functions_admin'
    )
    THEN
      CREATE USER supabase_functions_admin NOINHERIT CREATEROLE LOGIN NOREPLICATION;
    END IF;

    GRANT USAGE ON SCHEMA net TO supabase_functions_admin, postgres, anon, authenticated, service_role;

    IF EXISTS (
      SELECT FROM pg_extension
      WHERE extname = 'pg_net'
      -- all versions in use on existing projects as of 2025-02-20
      -- version 0.12.0 onwards don't need these applied
      AND extversion IN ('0.2', '0.6', '0.7', '0.7.1', '0.8', '0.10.0', '0.11.0')
    ) THEN
      ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;
      ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;

      ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;
      ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;

      REVOKE ALL ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;
      REVOKE ALL ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;

      GRANT EXECUTE ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
      GRANT EXECUTE ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
    END IF;
  END IF;
END;
$$;


--
-- Name: FUNCTION grant_pg_net_access(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.grant_pg_net_access() IS 'Grants access to pg_net';


--
-- Name: pgrst_ddl_watch(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.pgrst_ddl_watch() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN SELECT * FROM pg_event_trigger_ddl_commands()
  LOOP
    IF cmd.command_tag IN (
      'CREATE SCHEMA', 'ALTER SCHEMA'
    , 'CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO', 'ALTER TABLE'
    , 'CREATE FOREIGN TABLE', 'ALTER FOREIGN TABLE'
    , 'CREATE VIEW', 'ALTER VIEW'
    , 'CREATE MATERIALIZED VIEW', 'ALTER MATERIALIZED VIEW'
    , 'CREATE FUNCTION', 'ALTER FUNCTION'
    , 'CREATE TRIGGER'
    , 'CREATE TYPE', 'ALTER TYPE'
    , 'CREATE RULE'
    , 'COMMENT'
    )
    -- don't notify in case of CREATE TEMP table or other objects created on pg_temp
    AND cmd.schema_name is distinct from 'pg_temp'
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


--
-- Name: pgrst_drop_watch(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.pgrst_drop_watch() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  obj record;
BEGIN
  FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
  LOOP
    IF obj.object_type IN (
      'schema'
    , 'table'
    , 'foreign table'
    , 'view'
    , 'materialized view'
    , 'function'
    , 'trigger'
    , 'type'
    , 'rule'
    )
    AND obj.is_temporary IS false -- no pg_temp objects
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


--
-- Name: set_graphql_placeholder(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION extensions.set_graphql_placeholder() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $_$
    DECLARE
    graphql_is_dropped bool;
    BEGIN
    graphql_is_dropped = (
        SELECT ev.schema_name = 'graphql_public'
        FROM pg_event_trigger_dropped_objects() AS ev
        WHERE ev.schema_name = 'graphql_public'
    );

    IF graphql_is_dropped
    THEN
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language plpgsql
        as $$
            DECLARE
                server_version float;
            BEGIN
                server_version = (SELECT (SPLIT_PART((select version()), ' ', 2))::float);

                IF server_version >= 14 THEN
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql extension is not enabled.'
                            )
                        )
                    );
                ELSE
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql is only available on projects running Postgres 14 onwards.'
                            )
                        )
                    );
                END IF;
            END;
        $$;
    END IF;

    END;
$_$;


--
-- Name: FUNCTION set_graphql_placeholder(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION extensions.set_graphql_placeholder() IS 'Reintroduces placeholder function for graphql_public.graphql';


--
-- Name: get_auth(text); Type: FUNCTION; Schema: pgbouncer; Owner: -
--

CREATE FUNCTION pgbouncer.get_auth(p_usename text) RETURNS TABLE(username text, password text)
    LANGUAGE plpgsql SECURITY DEFINER
    AS $_$
begin
    raise debug 'PgBouncer auth request: %', p_usename;

    return query
    select 
        rolname::text, 
        case when rolvaliduntil < now() 
            then null 
            else rolpassword::text 
        end 
    from pg_authid 
    where rolname=$1 and rolcanlogin;
end;
$_$;


--
-- Name: apply_rls(jsonb, integer); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.apply_rls(wal jsonb, max_record_bytes integer DEFAULT (1024 * 1024)) RETURNS SETOF realtime.wal_rls
    LANGUAGE plpgsql
    AS $$
declare
-- Regclass of the table e.g. public.notes
entity_ regclass = (quote_ident(wal ->> 'schema') || '.' || quote_ident(wal ->> 'table'))::regclass;

-- I, U, D, T: insert, update ...
action realtime.action = (
    case wal ->> 'action'
        when 'I' then 'INSERT'
        when 'U' then 'UPDATE'
        when 'D' then 'DELETE'
        else 'ERROR'
    end
);

-- Is row level security enabled for the table
is_rls_enabled bool = relrowsecurity from pg_class where oid = entity_;

subscriptions realtime.subscription[] = array_agg(subs)
    from
        realtime.subscription subs
    where
        subs.entity = entity_;

-- Subscription vars
roles regrole[] = array_agg(distinct us.claims_role::text)
    from
        unnest(subscriptions) us;

working_role regrole;
claimed_role regrole;
claims jsonb;

subscription_id uuid;
subscription_has_access bool;
visible_to_subscription_ids uuid[] = '{}';

-- structured info for wal's columns
columns realtime.wal_column[];
-- previous identity values for update/delete
old_columns realtime.wal_column[];

error_record_exceeds_max_size boolean = octet_length(wal::text) > max_record_bytes;

-- Primary jsonb output for record
output jsonb;

begin
perform set_config('role', null, true);

columns =
    array_agg(
        (
            x->>'name',
            x->>'type',
            x->>'typeoid',
            realtime.cast(
                (x->'value') #>> '{}',
                coalesce(
                    (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                    (x->>'type')::regtype
                )
            ),
            (pks ->> 'name') is not null,
            true
        )::realtime.wal_column
    )
    from
        jsonb_array_elements(wal -> 'columns') x
        left join jsonb_array_elements(wal -> 'pk') pks
            on (x ->> 'name') = (pks ->> 'name');

old_columns =
    array_agg(
        (
            x->>'name',
            x->>'type',
            x->>'typeoid',
            realtime.cast(
                (x->'value') #>> '{}',
                coalesce(
                    (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                    (x->>'type')::regtype
                )
            ),
            (pks ->> 'name') is not null,
            true
        )::realtime.wal_column
    )
    from
        jsonb_array_elements(wal -> 'identity') x
        left join jsonb_array_elements(wal -> 'pk') pks
            on (x ->> 'name') = (pks ->> 'name');

for working_role in select * from unnest(roles) loop

    -- Update `is_selectable` for columns and old_columns
    columns =
        array_agg(
            (
                c.name,
                c.type_name,
                c.type_oid,
                c.value,
                c.is_pkey,
                pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
            )::realtime.wal_column
        )
        from
            unnest(columns) c;

    old_columns =
            array_agg(
                (
                    c.name,
                    c.type_name,
                    c.type_oid,
                    c.value,
                    c.is_pkey,
                    pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
                )::realtime.wal_column
            )
            from
                unnest(old_columns) c;

    if action <> 'DELETE' and count(1) = 0 from unnest(columns) c where c.is_pkey then
        return next (
            jsonb_build_object(
                'schema', wal ->> 'schema',
                'table', wal ->> 'table',
                'type', action
            ),
            is_rls_enabled,
            -- subscriptions is already filtered by entity
            (select array_agg(s.subscription_id) from unnest(subscriptions) as s where claims_role = working_role),
            array['Error 400: Bad Request, no primary key']
        )::realtime.wal_rls;

    -- The claims role does not have SELECT permission to the primary key of entity
    elsif action <> 'DELETE' and sum(c.is_selectable::int) <> count(1) from unnest(columns) c where c.is_pkey then
        return next (
            jsonb_build_object(
                'schema', wal ->> 'schema',
                'table', wal ->> 'table',
                'type', action
            ),
            is_rls_enabled,
            (select array_agg(s.subscription_id) from unnest(subscriptions) as s where claims_role = working_role),
            array['Error 401: Unauthorized']
        )::realtime.wal_rls;

    else
        output = jsonb_build_object(
            'schema', wal ->> 'schema',
            'table', wal ->> 'table',
            'type', action,
            'commit_timestamp', to_char(
                ((wal ->> 'timestamp')::timestamptz at time zone 'utc'),
                'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'
            ),
            'columns', (
                select
                    jsonb_agg(
                        jsonb_build_object(
                            'name', pa.attname,
                            'type', pt.typname
                        )
                        order by pa.attnum asc
                    )
                from
                    pg_attribute pa
                    join pg_type pt
                        on pa.atttypid = pt.oid
                where
                    attrelid = entity_
                    and attnum > 0
                    and pg_catalog.has_column_privilege(working_role, entity_, pa.attname, 'SELECT')
            )
        )
        -- Add "record" key for insert and update
        || case
            when action in ('INSERT', 'UPDATE') then
                jsonb_build_object(
                    'record',
                    (
                        select
                            jsonb_object_agg(
                                -- if unchanged toast, get column name and value from old record
                                coalesce((c).name, (oc).name),
                                case
                                    when (c).name is null then (oc).value
                                    else (c).value
                                end
                            )
                        from
                            unnest(columns) c
                            full outer join unnest(old_columns) oc
                                on (c).name = (oc).name
                        where
                            coalesce((c).is_selectable, (oc).is_selectable)
                            and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                    )
                )
            else '{}'::jsonb
        end
        -- Add "old_record" key for update and delete
        || case
            when action = 'UPDATE' then
                jsonb_build_object(
                        'old_record',
                        (
                            select jsonb_object_agg((c).name, (c).value)
                            from unnest(old_columns) c
                            where
                                (c).is_selectable
                                and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                        )
                    )
            when action = 'DELETE' then
                jsonb_build_object(
                    'old_record',
                    (
                        select jsonb_object_agg((c).name, (c).value)
                        from unnest(old_columns) c
                        where
                            (c).is_selectable
                            and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                            and ( not is_rls_enabled or (c).is_pkey ) -- if RLS enabled, we can't secure deletes so filter to pkey
                    )
                )
            else '{}'::jsonb
        end;

        -- Create the prepared statement
        if is_rls_enabled and action <> 'DELETE' then
            if (select 1 from pg_prepared_statements where name = 'walrus_rls_stmt' limit 1) > 0 then
                deallocate walrus_rls_stmt;
            end if;
            execute realtime.build_prepared_statement_sql('walrus_rls_stmt', entity_, columns);
        end if;

        visible_to_subscription_ids = '{}';

        for subscription_id, claims in (
                select
                    subs.subscription_id,
                    subs.claims
                from
                    unnest(subscriptions) subs
                where
                    subs.entity = entity_
                    and subs.claims_role = working_role
                    and (
                        realtime.is_visible_through_filters(columns, subs.filters)
                        or (
                          action = 'DELETE'
                          and realtime.is_visible_through_filters(old_columns, subs.filters)
                        )
                    )
        ) loop

            if not is_rls_enabled or action = 'DELETE' then
                visible_to_subscription_ids = visible_to_subscription_ids || subscription_id;
            else
                -- Check if RLS allows the role to see the record
                perform
                    -- Trim leading and trailing quotes from working_role because set_config
                    -- doesn't recognize the role as valid if they are included
                    set_config('role', trim(both '"' from working_role::text), true),
                    set_config('request.jwt.claims', claims::text, true);

                execute 'execute walrus_rls_stmt' into subscription_has_access;

                if subscription_has_access then
                    visible_to_subscription_ids = visible_to_subscription_ids || subscription_id;
                end if;
            end if;
        end loop;

        perform set_config('role', null, true);

        return next (
            output,
            is_rls_enabled,
            visible_to_subscription_ids,
            case
                when error_record_exceeds_max_size then array['Error 413: Payload Too Large']
                else '{}'
            end
        )::realtime.wal_rls;

    end if;
end loop;

perform set_config('role', null, true);
end;
$$;


--
-- Name: broadcast_changes(text, text, text, text, text, record, record, text); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.broadcast_changes(topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text DEFAULT 'ROW'::text) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    -- Declare a variable to hold the JSONB representation of the row
    row_data jsonb := '{}'::jsonb;
BEGIN
    IF level = 'STATEMENT' THEN
        RAISE EXCEPTION 'function can only be triggered for each row, not for each statement';
    END IF;
    -- Check the operation type and handle accordingly
    IF operation = 'INSERT' OR operation = 'UPDATE' OR operation = 'DELETE' THEN
        row_data := jsonb_build_object('old_record', OLD, 'record', NEW, 'operation', operation, 'table', table_name, 'schema', table_schema);
        PERFORM realtime.send (row_data, event_name, topic_name);
    ELSE
        RAISE EXCEPTION 'Unexpected operation type: %', operation;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to process the row: %', SQLERRM;
END;

$$;


--
-- Name: build_prepared_statement_sql(text, regclass, realtime.wal_column[]); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.build_prepared_statement_sql(prepared_statement_name text, entity regclass, columns realtime.wal_column[]) RETURNS text
    LANGUAGE sql
    AS $$
      /*
      Builds a sql string that, if executed, creates a prepared statement to
      tests retrive a row from *entity* by its primary key columns.
      Example
          select realtime.build_prepared_statement_sql('public.notes', '{"id"}'::text[], '{"bigint"}'::text[])
      */
          select
      'prepare ' || prepared_statement_name || ' as
          select
              exists(
                  select
                      1
                  from
                      ' || entity || '
                  where
                      ' || string_agg(quote_ident(pkc.name) || '=' || quote_nullable(pkc.value #>> '{}') , ' and ') || '
              )'
          from
              unnest(columns) pkc
          where
              pkc.is_pkey
          group by
              entity
      $$;


--
-- Name: cast(text, regtype); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime."cast"(val text, type_ regtype) RETURNS jsonb
    LANGUAGE plpgsql IMMUTABLE
    AS $$
    declare
      res jsonb;
    begin
      execute format('select to_jsonb(%L::'|| type_::text || ')', val)  into res;
      return res;
    end
    $$;


--
-- Name: check_equality_op(realtime.equality_op, regtype, text, text); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.check_equality_op(op realtime.equality_op, type_ regtype, val_1 text, val_2 text) RETURNS boolean
    LANGUAGE plpgsql IMMUTABLE
    AS $$
      /*
      Casts *val_1* and *val_2* as type *type_* and check the *op* condition for truthiness
      */
      declare
          op_symbol text = (
              case
                  when op = 'eq' then '='
                  when op = 'neq' then '!='
                  when op = 'lt' then '<'
                  when op = 'lte' then '<='
                  when op = 'gt' then '>'
                  when op = 'gte' then '>='
                  when op = 'in' then '= any'
                  else 'UNKNOWN OP'
              end
          );
          res boolean;
      begin
          execute format(
              'select %L::'|| type_::text || ' ' || op_symbol
              || ' ( %L::'
              || (
                  case
                      when op = 'in' then type_::text || '[]'
                      else type_::text end
              )
              || ')', val_1, val_2) into res;
          return res;
      end;
      $$;


--
-- Name: is_visible_through_filters(realtime.wal_column[], realtime.user_defined_filter[]); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.is_visible_through_filters(columns realtime.wal_column[], filters realtime.user_defined_filter[]) RETURNS boolean
    LANGUAGE sql IMMUTABLE
    AS $_$
    /*
    Should the record be visible (true) or filtered out (false) after *filters* are applied
    */
        select
            -- Default to allowed when no filters present
            $2 is null -- no filters. this should not happen because subscriptions has a default
            or array_length($2, 1) is null -- array length of an empty array is null
            or bool_and(
                coalesce(
                    realtime.check_equality_op(
                        op:=f.op,
                        type_:=coalesce(
                            col.type_oid::regtype, -- null when wal2json version <= 2.4
                            col.type_name::regtype
                        ),
                        -- cast jsonb to text
                        val_1:=col.value #>> '{}',
                        val_2:=f.value
                    ),
                    false -- if null, filter does not match
                )
            )
        from
            unnest(filters) f
            join unnest(columns) col
                on f.column_name = col.name;
    $_$;


--
-- Name: list_changes(name, name, integer, integer); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.list_changes(publication name, slot_name name, max_changes integer, max_record_bytes integer) RETURNS SETOF realtime.wal_rls
    LANGUAGE sql
    SET log_min_messages TO 'fatal'
    AS $$
      with pub as (
        select
          concat_ws(
            ',',
            case when bool_or(pubinsert) then 'insert' else null end,
            case when bool_or(pubupdate) then 'update' else null end,
            case when bool_or(pubdelete) then 'delete' else null end
          ) as w2j_actions,
          coalesce(
            string_agg(
              realtime.quote_wal2json(format('%I.%I', schemaname, tablename)::regclass),
              ','
            ) filter (where ppt.tablename is not null and ppt.tablename not like '% %'),
            ''
          ) w2j_add_tables
        from
          pg_publication pp
          left join pg_publication_tables ppt
            on pp.pubname = ppt.pubname
        where
          pp.pubname = publication
        group by
          pp.pubname
        limit 1
      ),
      w2j as (
        select
          x.*, pub.w2j_add_tables
        from
          pub,
          pg_logical_slot_get_changes(
            slot_name, null, max_changes,
            'include-pk', 'true',
            'include-transaction', 'false',
            'include-timestamp', 'true',
            'include-type-oids', 'true',
            'format-version', '2',
            'actions', pub.w2j_actions,
            'add-tables', pub.w2j_add_tables
          ) x
      )
      select
        xyz.wal,
        xyz.is_rls_enabled,
        xyz.subscription_ids,
        xyz.errors
      from
        w2j,
        realtime.apply_rls(
          wal := w2j.data::jsonb,
          max_record_bytes := max_record_bytes
        ) xyz(wal, is_rls_enabled, subscription_ids, errors)
      where
        w2j.w2j_add_tables <> ''
        and xyz.subscription_ids[1] is not null
    $$;


--
-- Name: quote_wal2json(regclass); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.quote_wal2json(entity regclass) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
      select
        (
          select string_agg('' || ch,'')
          from unnest(string_to_array(nsp.nspname::text, null)) with ordinality x(ch, idx)
          where
            not (x.idx = 1 and x.ch = '"')
            and not (
              x.idx = array_length(string_to_array(nsp.nspname::text, null), 1)
              and x.ch = '"'
            )
        )
        || '.'
        || (
          select string_agg('' || ch,'')
          from unnest(string_to_array(pc.relname::text, null)) with ordinality x(ch, idx)
          where
            not (x.idx = 1 and x.ch = '"')
            and not (
              x.idx = array_length(string_to_array(nsp.nspname::text, null), 1)
              and x.ch = '"'
            )
          )
      from
        pg_class pc
        join pg_namespace nsp
          on pc.relnamespace = nsp.oid
      where
        pc.oid = entity
    $$;


--
-- Name: send(jsonb, text, text, boolean); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.send(payload jsonb, event text, topic text, private boolean DEFAULT true) RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  generated_id uuid;
  final_payload jsonb;
BEGIN
  BEGIN
    -- Generate a new UUID for the id
    generated_id := gen_random_uuid();

    -- Check if payload has an 'id' key, if not, add the generated UUID
    IF payload ? 'id' THEN
      final_payload := payload;
    ELSE
      final_payload := jsonb_set(payload, '{id}', to_jsonb(generated_id));
    END IF;

    -- Set the topic configuration
    EXECUTE format('SET LOCAL realtime.topic TO %L', topic);

    -- Attempt to insert the message
    INSERT INTO realtime.messages (id, payload, event, topic, private, extension)
    VALUES (generated_id, final_payload, event, topic, private, 'broadcast');
  EXCEPTION
    WHEN OTHERS THEN
      -- Capture and notify the error
      RAISE WARNING 'ErrorSendingBroadcastMessage: %', SQLERRM;
  END;
END;
$$;


--
-- Name: subscription_check_filters(); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.subscription_check_filters() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    /*
    Validates that the user defined filters for a subscription:
    - refer to valid columns that the claimed role may access
    - values are coercable to the correct column type
    */
    declare
        col_names text[] = coalesce(
                array_agg(c.column_name order by c.ordinal_position),
                '{}'::text[]
            )
            from
                information_schema.columns c
            where
                format('%I.%I', c.table_schema, c.table_name)::regclass = new.entity
                and pg_catalog.has_column_privilege(
                    (new.claims ->> 'role'),
                    format('%I.%I', c.table_schema, c.table_name)::regclass,
                    c.column_name,
                    'SELECT'
                );
        filter realtime.user_defined_filter;
        col_type regtype;

        in_val jsonb;
    begin
        for filter in select * from unnest(new.filters) loop
            -- Filtered column is valid
            if not filter.column_name = any(col_names) then
                raise exception 'invalid column for filter %', filter.column_name;
            end if;

            -- Type is sanitized and safe for string interpolation
            col_type = (
                select atttypid::regtype
                from pg_catalog.pg_attribute
                where attrelid = new.entity
                      and attname = filter.column_name
            );
            if col_type is null then
                raise exception 'failed to lookup type for column %', filter.column_name;
            end if;

            -- Set maximum number of entries for in filter
            if filter.op = 'in'::realtime.equality_op then
                in_val = realtime.cast(filter.value, (col_type::text || '[]')::regtype);
                if coalesce(jsonb_array_length(in_val), 0) > 100 then
                    raise exception 'too many values for `in` filter. Maximum 100';
                end if;
            else
                -- raises an exception if value is not coercable to type
                perform realtime.cast(filter.value, col_type);
            end if;

        end loop;

        -- Apply consistent order to filters so the unique constraint on
        -- (subscription_id, entity, filters) can't be tricked by a different filter order
        new.filters = coalesce(
            array_agg(f order by f.column_name, f.op, f.value),
            '{}'
        ) from unnest(new.filters) f;

        return new;
    end;
    $$;


--
-- Name: to_regrole(text); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.to_regrole(role_name text) RETURNS regrole
    LANGUAGE sql IMMUTABLE
    AS $$ select role_name::regrole $$;


--
-- Name: topic(); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION realtime.topic() RETURNS text
    LANGUAGE sql STABLE
    AS $$
select nullif(current_setting('realtime.topic', true), '')::text;
$$;


--
-- Name: add_prefixes(text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.add_prefixes(_bucket_id text, _name text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    prefixes text[];
BEGIN
    prefixes := "storage"."get_prefixes"("_name");

    IF array_length(prefixes, 1) > 0 THEN
        INSERT INTO storage.prefixes (name, bucket_id)
        SELECT UNNEST(prefixes) as name, "_bucket_id" ON CONFLICT DO NOTHING;
    END IF;
END;
$$;


--
-- Name: can_insert_object(text, text, uuid, jsonb); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.can_insert_object(bucketid text, name text, owner uuid, metadata jsonb) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  INSERT INTO "storage"."objects" ("bucket_id", "name", "owner", "metadata") VALUES (bucketid, name, owner, metadata);
  -- hack to rollback the successful insert
  RAISE sqlstate 'PT200' using
  message = 'ROLLBACK',
  detail = 'rollback successful insert';
END
$$;


--
-- Name: delete_leaf_prefixes(text[], text[]); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.delete_leaf_prefixes(bucket_ids text[], names text[]) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_rows_deleted integer;
BEGIN
    LOOP
        WITH candidates AS (
            SELECT DISTINCT
                t.bucket_id,
                unnest(storage.get_prefixes(t.name)) AS name
            FROM unnest(bucket_ids, names) AS t(bucket_id, name)
        ),
        uniq AS (
             SELECT
                 bucket_id,
                 name,
                 storage.get_level(name) AS level
             FROM candidates
             WHERE name <> ''
             GROUP BY bucket_id, name
        ),
        leaf AS (
             SELECT
                 p.bucket_id,
                 p.name,
                 p.level
             FROM storage.prefixes AS p
                  JOIN uniq AS u
                       ON u.bucket_id = p.bucket_id
                           AND u.name = p.name
                           AND u.level = p.level
             WHERE NOT EXISTS (
                 SELECT 1
                 FROM storage.objects AS o
                 WHERE o.bucket_id = p.bucket_id
                   AND o.level = p.level + 1
                   AND o.name COLLATE "C" LIKE p.name || '/%'
             )
             AND NOT EXISTS (
                 SELECT 1
                 FROM storage.prefixes AS c
                 WHERE c.bucket_id = p.bucket_id
                   AND c.level = p.level + 1
                   AND c.name COLLATE "C" LIKE p.name || '/%'
             )
        )
        DELETE
        FROM storage.prefixes AS p
            USING leaf AS l
        WHERE p.bucket_id = l.bucket_id
          AND p.name = l.name
          AND p.level = l.level;

        GET DIAGNOSTICS v_rows_deleted = ROW_COUNT;
        EXIT WHEN v_rows_deleted = 0;
    END LOOP;
END;
$$;


--
-- Name: delete_prefix(text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.delete_prefix(_bucket_id text, _name text) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- Check if we can delete the prefix
    IF EXISTS(
        SELECT FROM "storage"."prefixes"
        WHERE "prefixes"."bucket_id" = "_bucket_id"
          AND level = "storage"."get_level"("_name") + 1
          AND "prefixes"."name" COLLATE "C" LIKE "_name" || '/%'
        LIMIT 1
    )
    OR EXISTS(
        SELECT FROM "storage"."objects"
        WHERE "objects"."bucket_id" = "_bucket_id"
          AND "storage"."get_level"("objects"."name") = "storage"."get_level"("_name") + 1
          AND "objects"."name" COLLATE "C" LIKE "_name" || '/%'
        LIMIT 1
    ) THEN
    -- There are sub-objects, skip deletion
    RETURN false;
    ELSE
        DELETE FROM "storage"."prefixes"
        WHERE "prefixes"."bucket_id" = "_bucket_id"
          AND level = "storage"."get_level"("_name")
          AND "prefixes"."name" = "_name";
        RETURN true;
    END IF;
END;
$$;


--
-- Name: delete_prefix_hierarchy_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.delete_prefix_hierarchy_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    prefix text;
BEGIN
    prefix := "storage"."get_prefix"(OLD."name");

    IF coalesce(prefix, '') != '' THEN
        PERFORM "storage"."delete_prefix"(OLD."bucket_id", prefix);
    END IF;

    RETURN OLD;
END;
$$;


--
-- Name: enforce_bucket_name_length(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.enforce_bucket_name_length() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    if length(new.name) > 100 then
        raise exception 'bucket name "%" is too long (% characters). Max is 100.', new.name, length(new.name);
    end if;
    return new;
end;
$$;


--
-- Name: extension(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.extension(name text) RETURNS text
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
    _filename text;
BEGIN
    SELECT string_to_array(name, '/') INTO _parts;
    SELECT _parts[array_length(_parts,1)] INTO _filename;
    RETURN reverse(split_part(reverse(_filename), '.', 1));
END
$$;


--
-- Name: filename(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.filename(name text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
_parts text[];
BEGIN
	select string_to_array(name, '/') into _parts;
	return _parts[array_length(_parts,1)];
END
$$;


--
-- Name: foldername(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.foldername(name text) RETURNS text[]
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    _parts text[];
BEGIN
    -- Split on "/" to get path segments
    SELECT string_to_array(name, '/') INTO _parts;
    -- Return everything except the last segment
    RETURN _parts[1 : array_length(_parts,1) - 1];
END
$$;


--
-- Name: get_level(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_level(name text) RETURNS integer
    LANGUAGE sql IMMUTABLE STRICT
    AS $$
SELECT array_length(string_to_array("name", '/'), 1);
$$;


--
-- Name: get_prefix(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_prefix(name text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
SELECT
    CASE WHEN strpos("name", '/') > 0 THEN
             regexp_replace("name", '[\/]{1}[^\/]+\/?$', '')
         ELSE
             ''
        END;
$_$;


--
-- Name: get_prefixes(text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_prefixes(name text) RETURNS text[]
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
DECLARE
    parts text[];
    prefixes text[];
    prefix text;
BEGIN
    -- Split the name into parts by '/'
    parts := string_to_array("name", '/');
    prefixes := '{}';

    -- Construct the prefixes, stopping one level below the last part
    FOR i IN 1..array_length(parts, 1) - 1 LOOP
            prefix := array_to_string(parts[1:i], '/');
            prefixes := array_append(prefixes, prefix);
    END LOOP;

    RETURN prefixes;
END;
$$;


--
-- Name: get_size_by_bucket(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.get_size_by_bucket() RETURNS TABLE(size bigint, bucket_id text)
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
    return query
        select sum((metadata->>'size')::bigint) as size, obj.bucket_id
        from "storage".objects as obj
        group by obj.bucket_id;
END
$$;


--
-- Name: list_multipart_uploads_with_delimiter(text, text, text, integer, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.list_multipart_uploads_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer DEFAULT 100, next_key_token text DEFAULT ''::text, next_upload_token text DEFAULT ''::text) RETURNS TABLE(key text, id text, created_at timestamp with time zone)
    LANGUAGE plpgsql
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(key COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                        substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1)))
                    ELSE
                        key
                END AS key, id, created_at
            FROM
                storage.s3_multipart_uploads
            WHERE
                bucket_id = $5 AND
                key ILIKE $1 || ''%'' AND
                CASE
                    WHEN $4 != '''' AND $6 = '''' THEN
                        CASE
                            WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                                substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                key COLLATE "C" > $4
                            END
                    ELSE
                        true
                END AND
                CASE
                    WHEN $6 != '''' THEN
                        id COLLATE "C" > $6
                    ELSE
                        true
                    END
            ORDER BY
                key COLLATE "C" ASC, created_at ASC) as e order by key COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_key_token, bucket_id, next_upload_token;
END;
$_$;


--
-- Name: list_objects_with_delimiter(text, text, text, integer, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.list_objects_with_delimiter(bucket_id text, prefix_param text, delimiter_param text, max_keys integer DEFAULT 100, start_after text DEFAULT ''::text, next_token text DEFAULT ''::text) RETURNS TABLE(name text, id uuid, metadata jsonb, updated_at timestamp with time zone)
    LANGUAGE plpgsql
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(name COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(name from length($1) + 1)) > 0 THEN
                        substring(name from 1 for length($1) + position($2 IN substring(name from length($1) + 1)))
                    ELSE
                        name
                END AS name, id, metadata, updated_at
            FROM
                storage.objects
            WHERE
                bucket_id = $5 AND
                name ILIKE $1 || ''%'' AND
                CASE
                    WHEN $6 != '''' THEN
                    name COLLATE "C" > $6
                ELSE true END
                AND CASE
                    WHEN $4 != '''' THEN
                        CASE
                            WHEN position($2 IN substring(name from length($1) + 1)) > 0 THEN
                                substring(name from 1 for length($1) + position($2 IN substring(name from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                name COLLATE "C" > $4
                            END
                    ELSE
                        true
                END
            ORDER BY
                name COLLATE "C" ASC) as e order by name COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_token, bucket_id, start_after;
END;
$_$;


--
-- Name: lock_top_prefixes(text[], text[]); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.lock_top_prefixes(bucket_ids text[], names text[]) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_bucket text;
    v_top text;
BEGIN
    FOR v_bucket, v_top IN
        SELECT DISTINCT t.bucket_id,
            split_part(t.name, '/', 1) AS top
        FROM unnest(bucket_ids, names) AS t(bucket_id, name)
        WHERE t.name <> ''
        ORDER BY 1, 2
        LOOP
            PERFORM pg_advisory_xact_lock(hashtextextended(v_bucket || '/' || v_top, 0));
        END LOOP;
END;
$$;


--
-- Name: objects_delete_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_delete_cleanup() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_bucket_ids text[];
    v_names      text[];
BEGIN
    IF current_setting('storage.gc.prefixes', true) = '1' THEN
        RETURN NULL;
    END IF;

    PERFORM set_config('storage.gc.prefixes', '1', true);

    SELECT COALESCE(array_agg(d.bucket_id), '{}'),
           COALESCE(array_agg(d.name), '{}')
    INTO v_bucket_ids, v_names
    FROM deleted AS d
    WHERE d.name <> '';

    PERFORM storage.lock_top_prefixes(v_bucket_ids, v_names);
    PERFORM storage.delete_leaf_prefixes(v_bucket_ids, v_names);

    RETURN NULL;
END;
$$;


--
-- Name: objects_insert_prefix_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_insert_prefix_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    NEW.level := "storage"."get_level"(NEW."name");

    RETURN NEW;
END;
$$;


--
-- Name: objects_update_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_update_cleanup() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    -- NEW - OLD (destinations to create prefixes for)
    v_add_bucket_ids text[];
    v_add_names      text[];

    -- OLD - NEW (sources to prune)
    v_src_bucket_ids text[];
    v_src_names      text[];
BEGIN
    IF TG_OP <> 'UPDATE' THEN
        RETURN NULL;
    END IF;

    -- 1) Compute NEW−OLD (added paths) and OLD−NEW (moved-away paths)
    WITH added AS (
        SELECT n.bucket_id, n.name
        FROM new_rows n
        WHERE n.name <> '' AND position('/' in n.name) > 0
        EXCEPT
        SELECT o.bucket_id, o.name FROM old_rows o WHERE o.name <> ''
    ),
    moved AS (
         SELECT o.bucket_id, o.name
         FROM old_rows o
         WHERE o.name <> ''
         EXCEPT
         SELECT n.bucket_id, n.name FROM new_rows n WHERE n.name <> ''
    )
    SELECT
        -- arrays for ADDED (dest) in stable order
        COALESCE( (SELECT array_agg(a.bucket_id ORDER BY a.bucket_id, a.name) FROM added a), '{}' ),
        COALESCE( (SELECT array_agg(a.name      ORDER BY a.bucket_id, a.name) FROM added a), '{}' ),
        -- arrays for MOVED (src) in stable order
        COALESCE( (SELECT array_agg(m.bucket_id ORDER BY m.bucket_id, m.name) FROM moved m), '{}' ),
        COALESCE( (SELECT array_agg(m.name      ORDER BY m.bucket_id, m.name) FROM moved m), '{}' )
    INTO v_add_bucket_ids, v_add_names, v_src_bucket_ids, v_src_names;

    -- Nothing to do?
    IF (array_length(v_add_bucket_ids, 1) IS NULL) AND (array_length(v_src_bucket_ids, 1) IS NULL) THEN
        RETURN NULL;
    END IF;

    -- 2) Take per-(bucket, top) locks: ALL prefixes in consistent global order to prevent deadlocks
    DECLARE
        v_all_bucket_ids text[];
        v_all_names text[];
    BEGIN
        -- Combine source and destination arrays for consistent lock ordering
        v_all_bucket_ids := COALESCE(v_src_bucket_ids, '{}') || COALESCE(v_add_bucket_ids, '{}');
        v_all_names := COALESCE(v_src_names, '{}') || COALESCE(v_add_names, '{}');

        -- Single lock call ensures consistent global ordering across all transactions
        IF array_length(v_all_bucket_ids, 1) IS NOT NULL THEN
            PERFORM storage.lock_top_prefixes(v_all_bucket_ids, v_all_names);
        END IF;
    END;

    -- 3) Create destination prefixes (NEW−OLD) BEFORE pruning sources
    IF array_length(v_add_bucket_ids, 1) IS NOT NULL THEN
        WITH candidates AS (
            SELECT DISTINCT t.bucket_id, unnest(storage.get_prefixes(t.name)) AS name
            FROM unnest(v_add_bucket_ids, v_add_names) AS t(bucket_id, name)
            WHERE name <> ''
        )
        INSERT INTO storage.prefixes (bucket_id, name)
        SELECT c.bucket_id, c.name
        FROM candidates c
        ON CONFLICT DO NOTHING;
    END IF;

    -- 4) Prune source prefixes bottom-up for OLD−NEW
    IF array_length(v_src_bucket_ids, 1) IS NOT NULL THEN
        -- re-entrancy guard so DELETE on prefixes won't recurse
        IF current_setting('storage.gc.prefixes', true) <> '1' THEN
            PERFORM set_config('storage.gc.prefixes', '1', true);
        END IF;

        PERFORM storage.delete_leaf_prefixes(v_src_bucket_ids, v_src_names);
    END IF;

    RETURN NULL;
END;
$$;


--
-- Name: objects_update_level_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_update_level_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Ensure this is an update operation and the name has changed
    IF TG_OP = 'UPDATE' AND (NEW."name" <> OLD."name" OR NEW."bucket_id" <> OLD."bucket_id") THEN
        -- Set the new level
        NEW."level" := "storage"."get_level"(NEW."name");
    END IF;
    RETURN NEW;
END;
$$;


--
-- Name: objects_update_prefix_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.objects_update_prefix_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    old_prefixes TEXT[];
BEGIN
    -- Ensure this is an update operation and the name has changed
    IF TG_OP = 'UPDATE' AND (NEW."name" <> OLD."name" OR NEW."bucket_id" <> OLD."bucket_id") THEN
        -- Retrieve old prefixes
        old_prefixes := "storage"."get_prefixes"(OLD."name");

        -- Remove old prefixes that are only used by this object
        WITH all_prefixes as (
            SELECT unnest(old_prefixes) as prefix
        ),
        can_delete_prefixes as (
             SELECT prefix
             FROM all_prefixes
             WHERE NOT EXISTS (
                 SELECT 1 FROM "storage"."objects"
                 WHERE "bucket_id" = OLD."bucket_id"
                   AND "name" <> OLD."name"
                   AND "name" LIKE (prefix || '%')
             )
         )
        DELETE FROM "storage"."prefixes" WHERE name IN (SELECT prefix FROM can_delete_prefixes);

        -- Add new prefixes
        PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    END IF;
    -- Set the new level
    NEW."level" := "storage"."get_level"(NEW."name");

    RETURN NEW;
END;
$$;


--
-- Name: operation(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.operation() RETURNS text
    LANGUAGE plpgsql STABLE
    AS $$
BEGIN
    RETURN current_setting('storage.operation', true);
END;
$$;


--
-- Name: prefixes_delete_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.prefixes_delete_cleanup() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
DECLARE
    v_bucket_ids text[];
    v_names      text[];
BEGIN
    IF current_setting('storage.gc.prefixes', true) = '1' THEN
        RETURN NULL;
    END IF;

    PERFORM set_config('storage.gc.prefixes', '1', true);

    SELECT COALESCE(array_agg(d.bucket_id), '{}'),
           COALESCE(array_agg(d.name), '{}')
    INTO v_bucket_ids, v_names
    FROM deleted AS d
    WHERE d.name <> '';

    PERFORM storage.lock_top_prefixes(v_bucket_ids, v_names);
    PERFORM storage.delete_leaf_prefixes(v_bucket_ids, v_names);

    RETURN NULL;
END;
$$;


--
-- Name: prefixes_insert_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.prefixes_insert_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    RETURN NEW;
END;
$$;


--
-- Name: search(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql
    AS $$
declare
    can_bypass_rls BOOLEAN;
begin
    SELECT rolbypassrls
    INTO can_bypass_rls
    FROM pg_roles
    WHERE rolname = coalesce(nullif(current_setting('role', true), 'none'), current_user);

    IF can_bypass_rls THEN
        RETURN QUERY SELECT * FROM storage.search_v1_optimised(prefix, bucketname, limits, levels, offsets, search, sortcolumn, sortorder);
    ELSE
        RETURN QUERY SELECT * FROM storage.search_legacy_v1(prefix, bucketname, limits, levels, offsets, search, sortcolumn, sortorder);
    END IF;
end;
$$;


--
-- Name: search_legacy_v1(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search_legacy_v1(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
declare
    v_order_by text;
    v_sort_order text;
begin
    case
        when sortcolumn = 'name' then
            v_order_by = 'name';
        when sortcolumn = 'updated_at' then
            v_order_by = 'updated_at';
        when sortcolumn = 'created_at' then
            v_order_by = 'created_at';
        when sortcolumn = 'last_accessed_at' then
            v_order_by = 'last_accessed_at';
        else
            v_order_by = 'name';
        end case;

    case
        when sortorder = 'asc' then
            v_sort_order = 'asc';
        when sortorder = 'desc' then
            v_sort_order = 'desc';
        else
            v_sort_order = 'asc';
        end case;

    v_order_by = v_order_by || ' ' || v_sort_order;

    return query execute
        'with folders as (
           select path_tokens[$1] as folder
           from storage.objects
             where objects.name ilike $2 || $3 || ''%''
               and bucket_id = $4
               and array_length(objects.path_tokens, 1) <> $1
           group by folder
           order by folder ' || v_sort_order || '
     )
     (select folder as "name",
            null as id,
            null as updated_at,
            null as created_at,
            null as last_accessed_at,
            null as metadata from folders)
     union all
     (select path_tokens[$1] as "name",
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
     from storage.objects
     where objects.name ilike $2 || $3 || ''%''
       and bucket_id = $4
       and array_length(objects.path_tokens, 1) = $1
     order by ' || v_order_by || ')
     limit $5
     offset $6' using levels, prefix, search, bucketname, limits, offsets;
end;
$_$;


--
-- Name: search_v1_optimised(text, text, integer, integer, integer, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search_v1_optimised(prefix text, bucketname text, limits integer DEFAULT 100, levels integer DEFAULT 1, offsets integer DEFAULT 0, search text DEFAULT ''::text, sortcolumn text DEFAULT 'name'::text, sortorder text DEFAULT 'asc'::text) RETURNS TABLE(name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
declare
    v_order_by text;
    v_sort_order text;
begin
    case
        when sortcolumn = 'name' then
            v_order_by = 'name';
        when sortcolumn = 'updated_at' then
            v_order_by = 'updated_at';
        when sortcolumn = 'created_at' then
            v_order_by = 'created_at';
        when sortcolumn = 'last_accessed_at' then
            v_order_by = 'last_accessed_at';
        else
            v_order_by = 'name';
        end case;

    case
        when sortorder = 'asc' then
            v_sort_order = 'asc';
        when sortorder = 'desc' then
            v_sort_order = 'desc';
        else
            v_sort_order = 'asc';
        end case;

    v_order_by = v_order_by || ' ' || v_sort_order;

    return query execute
        'with folders as (
           select (string_to_array(name, ''/''))[level] as name
           from storage.prefixes
             where lower(prefixes.name) like lower($2 || $3) || ''%''
               and bucket_id = $4
               and level = $1
           order by name ' || v_sort_order || '
     )
     (select name,
            null as id,
            null as updated_at,
            null as created_at,
            null as last_accessed_at,
            null as metadata from folders)
     union all
     (select path_tokens[level] as "name",
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
     from storage.objects
     where lower(objects.name) like lower($2 || $3) || ''%''
       and bucket_id = $4
       and level = $1
     order by ' || v_order_by || ')
     limit $5
     offset $6' using levels, prefix, search, bucketname, limits, offsets;
end;
$_$;


--
-- Name: search_v2(text, text, integer, integer, text, text, text, text); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.search_v2(prefix text, bucket_name text, limits integer DEFAULT 100, levels integer DEFAULT 1, start_after text DEFAULT ''::text, sort_order text DEFAULT 'asc'::text, sort_column text DEFAULT 'name'::text, sort_column_after text DEFAULT ''::text) RETURNS TABLE(key text, name text, id uuid, updated_at timestamp with time zone, created_at timestamp with time zone, last_accessed_at timestamp with time zone, metadata jsonb)
    LANGUAGE plpgsql STABLE
    AS $_$
DECLARE
    sort_col text;
    sort_ord text;
    cursor_op text;
    cursor_expr text;
    sort_expr text;
BEGIN
    -- Validate sort_order
    sort_ord := lower(sort_order);
    IF sort_ord NOT IN ('asc', 'desc') THEN
        sort_ord := 'asc';
    END IF;

    -- Determine cursor comparison operator
    IF sort_ord = 'asc' THEN
        cursor_op := '>';
    ELSE
        cursor_op := '<';
    END IF;
    
    sort_col := lower(sort_column);
    -- Validate sort column  
    IF sort_col IN ('updated_at', 'created_at') THEN
        cursor_expr := format(
            '($5 = '''' OR ROW(date_trunc(''milliseconds'', %I), name COLLATE "C") %s ROW(COALESCE(NULLIF($6, '''')::timestamptz, ''epoch''::timestamptz), $5))',
            sort_col, cursor_op
        );
        sort_expr := format(
            'COALESCE(date_trunc(''milliseconds'', %I), ''epoch''::timestamptz) %s, name COLLATE "C" %s',
            sort_col, sort_ord, sort_ord
        );
    ELSE
        cursor_expr := format('($5 = '''' OR name COLLATE "C" %s $5)', cursor_op);
        sort_expr := format('name COLLATE "C" %s', sort_ord);
    END IF;

    RETURN QUERY EXECUTE format(
        $sql$
        SELECT * FROM (
            (
                SELECT
                    split_part(name, '/', $4) AS key,
                    name,
                    NULL::uuid AS id,
                    updated_at,
                    created_at,
                    NULL::timestamptz AS last_accessed_at,
                    NULL::jsonb AS metadata
                FROM storage.prefixes
                WHERE name COLLATE "C" LIKE $1 || '%%'
                    AND bucket_id = $2
                    AND level = $4
                    AND %s
                ORDER BY %s
                LIMIT $3
            )
            UNION ALL
            (
                SELECT
                    split_part(name, '/', $4) AS key,
                    name,
                    id,
                    updated_at,
                    created_at,
                    last_accessed_at,
                    metadata
                FROM storage.objects
                WHERE name COLLATE "C" LIKE $1 || '%%'
                    AND bucket_id = $2
                    AND level = $4
                    AND %s
                ORDER BY %s
                LIMIT $3
            )
        ) obj
        ORDER BY %s
        LIMIT $3
        $sql$,
        cursor_expr,    -- prefixes WHERE
        sort_expr,      -- prefixes ORDER BY
        cursor_expr,    -- objects WHERE
        sort_expr,      -- objects ORDER BY
        sort_expr       -- final ORDER BY
    )
    USING prefix, bucket_name, limits, levels, start_after, sort_column_after;
END;
$_$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION storage.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW; 
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_log_entries; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.audit_log_entries (
    instance_id uuid,
    id uuid NOT NULL,
    payload json,
    created_at timestamp with time zone,
    ip_address character varying(64) DEFAULT ''::character varying NOT NULL
);


--
-- Name: TABLE audit_log_entries; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.audit_log_entries IS 'Auth: Audit trail for user actions.';


--
-- Name: flow_state; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.flow_state (
    id uuid NOT NULL,
    user_id uuid,
    auth_code text NOT NULL,
    code_challenge_method auth.code_challenge_method NOT NULL,
    code_challenge text NOT NULL,
    provider_type text NOT NULL,
    provider_access_token text,
    provider_refresh_token text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    authentication_method text NOT NULL,
    auth_code_issued_at timestamp with time zone
);


--
-- Name: TABLE flow_state; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.flow_state IS 'stores metadata for pkce logins';


--
-- Name: identities; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.identities (
    provider_id text NOT NULL,
    user_id uuid NOT NULL,
    identity_data jsonb NOT NULL,
    provider text NOT NULL,
    last_sign_in_at timestamp with time zone,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    email text GENERATED ALWAYS AS (lower((identity_data ->> 'email'::text))) STORED,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


--
-- Name: TABLE identities; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.identities IS 'Auth: Stores identities associated to a user.';


--
-- Name: COLUMN identities.email; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.identities.email IS 'Auth: Email is a generated column that references the optional email property in the identity_data';


--
-- Name: instances; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.instances (
    id uuid NOT NULL,
    uuid uuid,
    raw_base_config text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: TABLE instances; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.instances IS 'Auth: Manages users across multiple sites.';


--
-- Name: mfa_amr_claims; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.mfa_amr_claims (
    session_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    authentication_method text NOT NULL,
    id uuid NOT NULL
);


--
-- Name: TABLE mfa_amr_claims; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.mfa_amr_claims IS 'auth: stores authenticator method reference claims for multi factor authentication';


--
-- Name: mfa_challenges; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.mfa_challenges (
    id uuid NOT NULL,
    factor_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    verified_at timestamp with time zone,
    ip_address inet NOT NULL,
    otp_code text,
    web_authn_session_data jsonb
);


--
-- Name: TABLE mfa_challenges; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.mfa_challenges IS 'auth: stores metadata about challenge requests made';


--
-- Name: mfa_factors; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.mfa_factors (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    friendly_name text,
    factor_type auth.factor_type NOT NULL,
    status auth.factor_status NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    secret text,
    phone text,
    last_challenged_at timestamp with time zone,
    web_authn_credential jsonb,
    web_authn_aaguid uuid,
    last_webauthn_challenge_data jsonb
);


--
-- Name: TABLE mfa_factors; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.mfa_factors IS 'auth: stores metadata about factors';


--
-- Name: COLUMN mfa_factors.last_webauthn_challenge_data; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.mfa_factors.last_webauthn_challenge_data IS 'Stores the latest WebAuthn challenge data including attestation/assertion for customer verification';


--
-- Name: oauth_authorizations; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.oauth_authorizations (
    id uuid NOT NULL,
    authorization_id text NOT NULL,
    client_id uuid NOT NULL,
    user_id uuid,
    redirect_uri text NOT NULL,
    scope text NOT NULL,
    state text,
    resource text,
    code_challenge text,
    code_challenge_method auth.code_challenge_method,
    response_type auth.oauth_response_type DEFAULT 'code'::auth.oauth_response_type NOT NULL,
    status auth.oauth_authorization_status DEFAULT 'pending'::auth.oauth_authorization_status NOT NULL,
    authorization_code text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '00:03:00'::interval) NOT NULL,
    approved_at timestamp with time zone,
    nonce text,
    CONSTRAINT oauth_authorizations_authorization_code_length CHECK ((char_length(authorization_code) <= 255)),
    CONSTRAINT oauth_authorizations_code_challenge_length CHECK ((char_length(code_challenge) <= 128)),
    CONSTRAINT oauth_authorizations_expires_at_future CHECK ((expires_at > created_at)),
    CONSTRAINT oauth_authorizations_nonce_length CHECK ((char_length(nonce) <= 255)),
    CONSTRAINT oauth_authorizations_redirect_uri_length CHECK ((char_length(redirect_uri) <= 2048)),
    CONSTRAINT oauth_authorizations_resource_length CHECK ((char_length(resource) <= 2048)),
    CONSTRAINT oauth_authorizations_scope_length CHECK ((char_length(scope) <= 4096)),
    CONSTRAINT oauth_authorizations_state_length CHECK ((char_length(state) <= 4096))
);


--
-- Name: oauth_clients; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.oauth_clients (
    id uuid NOT NULL,
    client_secret_hash text,
    registration_type auth.oauth_registration_type NOT NULL,
    redirect_uris text NOT NULL,
    grant_types text NOT NULL,
    client_name text,
    client_uri text,
    logo_uri text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone,
    client_type auth.oauth_client_type DEFAULT 'confidential'::auth.oauth_client_type NOT NULL,
    CONSTRAINT oauth_clients_client_name_length CHECK ((char_length(client_name) <= 1024)),
    CONSTRAINT oauth_clients_client_uri_length CHECK ((char_length(client_uri) <= 2048)),
    CONSTRAINT oauth_clients_logo_uri_length CHECK ((char_length(logo_uri) <= 2048))
);


--
-- Name: oauth_consents; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.oauth_consents (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    client_id uuid NOT NULL,
    scopes text NOT NULL,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    revoked_at timestamp with time zone,
    CONSTRAINT oauth_consents_revoked_after_granted CHECK (((revoked_at IS NULL) OR (revoked_at >= granted_at))),
    CONSTRAINT oauth_consents_scopes_length CHECK ((char_length(scopes) <= 2048)),
    CONSTRAINT oauth_consents_scopes_not_empty CHECK ((char_length(TRIM(BOTH FROM scopes)) > 0))
);


--
-- Name: one_time_tokens; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.one_time_tokens (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_type auth.one_time_token_type NOT NULL,
    token_hash text NOT NULL,
    relates_to text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT one_time_tokens_token_hash_check CHECK ((char_length(token_hash) > 0))
);


--
-- Name: refresh_tokens; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.refresh_tokens (
    instance_id uuid,
    id bigint NOT NULL,
    token character varying(255),
    user_id character varying(255),
    revoked boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    parent character varying(255),
    session_id uuid
);


--
-- Name: TABLE refresh_tokens; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.refresh_tokens IS 'Auth: Store of tokens used to refresh JWT tokens once they expire.';


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: auth; Owner: -
--

CREATE SEQUENCE auth.refresh_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: -
--

ALTER SEQUENCE auth.refresh_tokens_id_seq OWNED BY auth.refresh_tokens.id;


--
-- Name: saml_providers; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.saml_providers (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    entity_id text NOT NULL,
    metadata_xml text NOT NULL,
    metadata_url text,
    attribute_mapping jsonb,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    name_id_format text,
    CONSTRAINT "entity_id not empty" CHECK ((char_length(entity_id) > 0)),
    CONSTRAINT "metadata_url not empty" CHECK (((metadata_url = NULL::text) OR (char_length(metadata_url) > 0))),
    CONSTRAINT "metadata_xml not empty" CHECK ((char_length(metadata_xml) > 0))
);


--
-- Name: TABLE saml_providers; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.saml_providers IS 'Auth: Manages SAML Identity Provider connections.';


--
-- Name: saml_relay_states; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.saml_relay_states (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    request_id text NOT NULL,
    for_email text,
    redirect_to text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    flow_state_id uuid,
    CONSTRAINT "request_id not empty" CHECK ((char_length(request_id) > 0))
);


--
-- Name: TABLE saml_relay_states; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.saml_relay_states IS 'Auth: Contains SAML Relay State information for each Service Provider initiated login.';


--
-- Name: schema_migrations; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.schema_migrations (
    version character varying(255) NOT NULL
);


--
-- Name: TABLE schema_migrations; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.schema_migrations IS 'Auth: Manages updates to the auth system.';


--
-- Name: sessions; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.sessions (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    factor_id uuid,
    aal auth.aal_level,
    not_after timestamp with time zone,
    refreshed_at timestamp without time zone,
    user_agent text,
    ip inet,
    tag text,
    oauth_client_id uuid,
    refresh_token_hmac_key text,
    refresh_token_counter bigint,
    scopes text,
    CONSTRAINT sessions_scopes_length CHECK ((char_length(scopes) <= 4096))
);


--
-- Name: TABLE sessions; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.sessions IS 'Auth: Stores session data associated to a user.';


--
-- Name: COLUMN sessions.not_after; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sessions.not_after IS 'Auth: Not after is a nullable column that contains a timestamp after which the session should be regarded as expired.';


--
-- Name: COLUMN sessions.refresh_token_hmac_key; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sessions.refresh_token_hmac_key IS 'Holds a HMAC-SHA256 key used to sign refresh tokens for this session.';


--
-- Name: COLUMN sessions.refresh_token_counter; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sessions.refresh_token_counter IS 'Holds the ID (counter) of the last issued refresh token.';


--
-- Name: sso_domains; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.sso_domains (
    id uuid NOT NULL,
    sso_provider_id uuid NOT NULL,
    domain text NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    CONSTRAINT "domain not empty" CHECK ((char_length(domain) > 0))
);


--
-- Name: TABLE sso_domains; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.sso_domains IS 'Auth: Manages SSO email address domain mapping to an SSO Identity Provider.';


--
-- Name: sso_providers; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.sso_providers (
    id uuid NOT NULL,
    resource_id text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    disabled boolean,
    CONSTRAINT "resource_id not empty" CHECK (((resource_id = NULL::text) OR (char_length(resource_id) > 0)))
);


--
-- Name: TABLE sso_providers; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.sso_providers IS 'Auth: Manages SSO identity provider information; see saml_providers for SAML.';


--
-- Name: COLUMN sso_providers.resource_id; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.sso_providers.resource_id IS 'Auth: Uniquely identifies a SSO provider according to a user-chosen resource ID (case insensitive), useful in infrastructure as code.';


--
-- Name: users; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.users (
    instance_id uuid,
    id uuid NOT NULL,
    aud character varying(255),
    role character varying(255),
    email character varying(255),
    encrypted_password character varying(255),
    email_confirmed_at timestamp with time zone,
    invited_at timestamp with time zone,
    confirmation_token character varying(255),
    confirmation_sent_at timestamp with time zone,
    recovery_token character varying(255),
    recovery_sent_at timestamp with time zone,
    email_change_token_new character varying(255),
    email_change character varying(255),
    email_change_sent_at timestamp with time zone,
    last_sign_in_at timestamp with time zone,
    raw_app_meta_data jsonb,
    raw_user_meta_data jsonb,
    is_super_admin boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    phone text DEFAULT NULL::character varying,
    phone_confirmed_at timestamp with time zone,
    phone_change text DEFAULT ''::character varying,
    phone_change_token character varying(255) DEFAULT ''::character varying,
    phone_change_sent_at timestamp with time zone,
    confirmed_at timestamp with time zone GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED,
    email_change_token_current character varying(255) DEFAULT ''::character varying,
    email_change_confirm_status smallint DEFAULT 0,
    banned_until timestamp with time zone,
    reauthentication_token character varying(255) DEFAULT ''::character varying,
    reauthentication_sent_at timestamp with time zone,
    is_sso_user boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    is_anonymous boolean DEFAULT false NOT NULL,
    CONSTRAINT users_email_change_confirm_status_check CHECK (((email_change_confirm_status >= 0) AND (email_change_confirm_status <= 2)))
);


--
-- Name: TABLE users; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.users IS 'Auth: Stores user login data within a secure schema.';


--
-- Name: COLUMN users.is_sso_user; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.users.is_sso_user IS 'Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.';


--
-- Name: account_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.account_transactions (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    account_id integer,
    transaction_date date NOT NULL,
    transaction_type character varying(50) NOT NULL,
    debit_amount numeric(15,2),
    credit_amount numeric(15,2),
    balance_after numeric(15,2),
    reference_type character varying(50),
    reference_id integer,
    voucher_number character varying(50),
    narration text,
    created_at timestamp without time zone,
    created_by integer
);


--
-- Name: account_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.account_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: account_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.account_transactions_id_seq OWNED BY public.account_transactions.id;


--
-- Name: attendance; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    employee_id integer NOT NULL,
    site_id integer NOT NULL,
    employee_name character varying(100),
    type character varying(20) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    latitude double precision,
    longitude double precision,
    distance double precision,
    photo text,
    manual_entry boolean,
    comment character varying(500),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- Name: bank_accounts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bank_accounts (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    account_name character varying(100) NOT NULL,
    account_type character varying(20) NOT NULL,
    bank_name character varying(100),
    account_number character varying(50),
    ifsc_code character varying(20),
    branch character varying(100),
    opening_balance numeric(15,2),
    current_balance numeric(15,2),
    is_active boolean,
    is_default boolean,
    description text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bank_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bank_accounts_id_seq OWNED BY public.bank_accounts.id;


--
-- Name: commission_agents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.commission_agents (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(200) NOT NULL,
    code character varying(50),
    phone character varying(20),
    email character varying(120),
    default_commission_percentage double precision,
    employee_id integer,
    agent_type character varying(20),
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by integer
);


--
-- Name: commission_agents_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.commission_agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: commission_agents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.commission_agents_id_seq OWNED BY public.commission_agents.id;


--
-- Name: customer_loyalty_points; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customer_loyalty_points (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    customer_id integer NOT NULL,
    current_points integer,
    lifetime_earned_points integer,
    lifetime_redeemed_points integer,
    tier_level character varying(20),
    tier_updated_at timestamp without time zone,
    last_earned_at timestamp without time zone,
    last_redeemed_at timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: customer_loyalty_points_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customer_loyalty_points_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customer_loyalty_points_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customer_loyalty_points_id_seq OWNED BY public.customer_loyalty_points.id;


--
-- Name: customer_order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customer_order_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    item_id integer NOT NULL,
    quantity numeric(10,2) NOT NULL,
    rate numeric(10,2) NOT NULL,
    amount numeric(10,2) NOT NULL,
    tax_rate numeric(5,2),
    tax_amount numeric(10,2),
    created_at timestamp without time zone
);


--
-- Name: TABLE customer_order_items; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.customer_order_items IS 'Line items in customer orders';


--
-- Name: COLUMN customer_order_items.rate; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.customer_order_items.rate IS 'Price at time of order (snapshot)';


--
-- Name: customer_order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customer_order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customer_order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customer_order_items_id_seq OWNED BY public.customer_order_items.id;


--
-- Name: customer_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customer_orders (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    customer_id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    order_date timestamp without time zone NOT NULL,
    status character varying(20) NOT NULL,
    subtotal numeric(10,2) NOT NULL,
    tax_amount numeric(10,2) NOT NULL,
    total_amount numeric(10,2) NOT NULL,
    notes text,
    admin_notes text,
    fulfilled_date timestamp without time zone,
    fulfilled_by integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    invoice_id integer
);


--
-- Name: TABLE customer_orders; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.customer_orders IS 'Orders placed by customers through customer portal';


--
-- Name: COLUMN customer_orders.status; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.customer_orders.status IS 'Order status: pending, confirmed, fulfilled, cancelled';


--
-- Name: customer_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customer_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customer_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customer_orders_id_seq OWNED BY public.customer_orders.id;


--
-- Name: customer_subscriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customer_subscriptions (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    customer_id integer NOT NULL,
    plan_id integer NOT NULL,
    start_date date NOT NULL,
    current_period_start date NOT NULL,
    current_period_end date NOT NULL,
    status character varying(20),
    auto_renew boolean,
    cancelled_at timestamp without time zone,
    cancellation_reason text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    default_quantity numeric(10,2)
);


--
-- Name: customer_subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customer_subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customer_subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customer_subscriptions_id_seq OWNED BY public.customer_subscriptions.id;


--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    customer_code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    phone character varying(20),
    email character varying(120),
    address text,
    gstin character varying(15),
    state character varying(50),
    credit_limit double precision,
    payment_terms_days integer,
    opening_balance double precision,
    notes text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    pin character varying(10),
    bottles_in_possession integer DEFAULT 0,
    default_delivery_employee integer,
    delivery_special_instruction text,
    delivery_comment text,
    is_gst_customer boolean DEFAULT true,
    date_of_birth date,
    anniversary_date date
);


--
-- Name: COLUMN customers.default_delivery_employee; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.customers.default_delivery_employee IS 'Default employee for this customer deliveries';


--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.customers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.customers_id_seq OWNED BY public.customers.id;


--
-- Name: delivery_challan_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.delivery_challan_items (
    id integer NOT NULL,
    delivery_challan_id integer NOT NULL,
    tenant_id integer NOT NULL,
    item_id integer,
    item_name character varying(255) NOT NULL,
    description text,
    hsn_code character varying(20),
    quantity numeric(15,3) NOT NULL,
    unit character varying(50) DEFAULT 'pcs'::character varying,
    rate numeric(15,2),
    amount numeric(15,2),
    serial_numbers text,
    quantity_invoiced numeric(15,3) DEFAULT 0,
    quantity_returned numeric(15,3) DEFAULT 0,
    sales_order_item_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    sales_order_id integer,
    taxable_value numeric(15,2) DEFAULT 0,
    gst_rate numeric(5,2) DEFAULT 0,
    cgst_amount numeric(15,2) DEFAULT 0,
    sgst_amount numeric(15,2) DEFAULT 0,
    igst_amount numeric(15,2) DEFAULT 0,
    total_amount numeric(15,2) DEFAULT 0,
    batch_number character varying(50),
    serial_number character varying(100),
    notes text,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: delivery_challan_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.delivery_challan_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: delivery_challan_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.delivery_challan_items_id_seq OWNED BY public.delivery_challan_items.id;


--
-- Name: delivery_challans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.delivery_challans (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    challan_number character varying(50) NOT NULL,
    challan_date date NOT NULL,
    customer_id integer,
    customer_name character varying(255) NOT NULL,
    customer_phone character varying(20),
    customer_gstin character varying(15),
    customer_billing_address text,
    customer_shipping_address text,
    purpose character varying(100),
    transporter_name character varying(255),
    vehicle_number character varying(50),
    lr_number character varying(100),
    e_way_bill_number character varying(50),
    total_quantity numeric(15,3),
    total_amount numeric(15,2),
    status character varying(50) DEFAULT 'pending'::character varying,
    sales_order_id integer,
    expected_return_date date,
    actual_return_date date,
    notes text,
    terms text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    customer_email character varying(120),
    customer_state character varying(50) DEFAULT 'Maharashtra'::character varying,
    subtotal numeric(15,2) DEFAULT 0,
    cgst_amount numeric(15,2) DEFAULT 0,
    sgst_amount numeric(15,2) DEFAULT 0,
    igst_amount numeric(15,2) DEFAULT 0,
    delivery_note text,
    dispatched_at timestamp without time zone,
    delivered_at timestamp without time zone,
    invoiced_at timestamp without time zone
);


--
-- Name: delivery_challans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.delivery_challans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: delivery_challans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.delivery_challans_id_seq OWNED BY public.delivery_challans.id;


--
-- Name: delivery_day_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.delivery_day_notes (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    note_date date NOT NULL,
    note_text text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: delivery_day_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.delivery_day_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: delivery_day_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.delivery_day_notes_id_seq OWNED BY public.delivery_day_notes.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    pin character varying(10) NOT NULL,
    phone character varying(20),
    document_path text,
    site_id integer,
    active boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    email character varying(120),
    monthly_salary numeric(10,2) DEFAULT 0,
    date_of_joining date,
    designation character varying(100)
);


--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: expense_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expense_categories (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp without time zone
);


--
-- Name: expense_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expense_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: expense_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expense_categories_id_seq OWNED BY public.expense_categories.id;


--
-- Name: expenses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expenses (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    expense_date date NOT NULL,
    category_id integer NOT NULL,
    amount double precision NOT NULL,
    description text NOT NULL,
    payment_method character varying(50),
    reference_number character varying(100),
    vendor_name character varying(200),
    attachment_url character varying(500),
    created_by character varying(100),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.expenses_id_seq OWNED BY public.expenses.id;


--
-- Name: inventory_adjustment_lines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_adjustment_lines (
    id integer NOT NULL,
    adjustment_id integer NOT NULL,
    item_id integer NOT NULL,
    site_id integer NOT NULL,
    quantity_before double precision,
    value_before double precision,
    quantity_adjusted double precision,
    value_adjusted double precision,
    quantity_after double precision,
    value_after double precision
);


--
-- Name: inventory_adjustment_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inventory_adjustment_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inventory_adjustment_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inventory_adjustment_lines_id_seq OWNED BY public.inventory_adjustment_lines.id;


--
-- Name: inventory_adjustments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_adjustments (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    adjustment_number character varying(100) NOT NULL,
    adjustment_date date NOT NULL,
    mode character varying(20) NOT NULL,
    reason character varying(100),
    description text,
    account character varying(100),
    status character varying(20),
    created_by character varying(100),
    adjusted_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: inventory_adjustments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.inventory_adjustments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inventory_adjustments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.inventory_adjustments_id_seq OWNED BY public.inventory_adjustments.id;


--
-- Name: invoice_commissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invoice_commissions (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    invoice_id integer NOT NULL,
    agent_id integer NOT NULL,
    agent_name character varying(200) NOT NULL,
    agent_code character varying(50),
    commission_percentage double precision NOT NULL,
    invoice_amount double precision NOT NULL,
    commission_amount double precision NOT NULL,
    is_paid boolean,
    paid_date date,
    payment_notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: invoice_commissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.invoice_commissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: invoice_commissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.invoice_commissions_id_seq OWNED BY public.invoice_commissions.id;


--
-- Name: invoice_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invoice_items (
    id integer NOT NULL,
    invoice_id integer NOT NULL,
    item_id integer,
    item_name character varying(200) NOT NULL,
    description text,
    hsn_code character varying(20),
    quantity double precision NOT NULL,
    unit character varying(20),
    rate double precision NOT NULL,
    gst_rate double precision,
    taxable_value double precision NOT NULL,
    cgst_amount double precision,
    sgst_amount double precision,
    igst_amount double precision,
    total_amount double precision NOT NULL,
    sales_order_item_id integer,
    delivery_challan_item_id integer
);


--
-- Name: invoice_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.invoice_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: invoice_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.invoice_items_id_seq OWNED BY public.invoice_items.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invoices (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    invoice_date date NOT NULL,
    due_date date,
    customer_name character varying(200) NOT NULL,
    customer_phone character varying(20),
    customer_email character varying(120),
    customer_address text,
    customer_gstin character varying(15),
    customer_state character varying(50),
    subtotal double precision NOT NULL,
    cgst_amount double precision,
    sgst_amount double precision,
    igst_amount double precision,
    discount_amount double precision,
    round_off double precision,
    total_amount double precision NOT NULL,
    payment_status character varying(20),
    paid_amount double precision,
    payment_method character varying(50),
    notes text,
    internal_notes text,
    status character varying(20),
    cancelled_at timestamp without time zone,
    cancelled_reason text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    customer_id integer,
    sales_order_id integer,
    delivery_challan_id integer,
    discount_type character varying(20) DEFAULT 'flat'::character varying,
    discount_value numeric(10,2) DEFAULT 0,
    gst_enabled boolean DEFAULT true,
    loyalty_discount numeric(10,2) DEFAULT 0,
    loyalty_points_redeemed integer DEFAULT 0,
    loyalty_points_earned integer DEFAULT 0
);


--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.invoices_id_seq OWNED BY public.invoices.id;


--
-- Name: item_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.item_categories (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    parent_category_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    group_id integer
);


--
-- Name: item_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.item_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: item_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.item_categories_id_seq OWNED BY public.item_categories.id;


--
-- Name: item_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.item_groups (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: item_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.item_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: item_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.item_groups_id_seq OWNED BY public.item_groups.id;


--
-- Name: item_images; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.item_images (
    id integer NOT NULL,
    item_id integer NOT NULL,
    image_url text NOT NULL,
    is_primary boolean,
    display_order integer,
    uploaded_at timestamp without time zone
);


--
-- Name: item_images_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.item_images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: item_images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.item_images_id_seq OWNED BY public.item_images.id;


--
-- Name: item_stock_movements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.item_stock_movements (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    item_id integer NOT NULL,
    site_id integer NOT NULL,
    movement_type character varying(50) NOT NULL,
    quantity double precision NOT NULL,
    unit_cost double precision,
    total_value double precision,
    reference_number character varying(100),
    reference_type character varying(50),
    reference_id integer,
    from_site_id integer,
    to_site_id integer,
    reason text,
    notes text,
    created_by character varying(100),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: item_stock_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.item_stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: item_stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.item_stock_movements_id_seq OWNED BY public.item_stock_movements.id;


--
-- Name: item_stocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.item_stocks (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    item_id integer NOT NULL,
    site_id integer NOT NULL,
    quantity_available double precision,
    quantity_committed double precision,
    stock_value double precision,
    valuation_method character varying(20),
    last_stock_date timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: item_stocks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.item_stocks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: item_stocks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.item_stocks_id_seq OWNED BY public.item_stocks.id;


--
-- Name: items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.items (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(200) NOT NULL,
    sku character varying(100) NOT NULL,
    type character varying(20),
    category_id integer,
    item_group_id integer,
    unit character varying(50),
    dimensions_length double precision,
    dimensions_width double precision,
    dimensions_height double precision,
    dimensions_unit character varying(10),
    weight double precision,
    weight_unit character varying(10),
    manufacturer character varying(200),
    brand character varying(100),
    upc character varying(50),
    ean character varying(50),
    mpn character varying(50),
    isbn character varying(50),
    selling_price double precision,
    sales_description text,
    sales_account character varying(100),
    tax_preference character varying(50),
    cost_price double precision,
    purchase_description text,
    purchase_account character varying(100),
    preferred_vendor character varying(200),
    track_inventory boolean,
    opening_stock double precision,
    opening_stock_value double precision,
    reorder_point double precision,
    primary_image text,
    is_active boolean,
    is_returnable boolean,
    created_by character varying(100),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    hsn_code character varying(20),
    gst_rate double precision DEFAULT 18.0,
    mrp numeric(10,2) DEFAULT NULL::numeric,
    discount_percent numeric(5,2) DEFAULT 0,
    barcode character varying(50)
);


--
-- Name: items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.items_id_seq OWNED BY public.items.id;


--
-- Name: loyalty_programs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.loyalty_programs (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    program_name character varying(100),
    is_active boolean,
    points_per_100_rupees numeric(5,2),
    minimum_purchase_for_points numeric(10,2),
    maximum_points_per_invoice integer,
    enable_threshold_bonuses boolean,
    threshold_1_amount numeric(10,2),
    threshold_1_bonus_points integer,
    threshold_2_amount numeric(10,2),
    threshold_2_bonus_points integer,
    threshold_3_amount numeric(10,2),
    threshold_3_bonus_points integer,
    points_to_rupees_ratio numeric(5,2),
    minimum_points_to_redeem integer,
    maximum_discount_percent numeric(5,2),
    maximum_points_per_redemption integer,
    show_points_on_invoice boolean,
    invoice_footer_text character varying(255),
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    enable_birthday_bonus boolean DEFAULT false,
    birthday_bonus_points integer DEFAULT 0,
    enable_anniversary_bonus boolean DEFAULT false,
    anniversary_bonus_points integer DEFAULT 0,
    enable_membership_tiers boolean DEFAULT false,
    tier_bronze_name character varying(50) DEFAULT 'Bronze'::character varying,
    tier_bronze_min_points integer DEFAULT 0,
    tier_silver_name character varying(50) DEFAULT 'Silver'::character varying,
    tier_silver_min_points integer DEFAULT 1000,
    tier_gold_name character varying(50) DEFAULT 'Gold'::character varying,
    tier_gold_min_points integer DEFAULT 5000,
    tier_platinum_name character varying(50) DEFAULT 'Platinum'::character varying,
    tier_platinum_min_points integer DEFAULT 10000,
    tier_bronze_earning_multiplier numeric(5,2) DEFAULT 1.0,
    tier_bronze_redemption_multiplier numeric(5,2) DEFAULT 1.0,
    tier_bronze_max_discount_percent numeric(5,2),
    tier_silver_earning_multiplier numeric(5,2) DEFAULT 1.2,
    tier_silver_redemption_multiplier numeric(5,2) DEFAULT 1.1,
    tier_silver_max_discount_percent numeric(5,2),
    tier_gold_earning_multiplier numeric(5,2) DEFAULT 1.5,
    tier_gold_redemption_multiplier numeric(5,2) DEFAULT 1.25,
    tier_gold_max_discount_percent numeric(5,2),
    tier_platinum_earning_multiplier numeric(5,2) DEFAULT 2.0,
    tier_platinum_redemption_multiplier numeric(5,2) DEFAULT 1.5,
    tier_platinum_max_discount_percent numeric(5,2)
);


--
-- Name: loyalty_programs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.loyalty_programs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: loyalty_programs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.loyalty_programs_id_seq OWNED BY public.loyalty_programs.id;


--
-- Name: loyalty_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.loyalty_transactions (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    customer_id integer NOT NULL,
    transaction_type character varying(20) NOT NULL,
    points integer NOT NULL,
    points_before integer,
    points_after integer,
    invoice_id integer,
    invoice_number character varying(50),
    description text,
    base_points integer,
    bonus_points integer,
    invoice_amount numeric(10,2),
    created_at timestamp without time zone,
    created_by integer
);


--
-- Name: loyalty_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.loyalty_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: loyalty_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.loyalty_transactions_id_seq OWNED BY public.loyalty_transactions.id;


--
-- Name: materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.materials (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    category character varying(50),
    unit character varying(20),
    description text,
    image character varying(200),
    active boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: materials_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.materials_id_seq OWNED BY public.materials.id;


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.password_reset_tokens (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    token character varying(100) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone NOT NULL,
    used boolean DEFAULT false,
    used_at timestamp without time zone,
    ip_address character varying(50)
);


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.password_reset_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.password_reset_tokens_id_seq OWNED BY public.password_reset_tokens.id;


--
-- Name: payment_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payment_allocations (
    id integer NOT NULL,
    payment_id integer NOT NULL,
    purchase_bill_id integer NOT NULL,
    amount_allocated numeric(15,2) NOT NULL
);


--
-- Name: payment_allocations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payment_allocations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payment_allocations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payment_allocations_id_seq OWNED BY public.payment_allocations.id;


--
-- Name: payroll_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.payroll_payments (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    payment_month integer NOT NULL,
    payment_year integer NOT NULL,
    payment_date date NOT NULL,
    total_amount numeric(10,2) NOT NULL,
    paid_from_account_id integer,
    notes text,
    created_at timestamp without time zone NOT NULL,
    created_by integer
);


--
-- Name: payroll_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.payroll_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: payroll_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.payroll_payments_id_seq OWNED BY public.payroll_payments.id;


--
-- Name: purchase_bill_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.purchase_bill_items (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    purchase_bill_id integer NOT NULL,
    item_id integer,
    item_name character varying(255) NOT NULL,
    description text,
    hsn_code character varying(20),
    quantity numeric(15,3) NOT NULL,
    unit character varying(20),
    rate numeric(15,2) NOT NULL,
    discount_percentage numeric(5,2),
    discount_amount numeric(15,2),
    taxable_value numeric(15,2),
    gst_rate numeric(5,2),
    cgst_amount numeric(15,2),
    sgst_amount numeric(15,2),
    igst_amount numeric(15,2),
    total_amount numeric(15,2),
    site_id integer,
    received_quantity numeric(15,3),
    batch_number character varying(50),
    expiry_date date,
    notes text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: purchase_bill_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.purchase_bill_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: purchase_bill_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.purchase_bill_items_id_seq OWNED BY public.purchase_bill_items.id;


--
-- Name: purchase_bills; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.purchase_bills (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    bill_number character varying(50) NOT NULL,
    bill_date date NOT NULL,
    due_date date,
    vendor_id integer,
    vendor_name character varying(255) NOT NULL,
    vendor_phone character varying(20),
    vendor_email character varying(120),
    vendor_gstin character varying(15),
    vendor_address text,
    vendor_state character varying(50),
    purchase_request_id integer,
    subtotal numeric(15,2),
    discount_amount numeric(15,2),
    cgst_amount numeric(15,2),
    sgst_amount numeric(15,2),
    igst_amount numeric(15,2),
    other_charges numeric(15,2),
    round_off numeric(10,2),
    total_amount numeric(15,2) NOT NULL,
    payment_status character varying(20),
    paid_amount numeric(15,2),
    balance_due numeric(15,2),
    payment_terms character varying(100),
    reference_number character varying(100),
    notes text,
    terms_conditions text,
    document_url character varying(500),
    status character varying(20),
    approved_at timestamp without time zone,
    approved_by integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: purchase_bills_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.purchase_bills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: purchase_bills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.purchase_bills_id_seq OWNED BY public.purchase_bills.id;


--
-- Name: purchase_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.purchase_requests (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    employee_id integer NOT NULL,
    item_name character varying(200) NOT NULL,
    quantity double precision NOT NULL,
    estimated_price double precision NOT NULL,
    vendor_name character varying(200),
    request_type character varying(20) NOT NULL,
    category_id integer,
    reason text,
    document_url text,
    status character varying(20) NOT NULL,
    admin_notes text,
    rejection_reason text,
    processed_by character varying(100),
    processed_at timestamp without time zone,
    created_expense_id integer,
    created_item_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: purchase_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.purchase_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: purchase_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.purchase_requests_id_seq OWNED BY public.purchase_requests.id;


--
-- Name: salary_slips; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.salary_slips (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    payroll_payment_id integer,
    employee_id integer NOT NULL,
    payment_month integer NOT NULL,
    payment_year integer NOT NULL,
    salary_amount numeric(10,2) NOT NULL,
    payment_date date NOT NULL,
    payment_method character varying(50) DEFAULT 'Cash'::character varying,
    notes text,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: salary_slips_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.salary_slips_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: salary_slips_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.salary_slips_id_seq OWNED BY public.salary_slips.id;


--
-- Name: sales_order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales_order_items (
    id integer NOT NULL,
    sales_order_id integer NOT NULL,
    tenant_id integer NOT NULL,
    item_id integer,
    item_name character varying(255) NOT NULL,
    description text,
    hsn_code character varying(20),
    quantity numeric(15,3) NOT NULL,
    unit character varying(50),
    rate numeric(15,2) NOT NULL,
    gst_rate numeric(5,2),
    price_inclusive boolean,
    discount_type character varying(20),
    discount_value numeric(15,2),
    taxable_amount numeric(15,2),
    tax_amount numeric(15,2),
    total_amount numeric(15,2),
    quantity_delivered numeric(15,3),
    quantity_invoiced numeric(15,3),
    stock_reserved boolean,
    site_id integer,
    created_at timestamp without time zone
);


--
-- Name: sales_order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sales_order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_order_items_id_seq OWNED BY public.sales_order_items.id;


--
-- Name: sales_orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sales_orders (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    order_date date NOT NULL,
    expected_delivery_date date,
    customer_id integer,
    customer_name character varying(255) NOT NULL,
    customer_phone character varying(20),
    customer_email character varying(255),
    customer_gstin character varying(15),
    billing_address text,
    shipping_address text,
    subtotal numeric(15,2),
    discount_amount numeric(15,2),
    tax_amount numeric(15,2),
    total_amount numeric(15,2) NOT NULL,
    status character varying(50),
    quantity_ordered integer,
    quantity_delivered integer,
    quantity_invoiced integer,
    quotation_id integer,
    terms_and_conditions text,
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    created_by character varying(255)
);


--
-- Name: sales_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sales_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sales_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sales_orders_id_seq OWNED BY public.sales_orders.id;


--
-- Name: sites; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sites (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    address character varying(255),
    latitude double precision,
    longitude double precision,
    allowed_radius integer,
    active boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    is_default boolean DEFAULT false
);


--
-- Name: sites_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sites_id_seq OWNED BY public.sites.id;


--
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_movements (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    material_id integer NOT NULL,
    site_id integer NOT NULL,
    type character varying(20) NOT NULL,
    quantity double precision NOT NULL,
    reason character varying(255),
    reference character varying(100),
    "timestamp" timestamp without time zone NOT NULL,
    user_id integer,
    transfer_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stock_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stock_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stock_movements_id_seq OWNED BY public.stock_movements.id;


--
-- Name: stocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stocks (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    material_id integer NOT NULL,
    site_id integer NOT NULL,
    quantity double precision,
    min_stock_alert double precision,
    last_updated timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: stocks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stocks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stocks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stocks_id_seq OWNED BY public.stocks.id;


--
-- Name: subscription_deliveries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscription_deliveries (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    subscription_id integer NOT NULL,
    delivery_date date NOT NULL,
    quantity numeric(10,2) NOT NULL,
    rate numeric(10,2) NOT NULL,
    amount numeric(10,2) NOT NULL,
    status character varying(20) NOT NULL,
    is_modified boolean,
    modification_reason character varying(200),
    notes text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    delivered_by integer,
    delivered_at timestamp without time zone,
    bottles_delivered integer DEFAULT 0,
    bottles_collected integer DEFAULT 0,
    assigned_to integer
);


--
-- Name: COLUMN subscription_deliveries.assigned_to; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.subscription_deliveries.assigned_to IS 'Employee assigned to make this delivery';


--
-- Name: subscription_deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subscription_deliveries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subscription_deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subscription_deliveries_id_seq OWNED BY public.subscription_deliveries.id;


--
-- Name: subscription_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscription_payments (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    subscription_id integer NOT NULL,
    invoice_id integer,
    payment_date date NOT NULL,
    amount numeric(10,2) NOT NULL,
    payment_mode character varying(50),
    period_start date NOT NULL,
    period_end date NOT NULL,
    billing_period_label character varying(50),
    notes text,
    created_at timestamp without time zone
);


--
-- Name: subscription_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subscription_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subscription_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subscription_payments_id_seq OWNED BY public.subscription_payments.id;


--
-- Name: subscription_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subscription_plans (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    price numeric(10,2),
    duration_days integer,
    is_active boolean NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    plan_type character varying(20) DEFAULT 'fixed'::character varying NOT NULL,
    unit_rate numeric(10,2),
    unit_name character varying(20),
    delivery_pattern character varying(20) DEFAULT 'daily'::character varying,
    custom_days character varying(50)
);


--
-- Name: COLUMN subscription_plans.delivery_pattern; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.subscription_plans.delivery_pattern IS 'Delivery schedule: daily, alternate, weekdays, weekends, custom';


--
-- Name: COLUMN subscription_plans.custom_days; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.subscription_plans.custom_days IS 'Custom weekdays (0-6): e.g. 1,3,5 for Mon,Wed,Fri';


--
-- Name: subscription_plans_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.subscription_plans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: subscription_plans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.subscription_plans_id_seq OWNED BY public.subscription_plans.id;


--
-- Name: task_materials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_materials (
    id integer NOT NULL,
    task_id integer NOT NULL,
    material_name character varying(200) NOT NULL,
    quantity double precision NOT NULL,
    unit character varying(50),
    cost_per_unit double precision,
    total_cost double precision,
    added_by integer NOT NULL,
    created_at timestamp without time zone
);


--
-- Name: task_materials_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_materials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_materials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_materials_id_seq OWNED BY public.task_materials.id;


--
-- Name: task_media; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_media (
    id integer NOT NULL,
    task_id integer NOT NULL,
    media_type character varying(20) NOT NULL,
    file_path character varying(500) NOT NULL,
    caption text,
    uploaded_by integer NOT NULL,
    created_at timestamp without time zone
);


--
-- Name: task_media_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_media_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_media_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_media_id_seq OWNED BY public.task_media.id;


--
-- Name: task_updates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_updates (
    id integer NOT NULL,
    task_id integer NOT NULL,
    status character varying(20) NOT NULL,
    notes text,
    progress_percentage integer,
    worker_count integer,
    hours_worked double precision,
    updated_by integer NOT NULL,
    created_at timestamp without time zone
);


--
-- Name: task_updates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.task_updates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: task_updates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.task_updates_id_seq OWNED BY public.task_updates.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    task_number character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    priority character varying(20),
    status character varying(20),
    assigned_to integer NOT NULL,
    site_id integer,
    start_date date,
    deadline date,
    completed_at timestamp without time zone,
    created_by integer,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: tenants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenants (
    id integer NOT NULL,
    company_name character varying(100) NOT NULL,
    subdomain character varying(50) NOT NULL,
    admin_name character varying(100) NOT NULL,
    admin_email character varying(100) NOT NULL,
    admin_phone character varying(20),
    admin_password_hash character varying(256) NOT NULL,
    plan character varying(20),
    status character varying(20),
    trial_ends_at timestamp without time zone,
    subscription_ends_at timestamp without time zone,
    max_employees integer,
    max_sites integer,
    storage_limit_mb integer,
    features text,
    settings text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login_at timestamp without time zone,
    email_verified boolean DEFAULT true,
    verification_token character varying(100),
    token_expiry timestamp without time zone,
    total_bottles_inventory integer DEFAULT 0,
    damaged_bottles_count integer DEFAULT 0
);


--
-- Name: tenants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tenants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tenants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tenants_id_seq OWNED BY public.tenants.id;


--
-- Name: transfers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transfers (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    material_id integer NOT NULL,
    from_site_id integer NOT NULL,
    to_site_id integer NOT NULL,
    quantity double precision NOT NULL,
    reason character varying(255),
    status character varying(20),
    initiated_by integer,
    "timestamp" timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: transfers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.transfers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: transfers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.transfers_id_seq OWNED BY public.transfers.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password_hash character varying(255) NOT NULL,
    is_admin boolean,
    active boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vendor_payments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vendor_payments (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    payment_number character varying(50) NOT NULL,
    payment_date date NOT NULL,
    vendor_id integer NOT NULL,
    vendor_name character varying(255) NOT NULL,
    amount numeric(15,2) NOT NULL,
    payment_method character varying(50),
    reference_number character varying(100),
    bank_account character varying(100),
    notes text,
    created_by character varying(100),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


--
-- Name: vendor_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vendor_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vendor_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vendor_payments_id_seq OWNED BY public.vendor_payments.id;


--
-- Name: vendors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vendors (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    vendor_code character varying(50) NOT NULL,
    name character varying(200) NOT NULL,
    company_name character varying(200),
    phone character varying(20),
    email character varying(120),
    address text,
    gstin character varying(15),
    state character varying(50),
    credit_limit double precision,
    payment_terms_days integer,
    opening_balance double precision,
    notes text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


--
-- Name: vendors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vendors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vendors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vendors_id_seq OWNED BY public.vendors.id;


--
-- Name: messages; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE realtime.messages (
    topic text NOT NULL,
    extension text NOT NULL,
    payload jsonb,
    event text,
    private boolean DEFAULT false,
    updated_at timestamp without time zone DEFAULT now() NOT NULL,
    inserted_at timestamp without time zone DEFAULT now() NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL
)
PARTITION BY RANGE (inserted_at);


--
-- Name: schema_migrations; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE realtime.schema_migrations (
    version bigint NOT NULL,
    inserted_at timestamp(0) without time zone
);


--
-- Name: subscription; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE realtime.subscription (
    id bigint NOT NULL,
    subscription_id uuid NOT NULL,
    entity regclass NOT NULL,
    filters realtime.user_defined_filter[] DEFAULT '{}'::realtime.user_defined_filter[] NOT NULL,
    claims jsonb NOT NULL,
    claims_role regrole GENERATED ALWAYS AS (realtime.to_regrole((claims ->> 'role'::text))) STORED NOT NULL,
    created_at timestamp without time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);


--
-- Name: subscription_id_seq; Type: SEQUENCE; Schema: realtime; Owner: -
--

ALTER TABLE realtime.subscription ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME realtime.subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: buckets; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.buckets (
    id text NOT NULL,
    name text NOT NULL,
    owner uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    public boolean DEFAULT false,
    avif_autodetection boolean DEFAULT false,
    file_size_limit bigint,
    allowed_mime_types text[],
    owner_id text,
    type storage.buckettype DEFAULT 'STANDARD'::storage.buckettype NOT NULL
);


--
-- Name: COLUMN buckets.owner; Type: COMMENT; Schema: storage; Owner: -
--

COMMENT ON COLUMN storage.buckets.owner IS 'Field is deprecated, use owner_id instead';


--
-- Name: buckets_analytics; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.buckets_analytics (
    name text NOT NULL,
    type storage.buckettype DEFAULT 'ANALYTICS'::storage.buckettype NOT NULL,
    format text DEFAULT 'ICEBERG'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: buckets_vectors; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.buckets_vectors (
    id text NOT NULL,
    type storage.buckettype DEFAULT 'VECTOR'::storage.buckettype NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: migrations; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.migrations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    hash character varying(40) NOT NULL,
    executed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: objects; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.objects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    bucket_id text,
    name text,
    owner uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_accessed_at timestamp with time zone DEFAULT now(),
    metadata jsonb,
    path_tokens text[] GENERATED ALWAYS AS (string_to_array(name, '/'::text)) STORED,
    version text,
    owner_id text,
    user_metadata jsonb,
    level integer
);


--
-- Name: COLUMN objects.owner; Type: COMMENT; Schema: storage; Owner: -
--

COMMENT ON COLUMN storage.objects.owner IS 'Field is deprecated, use owner_id instead';


--
-- Name: prefixes; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.prefixes (
    bucket_id text NOT NULL,
    name text NOT NULL COLLATE pg_catalog."C",
    level integer GENERATED ALWAYS AS (storage.get_level(name)) STORED NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: s3_multipart_uploads; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.s3_multipart_uploads (
    id text NOT NULL,
    in_progress_size bigint DEFAULT 0 NOT NULL,
    upload_signature text NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL COLLATE pg_catalog."C",
    version text NOT NULL,
    owner_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_metadata jsonb
);


--
-- Name: s3_multipart_uploads_parts; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.s3_multipart_uploads_parts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    upload_id text NOT NULL,
    size bigint DEFAULT 0 NOT NULL,
    part_number integer NOT NULL,
    bucket_id text NOT NULL,
    key text NOT NULL COLLATE pg_catalog."C",
    etag text NOT NULL,
    owner_id text,
    version text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: vector_indexes; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE storage.vector_indexes (
    id text DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL COLLATE pg_catalog."C",
    bucket_id text NOT NULL,
    data_type text NOT NULL,
    dimension integer NOT NULL,
    distance_metric text NOT NULL,
    metadata_configuration jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('auth.refresh_tokens_id_seq'::regclass);


--
-- Name: account_transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_transactions ALTER COLUMN id SET DEFAULT nextval('public.account_transactions_id_seq'::regclass);


--
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- Name: bank_accounts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bank_accounts ALTER COLUMN id SET DEFAULT nextval('public.bank_accounts_id_seq'::regclass);


--
-- Name: commission_agents id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents ALTER COLUMN id SET DEFAULT nextval('public.commission_agents_id_seq'::regclass);


--
-- Name: customer_loyalty_points id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_loyalty_points ALTER COLUMN id SET DEFAULT nextval('public.customer_loyalty_points_id_seq'::regclass);


--
-- Name: customer_order_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_order_items ALTER COLUMN id SET DEFAULT nextval('public.customer_order_items_id_seq'::regclass);


--
-- Name: customer_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders ALTER COLUMN id SET DEFAULT nextval('public.customer_orders_id_seq'::regclass);


--
-- Name: customer_subscriptions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_subscriptions ALTER COLUMN id SET DEFAULT nextval('public.customer_subscriptions_id_seq'::regclass);


--
-- Name: customers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers ALTER COLUMN id SET DEFAULT nextval('public.customers_id_seq'::regclass);


--
-- Name: delivery_challan_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challan_items ALTER COLUMN id SET DEFAULT nextval('public.delivery_challan_items_id_seq'::regclass);


--
-- Name: delivery_challans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challans ALTER COLUMN id SET DEFAULT nextval('public.delivery_challans_id_seq'::regclass);


--
-- Name: delivery_day_notes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_day_notes ALTER COLUMN id SET DEFAULT nextval('public.delivery_day_notes_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: expense_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_categories ALTER COLUMN id SET DEFAULT nextval('public.expense_categories_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses ALTER COLUMN id SET DEFAULT nextval('public.expenses_id_seq'::regclass);


--
-- Name: inventory_adjustment_lines id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustment_lines ALTER COLUMN id SET DEFAULT nextval('public.inventory_adjustment_lines_id_seq'::regclass);


--
-- Name: inventory_adjustments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustments ALTER COLUMN id SET DEFAULT nextval('public.inventory_adjustments_id_seq'::regclass);


--
-- Name: invoice_commissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_commissions ALTER COLUMN id SET DEFAULT nextval('public.invoice_commissions_id_seq'::regclass);


--
-- Name: invoice_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_items ALTER COLUMN id SET DEFAULT nextval('public.invoice_items_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices ALTER COLUMN id SET DEFAULT nextval('public.invoices_id_seq'::regclass);


--
-- Name: item_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_categories ALTER COLUMN id SET DEFAULT nextval('public.item_categories_id_seq'::regclass);


--
-- Name: item_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_groups ALTER COLUMN id SET DEFAULT nextval('public.item_groups_id_seq'::regclass);


--
-- Name: item_images id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_images ALTER COLUMN id SET DEFAULT nextval('public.item_images_id_seq'::regclass);


--
-- Name: item_stock_movements id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements ALTER COLUMN id SET DEFAULT nextval('public.item_stock_movements_id_seq'::regclass);


--
-- Name: item_stocks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stocks ALTER COLUMN id SET DEFAULT nextval('public.item_stocks_id_seq'::regclass);


--
-- Name: items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items ALTER COLUMN id SET DEFAULT nextval('public.items_id_seq'::regclass);


--
-- Name: loyalty_programs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_programs ALTER COLUMN id SET DEFAULT nextval('public.loyalty_programs_id_seq'::regclass);


--
-- Name: loyalty_transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_transactions ALTER COLUMN id SET DEFAULT nextval('public.loyalty_transactions_id_seq'::regclass);


--
-- Name: materials id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials ALTER COLUMN id SET DEFAULT nextval('public.materials_id_seq'::regclass);


--
-- Name: password_reset_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens ALTER COLUMN id SET DEFAULT nextval('public.password_reset_tokens_id_seq'::regclass);


--
-- Name: payment_allocations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations ALTER COLUMN id SET DEFAULT nextval('public.payment_allocations_id_seq'::regclass);


--
-- Name: payroll_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_payments ALTER COLUMN id SET DEFAULT nextval('public.payroll_payments_id_seq'::regclass);


--
-- Name: purchase_bill_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bill_items ALTER COLUMN id SET DEFAULT nextval('public.purchase_bill_items_id_seq'::regclass);


--
-- Name: purchase_bills id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bills ALTER COLUMN id SET DEFAULT nextval('public.purchase_bills_id_seq'::regclass);


--
-- Name: purchase_requests id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_requests ALTER COLUMN id SET DEFAULT nextval('public.purchase_requests_id_seq'::regclass);


--
-- Name: salary_slips id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_slips ALTER COLUMN id SET DEFAULT nextval('public.salary_slips_id_seq'::regclass);


--
-- Name: sales_order_items id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_order_items ALTER COLUMN id SET DEFAULT nextval('public.sales_order_items_id_seq'::regclass);


--
-- Name: sales_orders id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders ALTER COLUMN id SET DEFAULT nextval('public.sales_orders_id_seq'::regclass);


--
-- Name: sites id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sites ALTER COLUMN id SET DEFAULT nextval('public.sites_id_seq'::regclass);


--
-- Name: stock_movements id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements ALTER COLUMN id SET DEFAULT nextval('public.stock_movements_id_seq'::regclass);


--
-- Name: stocks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stocks ALTER COLUMN id SET DEFAULT nextval('public.stocks_id_seq'::regclass);


--
-- Name: subscription_deliveries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries ALTER COLUMN id SET DEFAULT nextval('public.subscription_deliveries_id_seq'::regclass);


--
-- Name: subscription_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_payments ALTER COLUMN id SET DEFAULT nextval('public.subscription_payments_id_seq'::regclass);


--
-- Name: subscription_plans id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_plans ALTER COLUMN id SET DEFAULT nextval('public.subscription_plans_id_seq'::regclass);


--
-- Name: task_materials id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_materials ALTER COLUMN id SET DEFAULT nextval('public.task_materials_id_seq'::regclass);


--
-- Name: task_media id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_media ALTER COLUMN id SET DEFAULT nextval('public.task_media_id_seq'::regclass);


--
-- Name: task_updates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_updates ALTER COLUMN id SET DEFAULT nextval('public.task_updates_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: tenants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants ALTER COLUMN id SET DEFAULT nextval('public.tenants_id_seq'::regclass);


--
-- Name: transfers id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers ALTER COLUMN id SET DEFAULT nextval('public.transfers_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vendor_payments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendor_payments ALTER COLUMN id SET DEFAULT nextval('public.vendor_payments_id_seq'::regclass);


--
-- Name: vendors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors ALTER COLUMN id SET DEFAULT nextval('public.vendors_id_seq'::regclass);


--
-- Data for Name: audit_log_entries; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.audit_log_entries (instance_id, id, payload, created_at, ip_address) FROM stdin;
\.


--
-- Data for Name: flow_state; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.flow_state (id, user_id, auth_code, code_challenge_method, code_challenge, provider_type, provider_access_token, provider_refresh_token, created_at, updated_at, authentication_method, auth_code_issued_at) FROM stdin;
\.


--
-- Data for Name: identities; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.identities (provider_id, user_id, identity_data, provider, last_sign_in_at, created_at, updated_at, id) FROM stdin;
\.


--
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.instances (id, uuid, raw_base_config, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.mfa_amr_claims (session_id, created_at, updated_at, authentication_method, id) FROM stdin;
\.


--
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.mfa_challenges (id, factor_id, created_at, verified_at, ip_address, otp_code, web_authn_session_data) FROM stdin;
\.


--
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.mfa_factors (id, user_id, friendly_name, factor_type, status, created_at, updated_at, secret, phone, last_challenged_at, web_authn_credential, web_authn_aaguid, last_webauthn_challenge_data) FROM stdin;
\.


--
-- Data for Name: oauth_authorizations; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.oauth_authorizations (id, authorization_id, client_id, user_id, redirect_uri, scope, state, resource, code_challenge, code_challenge_method, response_type, status, authorization_code, created_at, expires_at, approved_at, nonce) FROM stdin;
\.


--
-- Data for Name: oauth_clients; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.oauth_clients (id, client_secret_hash, registration_type, redirect_uris, grant_types, client_name, client_uri, logo_uri, created_at, updated_at, deleted_at, client_type) FROM stdin;
\.


--
-- Data for Name: oauth_consents; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.oauth_consents (id, user_id, client_id, scopes, granted_at, revoked_at) FROM stdin;
\.


--
-- Data for Name: one_time_tokens; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.one_time_tokens (id, user_id, token_type, token_hash, relates_to, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.refresh_tokens (instance_id, id, token, user_id, revoked, created_at, updated_at, parent, session_id) FROM stdin;
\.


--
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.saml_providers (id, sso_provider_id, entity_id, metadata_xml, metadata_url, attribute_mapping, created_at, updated_at, name_id_format) FROM stdin;
\.


--
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.saml_relay_states (id, sso_provider_id, request_id, for_email, redirect_to, created_at, updated_at, flow_state_id) FROM stdin;
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.schema_migrations (version) FROM stdin;
20171026211738
20171026211808
20171026211834
20180103212743
20180108183307
20180119214651
20180125194653
00
20210710035447
20210722035447
20210730183235
20210909172000
20210927181326
20211122151130
20211124214934
20211202183645
20220114185221
20220114185340
20220224000811
20220323170000
20220429102000
20220531120530
20220614074223
20220811173540
20221003041349
20221003041400
20221011041400
20221020193600
20221021073300
20221021082433
20221027105023
20221114143122
20221114143410
20221125140132
20221208132122
20221215195500
20221215195800
20221215195900
20230116124310
20230116124412
20230131181311
20230322519590
20230402418590
20230411005111
20230508135423
20230523124323
20230818113222
20230914180801
20231027141322
20231114161723
20231117164230
20240115144230
20240214120130
20240306115329
20240314092811
20240427152123
20240612123726
20240729123726
20240802193726
20240806073726
20241009103726
20250717082212
20250731150234
20250804100000
20250901200500
20250903112500
20250904133000
20250925093508
20251007112900
20251104100000
20251111201300
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.sessions (id, user_id, created_at, updated_at, factor_id, aal, not_after, refreshed_at, user_agent, ip, tag, oauth_client_id, refresh_token_hmac_key, refresh_token_counter, scopes) FROM stdin;
\.


--
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.sso_domains (id, sso_provider_id, domain, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.sso_providers (id, resource_id, created_at, updated_at, disabled) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: -
--

COPY auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at, invited_at, confirmation_token, confirmation_sent_at, recovery_token, recovery_sent_at, email_change_token_new, email_change, email_change_sent_at, last_sign_in_at, raw_app_meta_data, raw_user_meta_data, is_super_admin, created_at, updated_at, phone, phone_confirmed_at, phone_change, phone_change_token, phone_change_sent_at, email_change_token_current, email_change_confirm_status, banned_until, reauthentication_token, reauthentication_sent_at, is_sso_user, deleted_at, is_anonymous) FROM stdin;
\.


--
-- Data for Name: account_transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.account_transactions (id, tenant_id, account_id, transaction_date, transaction_type, debit_amount, credit_amount, balance_after, reference_type, reference_id, voucher_number, narration, created_at, created_by) FROM stdin;
12	11	\N	2025-11-29	employee_expense	0.00	2000.00	8000.00	employee	13	Labour charge	Gave the payment to 5 workers	2025-11-29 11:18:50.532741	\N
14	11	\N	2025-11-29	employee_advance	10000.00	0.00	10000.00	employee	13	EMP-ADV-0001	for local expenses	2025-11-29 11:51:18.291755	\N
24	11	\N	2025-11-29	employee_return	0.00	1850.00	6150.00	employee	13	RET-13-1764445543	Cash returned by Rishi Jain to Cash in Hand	2025-11-29 19:45:43.897292	\N
26	11	4	2025-11-29	invoice_payment	2150.00	0.00	50950.00	invoice	53	INV-2025-0032	Payment received for INV-2025-0032 from Ayushi Samaiya	2025-11-29 20:52:00.804564	\N
21	11	4	2025-11-30	invoice_payment	1200.00	0.00	52150.00	invoice	58	INV-2025-0036	Payment received for INV-2025-0036 from Shubham Sethi	2025-11-29 19:18:52.297308	\N
5	11	9	2025-11-29	contra	10000.00	0.00	80000.00	contra	\N	CONTRA-0001	Transfer from Cash in Hand	2025-11-29 10:59:36.999422	\N
6	11	9	2025-11-29	contra	0.00	20000.00	60000.00	contra	\N	CONTRA-0002	Transfer to Cash in Hand	2025-11-29 11:00:44.681257	\N
18	11	9	2025-11-29	invoice_payment	650.00	0.00	60650.00	invoice	56	INV-2025-0034	Payment received for INV-2025-0034 from Ayushi Samaiya	2025-11-29 18:23:23.47843	\N
23	11	9	2025-11-30	expense	0.00	2000.00	58650.00	expense	12	EXP-12	expense on local fotkar - Business Expense	2025-11-29 19:31:12.367107	\N
30	11	10	2025-11-30	expense	0.00	1000.00	19000.00	expense	13	EXP-13	Santosh helper: weekly payment - Business Expense	2025-11-30 10:48:15.784582	\N
31	11	10	2025-11-30	expense	0.00	3000.00	16000.00	expense	14	EXP-14	Rent for JCB - JCB	2025-11-30 10:49:03.543884	\N
1	11	4	2025-11-29	balance_adjustment	50000.00	0.00	50000.00	\N	\N	\N	Balance adjustment: ₹50,000.00 added	2025-11-29 10:41:47.942031	\N
4	11	4	2025-11-29	contra	0.00	10000.00	40000.00	contra	\N	CONTRA-0001	Transfer to Bank HDFC	2025-11-29 10:59:36.999422	\N
7	11	4	2025-11-29	contra	20000.00	0.00	60000.00	contra	\N	CONTRA-0002	Transfer from Bank HDFC	2025-11-29 11:00:44.681257	\N
13	11	4	2025-11-29	employee_advance	0.00	10000.00	50000.00	employee_advance_given	13	EMP-ADV-0001	for local expenses	2025-11-29 11:51:18.291755	\N
17	11	4	2025-11-29	invoice_payment	950.00	0.00	50950.00	invoice	55	INV-2025-0033	Payment received for INV-2025-0033 from Rishi Samaiya	2025-11-29 16:50:08.950692	\N
22	11	4	2025-11-29	bill_payment	0.00	4000.00	46950.00	purchase_bill	28	PAY-0002	Payment to self for PB-202511-0009	2025-11-29 19:24:44.145053	\N
35	11	4	2025-11-30	opening_balance	52150.00	0.00	52150.00	\N	\N	\N	Opening balance - Cash in Hand (Auto-corrected)	2025-11-30 15:30:40.635973	\N
36	11	\N	2025-11-29	opening_balance_equity	0.00	142150.00	\N	\N	\N	OB-EQUITY-AUTO	Opening Balance - Owner Equity (Auto-balanced)	2025-11-30 15:30:40.635973	\N
37	11	4	2025-12-01	salary_payment	0.00	22000.00	30150.00	payroll	2	SAL-2025-12	Salary payment for 12/2025 - 2 employees	2025-11-30 19:54:13.285082	\N
38	11	9	2025-12-01	salary_payment	0.00	15000.00	43650.00	payroll	3	SAL-2025-11	Salary payment for 11/2025 - 1 employees	2025-11-30 20:08:56.708595	\N
39	11	9	2025-12-01	salary_payment	0.00	9000.00	34650.00	payroll	3	SAL-2025-11	Salary payment for 11/2025 - 1 employees	2025-11-30 20:13:00.349664	\N
40	11	4	2025-12-08	invoice_payment	1350.00	0.00	31500.00	invoice	61	INV-2025-0038	Payment received for INV-2025-0038 from Rishi Enterprises	2025-12-08 08:26:53.442147	\N
41	11	4	2025-12-10	invoice_payment	10800.00	0.00	42300.00	invoice	62	INV-2025-0039	Payment received for INV-2025-0039 from Rishi Samaiya	2025-12-10 05:47:13.83548	\N
42	11	4	2025-12-10	invoice_payment	1750.00	0.00	44050.00	invoice	63	INV-2025-0040	Payment received for INV-2025-0040 from Rishi Samaiya	2025-12-10 06:22:29.457844	\N
28	11	\N	2025-11-30	employee_expense	0.00	3500.00	2650.00	employee	13	Cemet 10 pkg	shortage	2025-11-30 10:17:52.489327	\N
29	11	\N	2025-11-30	employee_expense	0.00	1000.00	1650.00	employee	13	EMP-EXP-0001	Santosh helper: weekly payment	2025-11-30 10:29:41.272787	\N
3	11	9	2025-11-29	opening_balance	70000.00	0.00	140000.00	\N	\N	\N	Opening balance	2025-11-29 10:48:22.556829	\N
27	11	10	2025-11-30	opening_balance	20000.00	0.00	40000.00	\N	\N	\N	Opening balance	2025-11-30 10:15:36.05971	\N
25	11	4	2025-11-29	employee_return	1850.00	0.00	48800.00	employee	13	RET-13-1764445543	Cash returned by Rishi Jain	2025-11-29 19:45:43.897292	\N
43	21	11	2025-12-10	opening_balance	10000.00	0.00	10000.00	\N	\N	\N	Opening balance - Cash in locker	2025-12-10 12:21:02.508182	\N
44	21	\N	2025-12-10	opening_balance_equity	0.00	10000.00	10000.00	bank_account	11	OB-11	Opening balance equity - Cash in locker	2025-12-10 12:21:02.508182	\N
45	21	12	2025-12-10	opening_balance	10000.00	0.00	10000.00	\N	\N	\N	Opening balance - ICICI	2025-12-10 12:22:54.704409	\N
46	21	\N	2025-12-10	opening_balance_equity	0.00	10000.00	10000.00	bank_account	12	OB-12	Opening balance equity - ICICI	2025-12-10 12:22:54.704409	\N
47	16	\N	2025-12-02	opening_balance_inventory_equity	0.00	161680.00	161680.00	inventory_opening	\N	OB-INV-16	Opening Balance - Inventory Equity (₹161,680.00 worth of stock)	2025-12-11 04:21:58.123558	\N
48	11	\N	2025-11-02	opening_balance_inventory_equity	0.00	785437.50	785437.50	inventory_opening	\N	OB-INV-11	Opening Balance - Inventory Equity (₹785,437.50 worth of stock)	2025-12-11 04:21:58.123558	\N
49	21	\N	2025-12-10	opening_balance_inventory_equity	0.00	1989400.00	1989400.00	inventory_opening	\N	OB-INV-21	Opening Balance - Inventory Equity (₹1,989,400.00 worth of stock)	2025-12-11 04:21:58.123558	\N
\.


--
-- Data for Name: attendance; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.attendance (id, tenant_id, employee_id, site_id, employee_name, type, "timestamp", latitude, longitude, distance, photo, manual_entry, comment, created_at, updated_at) FROM stdin;
10	11	13	12	Rishi Jain	check_in	2025-12-06 10:57:51.181996	23.210312917854644	77.44201696937742	88.92936601230747	https://pyr7htm7ayy38zig.public.blob.vercel-storage.com/attendance/rishi_jain_20251206_105749-Py2DpWDGikLElaN12bFU3VAJ0yorbT.jpg	f	\N	2025-12-06 10:57:51.184493	2025-12-06 10:57:51.184499
\.


--
-- Data for Name: bank_accounts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bank_accounts (id, tenant_id, account_name, account_type, bank_name, account_number, ifsc_code, branch, opening_balance, current_balance, is_active, is_default, description, created_at, updated_at) FROM stdin;
1	17	Cash in Hand	cash	\N	\N	\N	\N	0.00	0.00	t	t	Default cash account for daily transactions	2025-11-29 10:12:49.076996	2025-11-29 10:12:49.076996
3	13	Cash in Hand	cash	\N	\N	\N	\N	0.00	0.00	t	t	Default cash account for daily transactions	2025-11-29 10:12:49.076996	2025-11-29 10:12:49.076996
6	16	Cash in Hand	cash	\N	\N	\N	\N	0.00	0.00	t	t	Default cash account for daily transactions	2025-11-29 10:12:49.076996	2025-11-29 10:12:49.076996
7	12	Cash in Hand	cash	\N	\N	\N	\N	0.00	0.00	t	t	Default cash account for daily transactions	2025-11-29 10:12:49.076996	2025-11-29 10:12:49.076996
10	11	Silak Nandu	cash					20000.00	16000.00	t	f		2025-11-30 10:15:36.05971	2025-11-30 13:04:17.835913
9	11	Bank HDFC	bank	HDFC Bank	07731530001380	HDFC0000773	Itarsi	70000.00	34650.00	t	f		2025-11-29 10:48:22.556829	2025-11-30 13:04:17.835913
4	11	Cash in Hand	cash					52150.00	44050.00	t	t	Default cash account for daily transactions	2025-11-29 10:12:49.076996	2025-12-10 06:22:29.457844
11	21	Cash in locker	cash					10000.00	10000.00	t	t		2025-12-10 12:21:02.508182	2025-12-10 12:21:02.508182
12	21	ICICI	bank	ICICI	042401543893	ICIC0000381	Itarsi	10000.00	10000.00	t	f		2025-12-10 12:22:54.704409	2025-12-10 12:22:54.704409
\.


--
-- Data for Name: commission_agents; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.commission_agents (id, tenant_id, name, code, phone, email, default_commission_percentage, employee_id, agent_type, is_active, created_at, updated_at, created_by) FROM stdin;
2	11	Ijaaz	\N	9766177231		1	\N	external	t	2025-11-10 04:03:12.396692	2025-11-10 04:03:12.396698	\N
1	11	Vaibhav jain	EMP-1212	83758 13228	coolvaibhav.jain88@gmail.com	1	18	employee	t	2025-11-09 20:17:41.445718	2025-11-25 04:30:12.146804	\N
3	11	Rishi Jain	EMP-1111	8983121201	rishi.samaiya@gmail.com	1	13	employee	t	2025-11-10 04:22:52.266581	2025-11-30 19:41:37.665811	\N
4	11	Ayushi Samaiya	EMP-2222	9617217821	ayushi.samaiya@gmail.com	1	14	employee	t	2025-11-30 19:49:24.774138	2025-11-30 19:49:24.774143	\N
5	11	Shubham sethi	EMP-4444	8099476801	sethishubham@gmail.com	1	16	employee	t	2025-11-30 20:08:30.19511	2025-11-30 20:08:30.195116	\N
6	11	Vikash Chauhan	EMP-5555	7276963330	vikashchauhan2310@gmail.com	1	17	employee	t	2025-11-30 20:12:37.113292	2025-11-30 20:12:37.113297	\N
\.


--
-- Data for Name: customer_loyalty_points; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customer_loyalty_points (id, tenant_id, customer_id, current_points, lifetime_earned_points, lifetime_redeemed_points, tier_level, tier_updated_at, last_earned_at, last_redeemed_at, created_at, updated_at) FROM stdin;
1	11	6	275	325	50	bronze	2025-12-10 06:22:34.710316	2025-12-10 06:22:33.590876	2025-12-10 06:22:32.091183	2025-12-10 05:45:48.975437	2025-12-10 06:22:34.711061
\.


--
-- Data for Name: customer_order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customer_order_items (id, order_id, item_id, quantity, rate, amount, tax_rate, tax_amount, created_at) FROM stdin;
1	1	58	0.50	400.00	200.00	0.00	0.00	2025-11-23 12:51:16.186361
2	2	59	1.00	1000.00	1000.00	0.00	0.00	2025-11-23 14:03:41.830533
3	3	58	0.50	400.00	200.00	0.00	0.00	2025-11-24 08:33:17.438838
4	4	59	1.00	1000.00	1000.00	0.00	0.00	2025-11-24 08:40:52.418387
5	5	58	0.50	400.00	200.00	0.00	0.00	2025-11-24 08:50:18.823241
6	6	59	1.00	1000.00	1000.00	0.00	0.00	2025-11-24 09:01:21.606302
7	7	58	0.50	400.00	200.00	0.00	0.00	2025-11-24 09:22:16.246522
8	8	59	1.00	1000.00	1000.00	0.00	0.00	2025-11-24 09:32:54.45221
9	9	59	0.50	1000.00	500.00	0.00	0.00	2025-11-24 09:46:05.793065
10	10	59	0.50	1000.00	500.00	0.00	0.00	2025-11-24 09:59:21.249029
11	11	58	0.20	400.00	80.00	0.00	0.00	2025-11-24 10:06:23.823298
12	12	59	0.50	1000.00	500.00	0.00	0.00	2025-11-24 10:28:13.263856
13	13	58	0.20	400.00	80.00	0.00	0.00	2025-11-24 10:41:38.361199
14	14	58	0.20	400.00	80.00	0.00	0.00	2025-11-24 10:50:32.44159
15	15	59	0.50	1000.00	500.00	0.00	0.00	2025-11-24 18:22:53.563498
16	16	58	0.20	400.00	80.00	0.00	0.00	2025-11-24 18:43:48.640811
17	17	20	1.00	150.00	150.00	18.00	27.00	2025-11-28 20:29:17.575809
\.


--
-- Data for Name: customer_orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customer_orders (id, tenant_id, customer_id, order_number, order_date, status, subtotal, tax_amount, total_amount, notes, admin_notes, fulfilled_date, fulfilled_by, created_at, updated_at, invoice_id) FROM stdin;
2	11	8	ORD-00002	2025-11-23 14:03:41.443783	fulfilled	1000.00	0.00	1000.00		your order is prepared ..will be delivered tomorrow	2025-11-24 08:01:38.272174	\N	2025-11-23 14:03:41.633168	2025-11-24 08:01:38.272182	38
1	11	8	ORD-00001	2025-11-23 12:51:15.79484	fulfilled	200.00	0.00	200.00		will be delivered tomorrow	2025-11-24 08:22:59.863457	\N	2025-11-23 12:51:15.984298	2025-11-24 08:22:59.863464	39
3	11	8	ORD-00003	2025-11-24 08:33:17.013599	fulfilled	200.00	0.00	200.00		\N	2025-11-24 08:35:10.063654	\N	2025-11-24 08:33:17.202937	2025-11-24 08:35:10.06366	40
4	11	8	ORD-00004	2025-11-24 08:40:52.037924	fulfilled	1000.00	0.00	1000.00		\N	2025-11-24 08:41:40.267062	\N	2025-11-24 08:40:52.22899	2025-11-24 08:41:40.267069	41
5	11	8	ORD-00005	2025-11-24 08:50:18.424704	fulfilled	200.00	0.00	200.00		\N	2025-11-24 08:53:42.642999	\N	2025-11-24 08:50:18.613097	2025-11-24 08:53:42.643006	42
6	11	8	ORD-00006	2025-11-24 09:01:21.227857	fulfilled	1000.00	0.00	1000.00		\N	2025-11-24 09:10:33.950794	\N	2025-11-24 09:01:21.417549	2025-11-24 09:10:33.950802	43
7	11	8	ORD-00007	2025-11-24 09:22:15.866594	fulfilled	200.00	0.00	200.00		\N	2025-11-24 09:23:22.015718	\N	2025-11-24 09:22:16.056779	2025-11-24 09:23:22.015724	44
8	11	8	ORD-00008	2025-11-24 09:32:54.028593	fulfilled	1000.00	0.00	1000.00		\N	2025-11-24 09:40:55.186971	\N	2025-11-24 09:32:54.231203	2025-11-24 09:40:55.186978	45
9	11	8	ORD-00009	2025-11-24 09:46:05.410869	fulfilled	500.00	0.00	500.00		\N	2025-11-24 09:47:10.356296	\N	2025-11-24 09:46:05.601364	2025-11-24 09:47:10.356303	46
10	11	8	ORD-00010	2025-11-24 09:59:20.842629	fulfilled	500.00	0.00	500.00		\N	2025-11-24 10:00:40.789467	\N	2025-11-24 09:59:21.045867	2025-11-24 10:00:40.789476	47
11	11	8	ORD-00011	2025-11-24 10:06:23.442408	fulfilled	80.00	0.00	80.00		\N	2025-11-24 10:07:17.386187	\N	2025-11-24 10:06:23.633349	2025-11-24 10:07:17.386193	48
12	11	8	ORD-00012	2025-11-24 10:28:12.850504	fulfilled	500.00	0.00	500.00		\N	2025-11-24 10:28:57.660337	\N	2025-11-24 10:28:13.053582	2025-11-24 10:28:57.660344	49
13	11	8	ORD-00013	2025-11-24 10:41:37.982266	fulfilled	80.00	0.00	80.00		\N	2025-11-24 10:42:18.105295	\N	2025-11-24 10:41:38.171336	2025-11-24 10:42:18.105302	50
14	11	8	ORD-00014	2025-11-24 10:50:32.061614	fulfilled	80.00	0.00	80.00		\N	2025-11-24 10:51:07.706599	\N	2025-11-24 10:50:32.250787	2025-11-24 10:51:07.706606	51
15	11	5	ORD-00015	2025-11-24 18:22:53.164339	fulfilled	500.00	0.00	500.00		will be delivered tomorrow	2025-11-24 18:26:10.231264	\N	2025-11-24 18:22:53.354332	2025-11-24 18:26:10.231271	52
16	11	5	ORD-00016	2025-11-24 18:43:48.179734	pending	80.00	0.00	80.00		\N	\N	\N	2025-11-24 18:43:48.411905	2025-11-24 18:43:48.411911	\N
17	11	8	ORD-00017	2025-11-28 20:29:17.1723	pending	150.00	27.00	177.00		\N	\N	\N	2025-11-28 20:29:17.362974	2025-11-28 20:29:17.36298	\N
\.


--
-- Data for Name: customer_subscriptions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customer_subscriptions (id, tenant_id, customer_id, plan_id, start_date, current_period_start, current_period_end, status, auto_renew, cancelled_at, cancellation_reason, created_at, updated_at, default_quantity) FROM stdin;
3	11	3	1	2025-11-12	2025-12-13	2026-01-12	active	t	\N	\N	2025-11-12 18:39:04.618892	2025-11-12 18:46:14.133222	\N
4	11	2	1	2025-11-13	2025-11-13	2025-12-13	active	t	\N	\N	2025-11-13 06:36:51.948063	2025-11-13 06:36:51.94807	\N
5	11	4	1	2025-11-13	2025-11-13	2025-12-13	active	t	\N	\N	2025-11-13 06:40:34.186682	2025-11-13 06:40:34.186689	\N
6	11	5	1	2025-11-13	2025-11-13	2025-12-13	active	t	\N	\N	2025-11-13 08:12:13.978721	2025-11-13 10:12:48.034164	\N
7	11	3	5	2025-11-22	2025-11-22	2025-12-22	active	t	\N	\N	2025-11-22 19:50:04.515501	2025-11-22 19:50:04.515506	1.00
9	11	6	5	2025-11-22	2025-11-22	2025-11-30	pending_payment	t	\N	\N	2025-11-22 20:34:02.30934	2025-11-23 03:59:27.493064	2.00
10	11	7	5	2025-11-23	2025-11-23	2025-11-30	pending_payment	t	\N	\N	2025-11-23 04:17:30.173784	2025-11-23 04:19:25.013659	1.50
12	11	5	5	2025-11-24	2025-11-24	2025-11-30	active	t	\N	\N	2025-11-24 18:13:35.105602	2025-11-24 18:13:35.105608	3.00
13	16	12	7	2025-12-02	2025-12-02	2025-12-31	active	t	\N	\N	2025-12-02 15:49:51.260374	2025-12-02 15:49:51.26038	1.50
14	16	58	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 15:55:35.919671	2025-12-02 15:55:35.919678	0.50
15	16	40	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 15:57:16.676703	2025-12-02 15:57:16.676709	1.00
16	16	34	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 15:58:29.863707	2025-12-02 15:58:29.863712	1.00
17	16	35	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 17:45:35.958657	2025-12-02 17:45:35.958665	0.50
19	16	37	9	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 18:55:02.979658	2025-12-02 18:55:02.979665	0.50
20	16	37	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:10:08.598928	2025-12-02 19:10:08.598935	1.00
21	16	38	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:26:34.891073	2025-12-02 19:26:34.891079	0.50
22	16	39	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:33:58.957148	2025-12-02 19:33:58.957154	1.00
23	16	32	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:35:09.117978	2025-12-02 19:35:09.117985	0.50
24	16	33	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:35:45.784439	2025-12-02 19:35:45.784445	0.50
25	16	41	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:37:40.191218	2025-12-02 19:37:40.191225	1.00
26	16	42	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:38:13.324798	2025-12-02 19:38:13.324805	1.00
11	11	8	5	2025-11-23	2025-11-23	2025-11-30	pending_payment	t	\N	\N	2025-11-23 10:53:46.251181	2025-12-02 20:20:54.914782	2.00
32	16	43	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:25.420774	2025-12-03 18:57:25.420781	1.00
35	16	46	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:28.908419	2025-12-03 18:57:28.908425	1.00
38	16	48	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:32.323823	2025-12-03 18:57:32.323829	1.00
39	16	49	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:33.273092	2025-12-03 18:57:33.273115	1.00
40	16	50	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:34.412421	2025-12-03 18:57:34.412428	1.00
42	16	53	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:36.692311	2025-12-03 18:57:36.692317	1.00
43	16	52	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:37.83367	2025-12-03 18:57:37.833676	1.00
44	16	54	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:38.970817	2025-12-03 18:57:38.970823	1.00
45	16	59	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:40.106927	2025-12-03 18:57:40.106932	1.00
46	16	76	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:41.243916	2025-12-03 18:57:41.243921	1.50
47	16	77	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:42.379397	2025-12-03 18:57:42.379402	1.00
48	16	75	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:43.516874	2025-12-03 18:57:43.51688	1.00
49	16	72	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:44.662588	2025-12-03 18:57:44.662594	1.00
51	16	73	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:46.952542	2025-12-03 18:57:46.952562	1.00
52	16	63	9	2025-12-02	2025-12-02	2025-12-31	active	t	\N	\N	2025-12-03 18:57:48.090428	2025-12-03 18:57:48.090433	1.00
53	16	63	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:49.225293	2025-12-03 18:57:49.225299	1.00
54	16	62	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:50.176715	2025-12-03 18:57:50.176722	1.00
55	16	64	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:51.31757	2025-12-03 18:57:51.317575	1.00
56	16	60	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:52.458466	2025-12-03 18:57:52.458471	1.00
57	16	61	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:53.595968	2025-12-03 18:57:53.595974	2.00
58	16	18	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:54.736626	2025-12-03 18:57:54.736631	1.00
59	16	13	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:55.875426	2025-12-03 18:57:55.875432	1.00
60	16	14	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:57.014786	2025-12-03 18:57:57.014792	0.50
61	16	15	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:58.157819	2025-12-03 18:57:58.157825	1.00
62	16	16	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:59.29548	2025-12-03 18:57:59.295486	1.00
63	16	16	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:00.435782	2025-12-03 18:58:00.435787	0.50
64	16	17	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:01.384863	2025-12-03 18:58:01.384869	1.50
65	16	20	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:02.523791	2025-12-03 18:58:02.523797	1.50
66	16	21	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:03.662722	2025-12-03 18:58:03.662728	1.00
67	16	22	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:04.799969	2025-12-03 18:58:04.799974	1.50
68	16	23	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:05.93677	2025-12-03 18:58:05.936777	1.00
69	16	19	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:07.074359	2025-12-03 18:58:07.074365	1.50
70	16	25	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:08.212954	2025-12-03 18:58:08.21296	0.50
71	16	24	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:09.348514	2025-12-03 18:58:09.34852	2.00
72	16	26	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:10.484926	2025-12-03 18:58:10.484932	0.50
73	16	27	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:11.625154	2025-12-03 18:58:11.625173	0.50
74	16	28	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:12.762993	2025-12-03 18:58:12.762999	0.50
75	16	29	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:13.900655	2025-12-03 18:58:13.900662	0.50
76	16	31	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:15.038077	2025-12-03 18:58:15.038084	1.00
77	16	55	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:16.176085	2025-12-03 18:58:16.17609	2.50
78	16	65	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:17.316361	2025-12-03 18:58:17.316367	1.00
79	16	66	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:18.45803	2025-12-03 18:58:18.458036	1.00
80	16	67	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:19.598418	2025-12-03 18:58:19.598425	1.00
81	16	68	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:20.737897	2025-12-03 18:58:20.737904	1.00
82	16	69	8	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:21.87514	2025-12-03 18:58:21.875146	0.50
83	16	70	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:23.008786	2025-12-03 18:58:23.008792	1.00
84	16	70	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:24.146916	2025-12-03 18:58:24.146922	0.50
85	16	71	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:25.100621	2025-12-03 18:58:25.100627	1.00
86	16	56	9	2025-12-02	2025-12-02	2025-12-31	active	t	\N	\N	2025-12-03 18:58:26.238011	2025-12-03 18:58:26.238017	1.00
87	16	57	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:27.37072	2025-12-03 18:58:27.370726	2.00
88	16	78	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:58:28.50892	2025-12-03 18:58:28.508926	1.00
34	16	45	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:27.770093	2025-12-03 19:14:15.145797	0.50
36	16	47	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:30.045965	2025-12-03 19:15:17.031377	0.50
37	16	48	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:31.184861	2025-12-03 19:15:48.125346	0.50
41	16	51	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:35.554042	2025-12-03 19:16:17.948384	0.50
89	16	79	7	2025-12-02	2025-12-02	2025-12-31	active	t	\N	\N	2025-12-03 18:58:29.648054	2025-12-03 18:58:29.64806	1.00
28	16	42	8	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-02 19:39:05.233764	2025-12-03 19:12:21.357663	0.50
33	16	44	7	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 18:57:26.62778	2025-12-03 19:13:11.047821	0.50
91	16	74	10	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 19:28:51.363049	2025-12-03 19:28:51.363055	1.00
92	16	36	12	2025-12-01	2025-12-01	2025-12-31	active	t	\N	\N	2025-12-03 19:32:02.525421	2025-12-03 19:32:02.525428	1.50
93	16	80	10	2025-12-03	2025-12-03	2025-12-31	active	t	\N	\N	2025-12-03 19:42:22.992122	2025-12-03 19:42:22.992128	1.00
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customers (id, tenant_id, customer_code, name, phone, email, address, gstin, state, credit_limit, payment_terms_days, opening_balance, notes, is_active, created_at, updated_at, pin, bottles_in_possession, default_delivery_employee, delivery_special_instruction, delivery_comment, is_gst_customer, date_of_birth, anniversary_date) FROM stdin;
7	11	CUST-0006	Khush Jain	8983121201	11rohit84@gmail.com	1/2 shalimar enclave E-3 arera colony		Maharashtra	0	30	0		t	2025-11-23 04:17:04.813169	2025-11-23 10:35:19.498753	6684	0	\N	\N	\N	t	\N	\N
15	16	CUST-0004	Riverdale Society E1-704 Neeru	9876543212		Riverdale Society E1-704 Neeru		Maharashtra	0	30	0		t	2025-12-02 10:08:32.288591	2025-12-02 10:08:32.288596	\N	0	\N	\N	\N	t	\N	\N
16	16	CUST-0005	Riverdale Society E1-802 Kiran	9876543213		Riverdale Society E1-802 Kiran		Maharashtra	0	30	0		t	2025-12-02 10:08:32.849632	2025-12-02 10:08:32.849661	\N	0	\N	\N	\N	t	\N	\N
9	11	CUST-0008	Sarita Jain	9425029537	saritajain18@gmail.com	1/2 shalimar enclave		Maharashtra	0	30	0	\N	t	2025-11-25 06:37:40.998073	2025-11-25 06:37:40.99808	9537	0	\N	\N	\N	t	\N	\N
10	11	CUST-0009	Rohan Nikhal	9637273732	email_rohan@gmail.com	tower 6, pune		Maharashtra	50000	30	0	KPIT	t	2025-11-26 04:42:39.827017	2025-11-26 04:42:39.827023	\N	0	\N	\N	\N	t	\N	\N
17	16	CUST-0006	Riverdale Society E1-804 Deepak	9876543214		Riverdale Society E1-804 Deepak		Maharashtra	0	30	0		t	2025-12-02 10:08:33.410719	2025-12-02 10:08:33.410723	\N	0	\N	\N	\N	t	\N	\N
18	16	CUST-0007	Riverdale Society E1-2303 Pragya	9876543215		Riverdale Society E1-2303 Pragya		Maharashtra	0	30	0		t	2025-12-02 10:08:33.971458	2025-12-02 10:08:33.971463	\N	0	\N	\N	\N	t	\N	\N
19	16	CUST-0008	Riverdale Society E2-801 Abha	9876543216		Riverdale Society E2-801 Abha		Maharashtra	0	30	0		t	2025-12-02 10:08:34.53266	2025-12-02 10:08:34.532666	\N	0	\N	\N	\N	t	\N	\N
20	16	CUST-0009	Riverdale Society E2-1003 Garima	9876543217		Riverdale Society E2-1003 Garima		Maharashtra	0	30	0		t	2025-12-02 10:08:35.093501	2025-12-02 10:08:35.093506	\N	0	\N	\N	\N	t	\N	\N
21	16	CUST-0010	Riverdale Society E2-1004 Rupal	9876543218		Riverdale Society E2-1004 Rupal		Maharashtra	0	30	0		t	2025-12-02 10:08:35.655944	2025-12-02 10:08:35.655949	\N	0	\N	\N	\N	t	\N	\N
2	11	CUST-0001	ABC Corporation	9876543210	contact@abc.com	123 Business Park, Mumbai, 400001	27AABCU9603R1ZM	Maharashtra	50000	30	0	VIP Customer	t	2025-11-02 18:20:16.52992	2025-11-26 06:57:24.020934	\N	1	16	\N	\N	t	\N	\N
22	16	CUST-0011	Riverdale Society E2-1201 Satish	9876543219		Riverdale Society E2-1201 Satish		Maharashtra	0	30	0		t	2025-12-02 10:08:36.216776	2025-12-02 10:08:36.216781	\N	0	\N	\N	\N	t	\N	\N
4	11	CUST-0003	Sharma Traders	9988776655	sharma@gmail.com	Main Market, Indore		Madhya Pradesh	50000	15	2500	Regular	t	2025-11-02 18:20:17.717481	2025-11-26 06:59:17.476584	\N	3	16	\N	\N	t	\N	\N
23	16	CUST-0012	Riverdale Society E2-2403 Shweta	9876543220		Riverdale Society E2-2403 Shweta		Maharashtra	0	30	0		t	2025-12-02 10:08:36.777808	2025-12-02 10:08:36.777813	\N	0	\N	\N	\N	t	\N	\N
24	16	CUST-0013	Riverdale Society E3-1201 Mayuri	9876543221		Riverdale Society E3-1201 Mayuri		Maharashtra	0	30	0		t	2025-12-02 10:08:37.338342	2025-12-02 10:08:37.338347	\N	0	\N	\N	\N	t	\N	\N
25	16	CUST-0014	Riverdale Society E3-101 Ruchita	9876543222		Riverdale Society E3-101 Ruchita		Maharashtra	0	30	0		t	2025-12-02 10:08:37.899049	2025-12-02 10:08:37.899054	\N	0	\N	\N	\N	t	\N	\N
26	16	CUST-0015	Riverdale Society E3-1303 Naseem	9876543223		Riverdale Society E3-1303 Naseem		Maharashtra	0	30	0		t	2025-12-02 10:08:38.459983	2025-12-02 10:08:38.459988	\N	0	\N	\N	\N	t	\N	\N
27	16	CUST-0016	Riverdale Society E3-1401 R.ubi	9876543224		Riverdale Society E3-1401 R.ubi		Maharashtra	0	30	0		t	2025-12-02 10:08:39.020271	2025-12-02 10:08:39.020276	\N	0	\N	\N	\N	t	\N	\N
28	16	CUST-0017	Riverdale Society E3-1602 Aastha	9876543225		Riverdale Society E3-1602 Aastha		Maharashtra	0	30	0		t	2025-12-02 10:08:39.581248	2025-12-02 10:08:39.581254	\N	0	\N	\N	\N	t	\N	\N
8	11	CUST-0007	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	0	30	0	\N	t	2025-11-23 10:52:00.518095	2025-11-26 19:46:25.830182	1234	3	21	\N	\N	t	\N	\N
3	11	CUST-0002	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Madhya Pradesh	100000	30	0	VIP	t	2025-11-02 18:20:17.103613	2025-11-26 19:46:38.470078	\N	1	21	\N	\N	t	\N	\N
5	11	CUST-0004	Shubham Sethi	7032018290	sethishubham@gmail.com	1/2 shalimar enclave		Madhya Pradesh	0	30	0		t	2025-11-08 10:12:57.47572	2025-11-26 19:46:50.372021	8290	4	21	\N	\N	t	\N	\N
13	16	CUST-0002	Riverdale Society E1-303 Tina	9876543210		Riverdale Society E1-303 Tina		Maharashtra	0	30	0		t	2025-12-02 10:08:31.154751	2025-12-02 10:08:31.154757	\N	0	\N	\N	\N	t	\N	\N
14	16	CUST-0003	Riverdale Society E1-403 Lovina	9876543211		Riverdale Society E1-403 Lovina		Maharashtra	0	30	0		t	2025-12-02 10:08:31.726812	2025-12-02 10:08:31.726817	\N	0	\N	\N	\N	t	\N	\N
29	16	CUST-0018	Riverdale Society E3-1804 Silky	9876543226		Riverdale Society E3-1804 Silky		Maharashtra	0	30	0		t	2025-12-02 10:08:40.142076	2025-12-02 10:08:40.142081	\N	0	\N	\N	\N	t	\N	\N
30	16	CUST-0019	Riverdale Society E3-1901 Ashwini	9876543227		Riverdale Society E3-1901 Ashwini		Maharashtra	0	30	0		t	2025-12-02 10:08:40.702674	2025-12-02 10:08:40.70268	\N	0	\N	\N	\N	t	\N	\N
31	16	CUST-0020	Riverdale Society E3-2001 Paridhi	9876543228		Riverdale Society E3-2001 Paridhi		Maharashtra	0	30	0		t	2025-12-02 10:08:41.263281	2025-12-02 10:08:41.263286	\N	0	\N	\N	\N	t	\N	\N
11	11	CUST-0010	Nitish Agrawal	9479526777		Itarsi		Madhya Pradesh	0	30	0		t	2025-11-30 09:40:32.142005	2025-12-10 04:30:57.076388	\N	0	\N	\N	\N	t	2025-12-11	2025-12-12
6	11	CUST-0005	Rishi Samaiya	8983121201	rishijainwit@gmail.com	1/2 shalimar enclave E-3 arera colony		Madhya Pradesh	0	30	0		t	2025-11-22 20:29:20.886373	2025-12-10 04:32:42.367844	\N	3	\N	\N	\N	t	2025-12-11	2025-12-12
55	16	CUST-0044	Satin Bricks Society D-501 Nikita	9876543253		Satin Bricks Society D-501 Nikita		Maharashtra	0	30	0		t	2025-12-02 10:08:54.731879	2025-12-02 10:08:54.731884	\N	0	\N	\N	\N	t	\N	\N
56	16	CUST-0045	Veerodya Society A-301 Vrushali	9876543254		Veerodya Society A-301 Vrushali		Maharashtra	0	30	0		t	2025-12-02 10:08:55.293294	2025-12-02 10:08:55.293299	\N	0	\N	\N	\N	t	\N	\N
57	16	CUST-0046	Veerodya Society A-702 Amit	9876543255		Veerodya Society A-702 Amit		Maharashtra	0	30	0		t	2025-12-02 10:08:55.854008	2025-12-02 10:08:55.854014	\N	0	\N	\N	\N	t	\N	\N
58	16	CUST-0047	Ganga Platino Society R-1403 Dimple	9876543256		Ganga Platino Society R-1403 Dimple		Maharashtra	0	30	0		t	2025-12-02 10:08:56.414751	2025-12-02 10:08:56.414756	\N	0	\N	\N	\N	t	\N	\N
60	16	CUST-0049	Marvel Zyfer Society M-301 Devika	9876543258		Marvel Zyfer Society M-301 Devika		Maharashtra	0	30	0		t	2025-12-02 10:08:57.535927	2025-12-02 10:08:57.535932	\N	0	\N	\N	\N	t	\N	\N
61	16	CUST-0050	Marvel Zyfer Society M-801 Shivani	9876543259		Marvel Zyfer Society M-801 Shivani		Maharashtra	0	30	0		t	2025-12-02 10:08:58.096797	2025-12-02 10:08:58.096803	\N	0	\N	\N	\N	t	\N	\N
62	16	CUST-0051	Marvel Zyfer Society F-901 Lakshmi	9876543260		Marvel Zyfer Society F-901 Lakshmi		Maharashtra	0	30	0		t	2025-12-02 10:08:58.657748	2025-12-02 10:08:58.657753	\N	0	\N	\N	\N	t	\N	\N
63	16	CUST-0052	Marvel Zyfer Society F-1101 Uma	9876543261		Marvel Zyfer Society F-1101 Uma		Maharashtra	0	30	0		t	2025-12-02 10:08:59.218692	2025-12-02 10:08:59.218697	\N	0	\N	\N	\N	t	\N	\N
64	16	CUST-0053	Marvel Zyfer Society H-1002 Sangeeta	9876543262		Marvel Zyfer Society H-1002 Sangeeta		Maharashtra	0	30	0		t	2025-12-02 10:08:59.779456	2025-12-02 10:08:59.779461	\N	0	\N	\N	\N	t	\N	\N
78	16	CUST-0067	Zen Estate E-905 Gautam	9876543276		Zen Estate E-905 Gautam		Maharashtra	0	30	0		t	2025-12-02 10:09:07.635061	2025-12-02 10:09:07.635066	\N	0	\N	\N	\N	t	\N	\N
79	16	CUST-0068	Zen Estate G-1302 Shubham	9876543277		Zen Estate G-1302 Shubham		Maharashtra	0	30	0		t	2025-12-02 10:09:08.196552	2025-12-02 10:09:08.196557	\N	0	\N	\N	\N	t	\N	\N
80	16	CUST-0069	Marvel Zyfer Society L-302 Jyoti	9876543278		Marvel Zyfer Society L-302 Jyoti		Maharashtra	0	30	0		t	2025-12-03 19:41:20.329782	2025-12-03 19:41:20.329788	\N	0	\N	\N	\N	t	\N	\N
81	16	CUST-0070	Marvel Zyfer Society M-501 Vani	9876543279		Marvel Zyfer Society M-501 Vani		Maharashtra	0	30	0		t	2025-12-03 19:41:20.920744	2025-12-03 19:41:20.92075	\N	0	\N	\N	\N	t	\N	\N
76	16	CUST-0065	Gulmohar Parkview Lotus-305 Vanisha	9876543274		Gulmohar Parkview Lotus-305 Vanisha		Maharashtra	0	30	0		t	2025-12-02 10:09:06.512775	2025-12-03 19:59:04.950958	\N	0	28	\N	\N	t	\N	\N
77	16	CUST-0066	Gulmohar Parkview Lotus-901 Aniket	9876543275		Gulmohar Parkview Lotus-901 Aniket		Maharashtra	0	30	0		t	2025-12-02 10:09:07.074586	2025-12-03 19:59:10.726711	\N	0	28	\N	\N	t	\N	\N
75	16	CUST-0064	Gulmohar Parkview Orchid-702 Vinay	9876543273		Gulmohar Parkview Orchid-702 Vinay		Maharashtra	0	30	0		t	2025-12-02 10:09:05.951554	2025-12-03 19:59:16.501939	\N	0	28	\N	\N	t	\N	\N
72	16	CUST-0061	Gulmohar Parkview Tulip-106 Reshma	9876543270		Gulmohar Parkview Tulip-106 Reshma		Maharashtra	0	30	0		t	2025-12-02 10:09:04.267658	2025-12-03 19:59:22.278612	\N	0	28	\N	\N	t	\N	\N
73	16	CUST-0062	Gulmohar Parkview Tulip-904 Shweta	9876543271		Gulmohar Parkview Tulip-904 Shweta		Maharashtra	0	30	0		t	2025-12-02 10:09:04.82908	2025-12-03 19:59:28.050941	\N	0	28	\N	\N	t	\N	\N
74	16	CUST-0063	Gulmohar Parkview Tulip-1103 Neha	9876543272		Gulmohar Parkview Tulip-1103 Neha		Maharashtra	0	30	0		t	2025-12-02 10:09:05.390291	2025-12-03 19:59:37.968453	\N	0	28	\N	\N	t	\N	\N
82	16	CUST-0071	Marvel Zyfer Society E-201 Pradip	9876543280		Marvel Zyfer Society E-201 Pradip		Maharashtra	0	30	0		t	2025-12-03 19:41:21.481799	2025-12-03 19:41:21.481804	\N	0	\N	\N	\N	t	\N	\N
12	16	CUST-0001	Gera SOJ A2-601 Praveen Singh			Gera SOJ  A2- 601		Maharashtra	0	30	0		t	2025-12-02 09:55:46.600163	2025-12-03 19:55:07.408403	\N	0	28	\N	\N	t	\N	\N
40	16	CUST-0029	Gera Song Of Joy A1-1004 Shub.	9876543237		Gera Song Of Joy A1-1004 Shub.		Maharashtra	0	30	0		t	2025-12-02 10:08:46.311745	2025-12-03 19:55:13.197645	\N	0	28	\N	\N	t	\N	\N
34	16	CUST-0023	Gera Song Of Joy A1-401 Ruchita	9876543231		Gera Song Of Joy A1-401 Ruchita		Maharashtra	0	30	0		t	2025-12-02 10:08:42.946823	2025-12-03 19:55:18.981301	\N	0	28	\N	\N	t	\N	\N
35	16	CUST-0024	Gera Song Of Joy A1-402 Kushboo	9876543232		Gera Song Of Joy A1-402 Kushboo		Maharashtra	0	30	0		t	2025-12-02 10:08:43.50737	2025-12-03 19:55:24.757128	\N	0	28	\N	\N	t	\N	\N
37	16	CUST-0026	Gera Song Of Joy A1-603 Suruchi	9876543234		Gera Song Of Joy A1-603 Suruchi		Maharashtra	0	30	0		t	2025-12-02 10:08:44.628171	2025-12-03 19:55:30.534412	\N	0	28	\N	\N	t	\N	\N
38	16	CUST-0027	Gera Song Of Joy A1-701 Bhavna	9876543235		Gera Song Of Joy A1-701 Bhavna		Maharashtra	0	30	0		t	2025-12-02 10:08:45.18914	2025-12-03 19:55:38.910846	\N	0	28	\N	\N	t	\N	\N
39	16	CUST-0028	Gera Song Of Joy A1-802 Abhinav	9876543236		Gera Song Of Joy A1-802 Abhinav		Maharashtra	0	30	0		t	2025-12-02 10:08:45.749498	2025-12-03 19:55:44.684876	\N	0	28	\N	\N	t	\N	\N
32	16	CUST-0021	Gera Song Of Joy A1-G02 Swati	9876543229		Gera Song Of Joy A1-G02 Swati		Maharashtra	0	30	0		t	2025-12-02 10:08:41.824255	2025-12-03 19:55:50.457551	\N	0	28	\N	\N	t	\N	\N
33	16	CUST-0022	Gera Song Of Joy A1-G04 Deepti	9876543230		Gera Song Of Joy A1-G04 Deepti		Maharashtra	0	30	0		t	2025-12-02 10:08:42.385887	2025-12-03 19:55:56.232039	\N	0	28	\N	\N	t	\N	\N
41	16	CUST-0030	Gera Song Of Joy A2-101 Nikhil	9876543238		Gera Song Of Joy A2-101 Nikhil		Maharashtra	0	30	0		t	2025-12-02 10:08:46.872318	2025-12-03 19:56:02.003656	\N	0	28	\N	\N	t	\N	\N
42	16	CUST-0031	Gera Song Of Joy A2-103 Kirti	9876543239		Gera Song Of Joy A2-103 Kirti		Maharashtra	0	30	0		t	2025-12-02 10:08:47.434174	2025-12-03 19:56:07.781577	\N	0	28	\N	\N	t	\N	\N
43	16	CUST-0032	Gera Song Of Joy A2-104 Rolly	9876543240		Gera Song Of Joy A2-104 Rolly		Maharashtra	0	30	0		t	2025-12-02 10:08:47.999986	2025-12-03 19:56:16.159849	\N	0	28	\N	\N	t	\N	\N
46	16	CUST-0035	Gera Song Of Joy A2-401 Renu	9876543243		Gera Song Of Joy A2-401 Renu		Maharashtra	0	30	0		t	2025-12-02 10:08:49.683414	2025-12-03 19:56:21.930977	\N	0	28	\N	\N	t	\N	\N
48	16	CUST-0037	Gera Song Of Joy A2-702 Swati	9876543246		Gera Song Of Joy A2-702 Swati		Maharashtra	0	30	0		t	2025-12-02 10:08:50.804721	2025-12-03 19:56:27.707621	\N	0	28	\N	\N	t	\N	\N
49	16	CUST-0038	Gera Song Of Joy A2-801 Archana	9876543247		Gera Song Of Joy A2-801 Archana		Maharashtra	0	30	0		t	2025-12-02 10:08:51.365719	2025-12-03 19:56:38.692922	\N	0	28	\N	\N	t	\N	\N
50	16	CUST-0039	Gera Song Of Joy A2-802 Preeti	9876543248		Gera Song Of Joy A2-802 Preeti		Maharashtra	0	30	0		t	2025-12-02 10:08:51.927673	2025-12-03 19:56:44.466664	\N	0	28	\N	\N	t	\N	\N
53	16	CUST-0042	Gera Song Of Joy A3-1002 Pooja	9876543251		Gera Song Of Joy A3-1002 Pooja		Maharashtra	0	30	0		t	2025-12-02 10:08:53.610207	2025-12-03 19:56:50.244342	\N	0	28	\N	\N	t	\N	\N
52	16	CUST-0041	Gera Song Of Joy A3-G02 Rosslin	9876543250		Gera Song Of Joy A3-G02 Rosslin		Maharashtra	0	30	0		t	2025-12-02 10:08:53.04922	2025-12-03 19:56:56.016315	\N	0	28	\N	\N	t	\N	\N
54	16	CUST-0043	Gera Song Of Joy B1-904 Kajal	9876543252		Gera Song Of Joy B1-904 Kajal		Maharashtra	0	30	0		t	2025-12-02 10:08:54.170781	2025-12-03 19:57:01.796764	\N	0	28	\N	\N	t	\N	\N
59	16	CUST-0048	Gera South Emerald E1-501 Ankita	9876543257		Gera South Emerald E1-501 Ankita		Maharashtra	0	30	0		t	2025-12-02 10:08:56.975325	2025-12-03 19:57:07.568112	\N	0	28	\N	\N	t	\N	\N
65	16	CUST-0054	Sky Vila Gera T4-508 Zarine	9876543263		Sky Vila Gera T4-508 Zarine		Maharashtra	0	30	0		t	2025-12-02 10:09:00.340855	2025-12-03 19:57:13.344097	\N	0	28	\N	\N	t	\N	\N
66	16	CUST-0055	Sky Vila Gera T4-509 Rucha	9876543264		Sky Vila Gera T4-509 Rucha		Maharashtra	0	30	0		t	2025-12-02 10:09:00.901808	2025-12-03 19:57:19.118418	\N	0	28	\N	\N	t	\N	\N
67	16	CUST-0056	Trinity Gera 1A-1502 Shiksha	9876543265		Trinity Gera 1A-1502 Shiksha		Maharashtra	0	30	0		t	2025-12-02 10:09:01.462932	2025-12-03 19:57:24.890465	\N	0	28	\N	\N	t	\N	\N
68	16	CUST-0057	Trinity Gera 2A-105 Swati	9876543266		Trinity Gera 2A-105 Swati		Maharashtra	0	30	0		t	2025-12-02 10:09:02.023546	2025-12-03 19:57:30.667493	\N	0	28	\N	\N	t	\N	\N
69	16	CUST-0058	Trinity Gera 2A-106 Chayanika	9876543267		Trinity Gera 2A-106 Chayanika		Maharashtra	0	30	0		t	2025-12-02 10:09:02.584627	2025-12-03 19:57:36.438371	\N	0	28	\N	\N	t	\N	\N
70	16	CUST-0059	Trinity Gera 2A-207 Shruti	9876543268		Trinity Gera 2A-207 Shruti		Maharashtra	0	30	0		t	2025-12-02 10:09:03.14571	2025-12-03 19:57:39.605694	\N	0	28	\N	\N	t	\N	\N
71	16	CUST-0060	Trinity Gera 2A-507 Gurmeet	9876543269		Trinity Gera 2A-507 Gurmeet		Maharashtra	0	30	0		t	2025-12-02 10:09:03.706862	2025-12-03 19:57:50.58785	\N	0	28	\N	\N	t	\N	\N
45	16	CUST-0034	Gera Song Of Joy A2-302 Prachi	9876543242		Gera Song Of Joy A2-302 Prachi		Maharashtra	0	30	0		t	2025-12-02 10:08:49.122334	2025-12-03 19:57:56.359626	\N	0	28	\N	\N	t	\N	\N
47	16	CUST-0036	Gera Song Of Joy A2-601 Sunita Maid	9876543245		Gera Song Of Joy A2-601 Sunita Maid		Maharashtra	0	30	0		t	2025-12-02 10:08:50.244264	2025-12-03 19:58:02.132133	\N	0	28	\N	\N	t	\N	\N
51	16	CUST-0040	Gera Song Of Joy A2-902 Tanvi	9876543249		Gera Song Of Joy A2-902 Tanvi		Maharashtra	0	30	0		t	2025-12-02 10:08:52.488502	2025-12-03 19:58:07.905735	\N	0	28	\N	\N	t	\N	\N
44	16	CUST-0033	Gera Song Of Joy A2-202 Snehal	9876543241		Gera Song Of Joy A2-202 Snehal		Maharashtra	0	30	0		t	2025-12-02 10:08:48.560946	2025-12-03 19:58:13.677067	\N	0	28	\N	\N	t	\N	\N
36	16	CUST-0025	Gera Song Of Joy A1-501 Neha	9876543233		Gera Song Of Joy A1-501 Neha		Maharashtra	0	30	0		t	2025-12-02 10:08:44.067813	2025-12-03 19:58:19.450089	\N	0	28	\N	\N	t	\N	\N
83	21	CUST-0001	Rishi Samaiya	9876543210	rishi.samaiya@gmail.com	Shop 12, Market Street, Surat		Gujarat	10000	15	500	Regular customer, prefers online payment	t	2025-12-10 12:18:03.711245	2025-12-10 12:18:03.711251	\N	0	\N	\N	\N	t	1988-03-15	2015-11-20
84	21	CUST-0002	Priya Sharma	9876543211	priya.sharma@yahoo.com	A-201, Sunshine Apartments, Mumbai		Maharashtra	5000	30	0	VIP customer	t	2025-12-10 12:18:04.357273	2025-12-10 12:18:04.357278	\N	0	\N	\N	\N	t	1992-07-22	2018-02-14
85	21	CUST-0003	Amit Patel	9876543212	amit.patel@gmail.com	15, Green Plaza, Ahmedabad	24AABCP1234F1Z5	Gujarat	15000	30	1200	Wholesale buyer	t	2025-12-10 12:18:04.991769	2025-12-10 12:18:04.991774	\N	0	\N	\N	\N	t	1985-12-10	2010-05-25
86	21	CUST-0004	Sneha Verma	9876543213	sneha.v@outlook.com	B-405, Royal Heights, Pune		Maharashtra	8000	15	0	Birthday in January	t	2025-12-10 12:18:05.625201	2025-12-10 12:18:05.625206	\N	0	\N	\N	\N	t	1995-01-08	2020-12-01
87	21	CUST-0005	Rajesh Kumar	9876543214	rajesh.kumar@rediffmail.com	Plot 7, Industrial Area, Delhi	27AABCR5678M1Z3	Delhi	25000	45	3500	B2B client, high volume	t	2025-12-10 12:18:06.258637	2025-12-10 12:18:06.258642	\N	0	\N	\N	\N	t	1980-06-18	2005-04-10
88	21	CUST-0006	Neha Joshi	9876543215	neha.joshi@gmail.com	C-102, Lake View, Bangalore		Karnataka	6000	30	0		t	2025-12-10 12:18:06.894173	2025-12-10 12:18:06.894178	\N	0	\N	\N	\N	t	1990-09-25	2016-07-15
89	21	CUST-0007	Vikram Singh	9876543216	vikram.s@yahoo.in	56, MG Road, Jaipur		Rajasthan	12000	30	800	Prefers cash payment	t	2025-12-10 12:18:07.52888	2025-12-10 12:18:07.528885	\N	0	\N	\N	\N	t	1987-04-30	2012-09-08
90	21	CUST-0008	Anjali Mehta	9876543217	anjali.mehta@hotmail.com	Shop 3, City Center, Surat	24AABCM9012G1Z8	Gujarat	20000	60	2500	Corporate client	t	2025-12-10 12:18:08.165812	2025-12-10 12:18:08.165818	\N	0	\N	\N	\N	t	1983-11-05	2008-03-22
91	21	CUST-0009	Karan Thakur	9876543218	karan.thakur@gmail.com	D-301, Skyline Towers, Hyderabad		Telangana	7000	15	0		t	2025-12-10 12:18:08.799441	2025-12-10 12:18:08.799446	\N	0	\N	\N	\N	t	1993-08-17	2019-11-30
92	21	CUST-0010	Divya Reddy	9876543219	divya.reddy@outlook.in	12-A, Park Avenue, Chennai		Tamil Nadu	9000	30	350	Birthday end of Feb	t	2025-12-10 12:18:09.433098	2025-12-10 12:18:09.433103	\N	0	\N	\N	\N	t	1991-02-28	2017-06-10
93	21	CUST-0011	Rohit Agarwal	9876543220	rohit.ag@gmail.com	45, Station Road, Indore		Madhya Pradesh	11000	30	0	Birthday in December	t	2025-12-10 12:18:10.068393	2025-12-10 12:18:10.068398	\N	0	\N	\N	\N	t	1989-12-15	2014-08-25
94	21	CUST-0012	Pooja Gupta	9876543221	pooja.gupta@yahoo.com	E-501, Ocean View, Mumbai	27AABCG3456H1Z9	Maharashtra	18000	45	1800	Wholesale dealer	t	2025-12-10 12:18:10.701623	2025-12-10 12:18:10.701629	\N	0	\N	\N	\N	t	1986-05-20	2011-01-17
95	21	CUST-0013	Suresh Rao	9876543222	suresh.rao@rediffmail.com	23, Temple Street, Mysore		Karnataka	5000	15	0		t	2025-12-10 12:18:11.335494	2025-12-10 12:18:11.3355	\N	0	\N	\N	\N	t	1994-10-12	2021-02-28
96	21	CUST-0014	Kavita Desai	9876543223	kavita.desai@gmail.com	F-102, City Heights, Nagpur		Maharashtra	8500	30	600	Regular buyer	t	2025-12-10 12:18:11.969256	2025-12-10 12:18:11.969261	\N	0	\N	\N	\N	t	1990-06-05	2015-09-14
97	21	CUST-0015	Manish Jain	9876543224	manish.jain@outlook.com	78, Business Hub, Rajkot	24AABCJ7890K1Z2	Gujarat	22000	60	4200	B2B premium client	t	2025-12-10 12:18:12.603568	2025-12-10 12:18:12.603573	\N	0	\N	\N	\N	t	1982-03-28	2007-12-20
\.


--
-- Data for Name: delivery_challan_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.delivery_challan_items (id, delivery_challan_id, tenant_id, item_id, item_name, description, hsn_code, quantity, unit, rate, amount, serial_numbers, quantity_invoiced, quantity_returned, sales_order_item_id, created_at, sales_order_id, taxable_value, gst_rate, cgst_amount, sgst_amount, igst_amount, total_amount, batch_number, serial_number, notes, updated_at) FROM stdin;
2	7	11	39	Bajaj LED Bulb 9W Cool White B22	\N		25.000	pcs	120.00	\N	\N	0.000	0.000	19	2025-11-06 12:53:04.977004	15	3000.00	12.00	180.00	180.00	0.00	3360.00	\N	\N	\N	2025-11-06 12:53:04.97701
3	8	11	39	Bajaj LED Bulb 9W Cool White B22	\N		10.000	pcs	120.00	\N	\N	0.000	0.000	18	2025-11-06 13:01:56.728891	14	1200.00	12.00	72.00	72.00	0.00	1344.00	\N	\N	\N	2025-11-06 13:01:56.728898
4	9	11	9	Bajaj Table Fan 400mm White	\N		10.000	pcs	850.00	\N	\N	0.000	0.000	17	2025-11-06 13:42:31.396522	13	8500.00	18.00	765.00	765.00	0.00	10030.00	\N	\N	\N	2025-11-06 13:42:31.396528
5	6	11	10	Orient Table Fan 400mm Blue	\N		5.000	pcs	950.00	\N	\N	0.000	0.000	\N	2025-11-06 18:12:19.339045	\N	4750.00	18.00	427.50	427.50	0.00	5605.00	\N	\N	\N	2025-11-06 18:12:19.339052
6	6	11	39	Bajaj LED Bulb 9W Cool White B22	\N		10.000	Pcs	120.00	\N	\N	0.000	0.000	\N	2025-11-06 18:12:19.339055	\N	1200.00	0.00	0.00	0.00	0.00	1200.00	\N	\N	\N	2025-11-06 18:12:19.339057
\.


--
-- Data for Name: delivery_challans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.delivery_challans (id, tenant_id, challan_number, challan_date, customer_id, customer_name, customer_phone, customer_gstin, customer_billing_address, customer_shipping_address, purpose, transporter_name, vehicle_number, lr_number, e_way_bill_number, total_quantity, total_amount, status, sales_order_id, expected_return_date, actual_return_date, notes, terms, created_at, updated_at, created_by, customer_email, customer_state, subtotal, cgst_amount, sgst_amount, igst_amount, delivery_note, dispatched_at, delivered_at, invoiced_at) FROM stdin;
9	11	DC-2511-0004	2025-11-06	4	Sharma Traders	9988776655				Sale				\N	\N	10030.00	delivered	13	\N	\N			2025-11-06 13:42:31.192386	2025-11-06 13:42:55.5988	\N	sharma@gmail.com	Maharashtra	8500.00	765.00	765.00	0.00		\N	2025-11-06 13:42:55.597728	\N
6	11	DC-2511-0001	2025-11-06	3	Rishi Enterprises	9876543210	27AABCU9603R1ZM			Sale				\N	\N	6805.00	delivered	16	\N	\N			2025-11-06 12:48:01.037548	2025-11-06 18:13:12.210651	\N	rishi.samaiya@gmail.com	Maharashtra	5950.00	427.50	427.50	0.00		\N	2025-11-06 18:13:12.20954	\N
7	11	DC-2511-0002	2025-11-06	3	Rishi Enterprises	9876543210	27AABCU9603R1ZM			Sale				\N	\N	3360.00	delivered	15	\N	\N			2025-11-06 12:53:04.757379	2025-11-06 18:14:07.382463	\N	rishi.samaiya@gmail.com	Maharashtra	3000.00	180.00	180.00	0.00		2025-11-06 12:55:03.583697	2025-11-06 18:14:07.381874	\N
8	11	DC-2511-0003	2025-11-06	2	ABC Corporation	9876543210	27AABCU9603R1ZM			Sale				\N	\N	1344.00	invoiced	14	\N	\N			2025-11-06 13:01:56.526633	2025-11-06 18:22:33.072037	\N	contact@abc.com	Maharashtra	1200.00	72.00	72.00	0.00		\N	2025-11-06 18:22:13.664649	2025-11-06 18:22:33.070801
\.


--
-- Data for Name: delivery_day_notes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.delivery_day_notes (id, tenant_id, note_date, note_text, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employees (id, tenant_id, name, pin, phone, document_path, site_id, active, created_at, updated_at, email, monthly_salary, date_of_joining, designation) FROM stdin;
15	11	Sagar Jain	3333	9766460248	\N	13	f	2025-11-02 18:05:48.24095	2025-11-10 04:32:24.586381	sagarjain26@gmail.com	0.00	\N	\N
18	11	Vaibhav jain	1212	83758 13228	\N	12	t	2025-11-09 20:17:40.68143	2025-11-25 04:30:11.768776	coolvaibhav.jain88@gmail.com	0.00	\N	\N
21	11	Rohit Jain	6666	7000968289	\N	12	t	2025-11-26 04:39:24.387445	2025-11-26 04:39:24.38745	11rohit84@gmail.com	0.00	\N	\N
22	13	Engineer Santram	1001	9876543210	\N	20	t	2025-11-28 19:08:20.833759	2025-11-28 19:08:20.833765	john@example.com	0.00	\N	\N
23	13	Engineer Nilesh	1002	\N	\N	20	t	2025-11-28 19:08:21.413933	2025-11-28 19:08:21.413939	\N	0.00	\N	\N
24	13	Supervisor Vijay	1003	\N	\N	20	t	2025-11-28 19:08:21.978056	2025-11-28 19:08:21.978062	\N	0.00	\N	\N
25	13	PM Ayush	1004	9174901901	\N	21	t	2025-11-28 19:08:22.724446	2025-11-28 19:08:22.724453	ayush.agrawal@live.com	0.00	\N	\N
26	13	Engineer Kush	1005		\N	21	t	2025-11-28 19:09:45.45734	2025-11-28 19:09:45.457346		0.00	\N	\N
13	11	Rishi Jain	1111	8983121201	\N	13	t	2025-11-02 18:05:47.114793	2025-11-30 19:48:13.644669	rishi.samaiya@gmail.com	10000.00	2025-01-01	sales
14	11	Ayushi Samaiya	2222	9617217821	\N	13	t	2025-11-02 18:05:47.680442	2025-11-30 19:49:24.399726	ayushi.samaiya@gmail.com	12000.00	2025-08-01	marketing
16	11	Shubham sethi	4444	8099476801	\N	13	t	2025-11-02 18:05:48.806425	2025-11-30 20:08:29.810083	sethishubham@gmail.com	15000.00	2025-09-01	helper
17	11	Vikash Chauhan	5555	7276963330	\N	13	t	2025-11-02 18:05:49.366476	2025-11-30 20:12:36.735428	vikashchauhan2310@gmail.com	9000.00	2025-09-01	sales
27	11	Ram kishan	8983	8983121201	\N	12	t	2025-12-01 05:49:00.219839	2025-12-01 05:49:00.219845	rishijainwit@gmail.com	25000.00	2025-01-01	Manager
28	16	Kalidas	1001		\N	24	t	2025-12-03 19:53:39.383042	2025-12-03 19:53:39.383048		\N	\N	\N
29	16	Balaji	1002		\N	24	t	2025-12-03 19:54:05.278492	2025-12-03 19:54:05.278498		\N	\N	\N
30	21	Rajesh Kumar	1001	9876500001	\N	26	t	2025-12-10 11:30:45.02004	2025-12-10 13:11:22.222493	rajesh.kumar@fashionhub.com	8000.00	2024-01-15	Store Manager
32	21	Amit Patel	1003	9876500003	\N	26	t	2025-12-10 11:30:46.233207	2025-12-10 13:13:12.122399	amit.patel@fashionhub.com	8000.00	2024-02-15	Sales Associate
33	21	Sneha Reddy	1004	9876500004	\N	26	t	2025-12-10 11:30:46.833518	2025-12-10 13:13:27.713586	sneha.reddy@fashionhub.com	8000.00	2024-03-01	Cashier
34	21	Vikram Singh	1005	9876500005	\N	26	t	2025-12-10 11:30:47.434007	2025-12-10 13:14:54.532155	vikram.singh@fashionhub.com	6000.00	2024-03-15	Helper
35	21	Anjali Mehta	1006	9876500006	\N	26	t	2025-12-10 11:30:48.234166	2025-12-10 13:15:09.387167	anjali.mehta@fashionhub.com	10000.00	2024-01-20	Assistant Manager
36	21	Rajesh Iyer	1007	9876500007	\N	26	t	2025-12-10 11:30:48.834281	2025-12-10 13:15:27.20002	rajesh.iyer@fashionhub.com	8000.00	2024-02-10	Sales Associate
37	21	Kavita Nair	1008	9876500008	\N	26	t	2025-12-10 11:30:49.434457	2025-12-10 13:15:47.864623	kavita.nair@fashionhub.com	8000.00	2024-02-20	Sales Associate
38	21	Deepak Joshi	1009	9876500009	\N	26	t	2025-12-10 11:30:50.033704	2025-12-10 13:16:08.478374	deepak.joshi@fashionhub.com	8000.00	2024-03-10	Cashier
31	21	Priya Sharma	1002	9876500002	\N	26	t	2025-12-10 11:30:45.628868	2025-12-10 13:16:27.615475	priya.sharma@fashionhub.com	8000.00	2024-02-01	Sales Associate
\.


--
-- Data for Name: expense_categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.expense_categories (id, tenant_id, name, description, is_active, created_at) FROM stdin;
3	11	local fotkar	local shopping for employee	t	2025-11-02 19:17:36.128602
4	11	Contra	expense under contra category	t	2025-11-30 10:47:31.67264
\.


--
-- Data for Name: expenses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.expenses (id, tenant_id, expense_date, category_id, amount, description, payment_method, reference_number, vendor_name, attachment_url, created_by, created_at, updated_at) FROM stdin;
7	11	2025-11-03	3	1000	Paint (Qty: 1.0) - Requested by Rishi Jain	Pending	PR-11	Ta shah	\N	\N	2025-11-02 19:27:01.612866	\N
8	11	2025-11-03	3	1000	Playwood (Qty: 5.0) - Requested by Rishi Jain	Pending	PR-13	TA shah	\N	\N	2025-11-03 04:17:42.139607	\N
9	11	2025-11-03	3	300	Hshsh (Qty: 2.0) - Requested by Rishi Jain	Pending	PR-14	Nsb	\N	\N	2025-11-03 04:17:53.675301	\N
10	11	2025-11-03	3	100	This is test (Qty: 1.0) - Requested by Rishi Jain	Cash	PR-17	Ta	\N	\N	2025-11-03 04:18:33.424094	\N
11	11	2025-11-03	3	600	Cemet (Qty: 2.0) - Requested by Rishi Jain	Cash	PR-18	Mp stone	\N	\N	2025-11-03 05:45:16.822037	\N
12	11	2025-11-30	3	2000	expense on local fotkar	Bank Transfer			\N	Mahaveer Electricals	2025-11-29 19:31:12.168266	\N
13	11	2025-11-30	4	1000	Santosh helper: weekly payment	Cash			\N	Mahaveer Electricals	2025-11-30 10:48:15.588919	\N
14	11	2025-11-30	4	3000	Rent for JCB	Cash		JCB	\N	Mahaveer Electricals	2025-11-30 10:49:03.35505	\N
\.


--
-- Data for Name: inventory_adjustment_lines; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventory_adjustment_lines (id, adjustment_id, item_id, site_id, quantity_before, value_before, quantity_adjusted, value_adjusted, quantity_after, value_after) FROM stdin;
\.


--
-- Data for Name: inventory_adjustments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.inventory_adjustments (id, tenant_id, adjustment_number, adjustment_date, mode, reason, description, account, status, created_by, adjusted_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: invoice_commissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.invoice_commissions (id, tenant_id, invoice_id, agent_id, agent_name, agent_code, commission_percentage, invoice_amount, commission_amount, is_paid, paid_date, payment_notes, created_at, updated_at) FROM stdin;
1	11	24	1	Vaibhav jain	EMP-1212	1	850	8.5	f	\N	\N	2025-11-09 20:20:59.551056	2025-11-09 20:20:59.551061
2	11	25	2	Ijaaz	\N	1	950	9.5	t	2025-11-10		2025-11-10 04:04:47.419289	2025-11-10 04:11:39.172142
3	11	30	3	Rishi Jain	EMP-1111	1	1475	14.75	f	\N	\N	2025-11-20 19:10:32.476533	2025-11-20 19:10:32.476538
\.


--
-- Data for Name: invoice_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.invoice_items (id, invoice_id, item_id, item_name, description, hsn_code, quantity, unit, rate, gst_rate, taxable_value, cgst_amount, sgst_amount, igst_amount, total_amount, sales_order_item_id, delivery_challan_item_id) FROM stdin;
19	11	13	Anchor Penta 6A Switch White			1	Nos	72.03389830508475	18	72.03389830508475	6.483050847457626	6.483050847457626	0	85	\N	\N
20	12	13	Anchor Penta 6A Switch White			10	Nos	72.03389830508475	18	720.3389830508474	64.83050847457628	64.83050847457628	0	850	\N	\N
21	13	5	Bajaj Ceiling Fan 48			1	Nos	1228.813559322034	18	1228.813559322034	110.59322033898297	110.59322033898297	0	1450	\N	\N
23	14	11	Bajaj Exhaust Fan 8			1	Nos	650	18	650	58.5	58.5	0	767	\N	\N
24	15	7	Havells SS-390 Ceiling Fan 48" Pearl White			10	Nos	1950	18	19500	1755	1755	0	23010	\N	\N
26	16	7	Havells SS-390 Ceiling Fan 48			10	Nos	1400.4576271186443	18	14004.576271186443	1260.4118644067794	1260.4118644067794	0	16525.4	\N	\N
27	17	13	Anchor Penta 6A Switch White			50	Nos	72.03389830508475	18	3601.6949152542375	324.15254237288127	324.15254237288127	0	4250	\N	\N
28	18	6	HBL Premium Ceiling Fan 52" White			10	Nos	1567.7966101694915	18	15677.966101694916	1411.016949152542	1411.016949152542	0	18500	\N	\N
29	19	6	HBL Premium Ceiling Fan 52" White			10	Nos	1567.7966101694915	18	15677.966101694916	1411.016949152542	1411.016949152542	0	18500	\N	\N
30	20	10	Orient Table Fan 400mm Blue			5	Nos	950	18	4750	427.5	427.5	0	5605	\N	\N
31	21	39	Bajaj LED Bulb 9W Cool White B22			10	Nos	107.14285714285714	12	1071.4285714285713	64.28571428571433	64.28571428571433	0	1200	\N	\N
32	22	53	Bajaj Edge Fan 48		8414	1	Nos	1300	18	1300	117	117	0	1534	\N	\N
33	23	7	Havells SS-390 Ceiling Fan 48			1	Nos	1950	12	1950	117	117	0	2184	\N	\N
34	23	5	Bajaj Ceiling Fan 48			1	Nos	1450	12	1450	87	87	0	1624	\N	\N
35	23	53	Bajaj Edge Fan 48		8414	1	Nos	1411	12	1411	84.66	84.66	0	1580.32	\N	\N
36	23	6	HBL Premium Ceiling Fan 52			1	Nos	1850	12	1850	111	111	0	2072	\N	\N
37	24	9	Bajaj Table Fan 400mm White			1	Nos	720.3389830508474	18	720.3389830508474	64.83050847457628	64.83050847457628	0	850	\N	\N
38	25	12	Havells Exhaust Fan 12			1	Nos	805.0847457627119	18	805.0847457627119	72.45762711864404	72.45762711864404	0	950	\N	\N
40	27	\N	Subscription - Monthly Gym Membership	Monthly Gym Membership - Nov 2025	\N	1	Service	500	0	500	0	0	0	500	\N	\N
41	28	\N	Subscription - Monthly Gym Membership	Monthly Gym Membership - Dec 2025	\N	1	Service	500	0	500	0	0	0	500	\N	\N
42	29	\N	Subscription - Monthly Gym Membership	Monthly Gym Membership - Nov 2025	\N	1	Service	500	0	500	0	0	0	500	\N	\N
43	30	14	Anchor Penta 16A Socket White			10	Nos	125	18	1250	112.5	112.5	0	1475	\N	\N
44	31	\N	Subscription - Daily milk Delivery	Daily milk Delivery\nNov 22 - Nov 30, 2025\nTotal: 18.00 liter	\N	18	liter	80	0	1440	0	0	0	1440	\N	\N
45	32	\N	Subscription - Daily milk Delivery	Daily milk Delivery\nNov 23 - Nov 30, 2025\nTotal: 10.50 liter	\N	10.5	liter	80	0	840	0	0	0	840	\N	\N
49	38	59	Ghee	\N		1	ltr	1000	0	1000	0	0	0	1000	\N	\N
50	39	58	Paneer	\N		0.5	kg	400	0	200	0	0	0	200	\N	\N
51	40	58	Paneer	\N		0.5	kg	400	0	200	0	0	0	200	\N	\N
52	41	59	Ghee	\N		1	ltr	1000	0	1000	0	0	0	1000	\N	\N
53	42	58	Paneer	\N		0.5	kg	400	0	200	0	0	0	200	\N	\N
54	43	59	Ghee	\N		1	ltr	1000	0	1000	0	0	0	1000	\N	\N
55	44	58	Paneer	\N		0.5	kg	400	0	200	0	0	0	200	\N	\N
56	45	59	Ghee	\N		1	ltr	1000	0	1000	0	0	0	1000	\N	\N
57	46	59	Ghee	\N		0.5	ltr	1000	0	500	0	0	0	500	\N	\N
58	47	59	Ghee	\N		0.5	ltr	1000	0	500	0	0	0	500	\N	\N
59	48	58	Paneer	\N		0.2	kg	400	0	80	0	0	0	80	\N	\N
60	49	59	Ghee	\N		0.5	ltr	1000	0	500	0	0	0	500	\N	\N
61	50	58	Paneer	\N		0.2	kg	400	0	80	0	0	0	80	\N	\N
62	51	58	Paneer	\N		0.2	kg	400	0	80	0	0	0	80	\N	\N
63	52	59	Ghee	\N		0.5	ltr	1000	0	500	0	0	0	500	\N	\N
64	53	8	Havells Leganza Ceiling Fan 52			1	Nos	2150	0	2150	0	0	0	2150	\N	\N
66	55	15	Anchor Penta 6A 2-Way Switch White			10	Nos	80.5084745762712	18	805.0847457627119	72.45762711864404	72.45762711864404	0	950	\N	\N
67	56	11	Bajaj Exhaust Fan 8			1	Nos	550.8474576271187	18	550.8474576271187	0	0	99.15254237288127	650	\N	\N
68	57	39	Bajaj LED Bulb 9W Cool White B22			10	Nos	101.6949152542373	18	1016.949152542373	91.52542372881351	91.52542372881351	0	1200	\N	\N
69	58	39	Bajaj LED Bulb 9W Cool White B22			10	Nos	101.6949152542373	18	1016.949152542373	91.52542372881351	91.52542372881351	0	1200	\N	\N
70	59	\N	Subscription - Daily milk Delivery	Daily milk Delivery\nNov 23 - Nov 30, 2025\nTotal: 13.00 liter	\N	13	liter	80	0	1040	0	0	0	1040	\N	\N
71	60	57	Anchor wire 1.5 Sq mm			1	Nos	1525.4237288135594	18	1525.4237288135594	137.28813559322032	137.28813559322032	0	1800	\N	\N
72	61	56	Anchor wire 1 Sq mm			1	Nos	1350	18	1350	0	0	0	1350	\N	\N
73	62	57	Anchor wire 1.5 Sq mm			6	Nos	1525.4237288135594	18	9152.542372881357	823.7288135593217	823.7288135593217	0	10800	\N	\N
74	63	57	Anchor wire 1.5 Sq mm			1	Nos	1525.4237288135594	18	1525.4237288135594	137.28813559322032	137.28813559322032	0	1800	\N	\N
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.invoices (id, tenant_id, invoice_number, invoice_date, due_date, customer_name, customer_phone, customer_email, customer_address, customer_gstin, customer_state, subtotal, cgst_amount, sgst_amount, igst_amount, discount_amount, round_off, total_amount, payment_status, paid_amount, payment_method, notes, internal_notes, status, cancelled_at, cancelled_reason, created_at, updated_at, customer_id, sales_order_id, delivery_challan_id, discount_type, discount_value, gst_enabled, loyalty_discount, loyalty_points_redeemed, loyalty_points_earned) FROM stdin;
11	11	INV-2025-0001	2025-11-03	\N	ABC Corporation	9876543210	contact@abc.com	123 Business Park, Mumbai, 400001	27AABCU9603R1ZM	Maharashtra	72.03389830508475	6.483050847457626	6.483050847457626	0	0	0	85	paid	85	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-03 06:02:26.661827	2025-11-03 06:02:26.661833	2	\N	\N	flat	0.00	t	0.00	0	0
12	11	INV-2025-0002	2025-11-03	\N	ABC Corporation	9876543210	contact@abc.com	123 Business Park, Mumbai, 400001	27AABCU9603R1ZM	Maharashtra	720.3389830508474	64.83050847457628	64.83050847457628	0	0	0	850	unpaid	0	\N	Payment due within 30 days. Goods once sold will not be taken back.	\N	draft	\N	\N	2025-11-03 06:08:47.659306	2025-11-03 06:08:47.659312	2	\N	\N	flat	0.00	t	0.00	0	0
13	11	INV-2025-0003	2025-11-03	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Maharashtra	1228.813559322034	110.59322033898297	110.59322033898297	0	0	0	1450	paid	1450	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-03 06:16:17.962992	2025-11-03 06:16:17.962998	3	\N	\N	flat	0.00	t	0.00	0	0
14	11	INV-2025-0004	2025-11-06	\N	ABC Corporation	9876543210	contact@abc.com		27AABCU9603R1ZM	Maharashtra	650	58.5	58.5	0	0	0	767	paid	767	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-06 10:03:17.465387	2025-11-06 10:31:26.084269	2	\N	\N	flat	0.00	t	0.00	0	0
15	11	INV-2025-0005	2025-11-06	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com		27AABCU9603R1ZM	Maharashtra	19500	1755	1755	0	0	0	23010	paid	23010	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-06 10:41:26.438383	2025-11-06 10:41:26.438389	3	\N	\N	flat	0.00	t	0.00	0	0
16	11	INV-2025-0006	2025-11-06	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com		27AABCU9603R1ZM	Maharashtra	14004.576271186443	1260.4118644067794	1260.4118644067794	0	0	-0.4000000000014552	16525	paid	16525	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-06 10:42:19.742769	2025-11-06 10:43:27.604315	3	\N	\N	flat	0.00	t	0.00	0	0
17	11	INV-2025-0007	2025-11-06	\N	Sharma Traders	9988776655	sharma@gmail.com			Maharashtra	3601.6949152542375	324.15254237288127	324.15254237288127	0	0	0	4250	paid	4250	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-06 10:50:55.003646	2025-11-06 10:50:55.003652	4	\N	\N	flat	0.00	t	0.00	0	0
18	11	INV-2025-0008	2025-11-06	\N	Sharma Traders	9988776655	sharma@gmail.com			Maharashtra	15677.966101694916	1411.016949152542	1411.016949152542	0	0	0	18500	paid	18500	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-06 11:24:55.905818	2025-11-06 11:24:55.905824	4	8	\N	flat	0.00	t	0.00	0	0
19	11	INV-2025-0009	2025-11-06	\N	Sharma Traders	9988776655	sharma@gmail.com			Maharashtra	15677.966101694916	1411.016949152542	1411.016949152542	0	0	0	18500	paid	18500	Cash	Payment due within 30 days. Goods once sold will not be taken back.	\N	sent	\N	\N	2025-11-06 11:33:45.329407	2025-11-06 11:33:45.329413	4	8	\N	flat	0.00	t	0.00	0	0
20	11	INV-2025-0010	2025-11-06	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com		27AABCU9603R1ZM	Maharashtra	4750	427.5	427.5	0	0	0	5605	unpaid	0	\N	Payment due within 30 days. Goods once sold will not be taken back.	\N	draft	\N	\N	2025-11-06 14:29:23.398321	2025-11-06 14:29:23.398327	3	16	\N	flat	0.00	t	0.00	0	0
21	11	INV-2025-0011	2025-11-06	\N	ABC Corporation	9876543210	contact@abc.com		27AABCU9603R1ZM	Maharashtra	1071.4285714285713	64.28571428571433	64.28571428571433	0	0	0	1200	unpaid	0	\N	Payment due within 30 days. Goods once sold will not be taken back.	\N	draft	\N	\N	2025-11-06 18:22:31.221463	2025-11-06 18:22:31.221469	2	\N	8	flat	0.00	t	0.00	0	0
22	11	INV-2025-0012	2025-11-08	\N	Shubham Sethi	8983121212				Madhya Pradesh	1300	117	117	0	0	0	1534	unpaid	0	\N	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	draft	\N	\N	2025-11-08 10:13:58.115909	2025-11-08 10:13:58.115915	5	\N	\N	flat	0.00	t	0.00	0	0
23	11	INV-2025-0013	2025-11-08	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Madhya Pradesh	6661	399.65999999999997	399.65999999999997	0	0	-0.31999999999970896	7460	unpaid	0	\N	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	draft	\N	\N	2025-11-08 19:36:17.673753	2025-11-08 19:36:17.673785	3	\N	\N	flat	0.00	t	0.00	0	0
24	11	INV-2025-0014	2025-11-09	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Madhya Pradesh	720.3389830508474	64.83050847457628	64.83050847457628	0	0	0	850	paid	850	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-11-09 20:20:57.926115	2025-11-09 20:20:57.926121	3	\N	\N	flat	0.00	t	0.00	0	0
25	11	INV-2025-0015	2025-11-10	\N	Sharma Traders	9988776655	sharma@gmail.com	Main Market, Indore		Madhya Pradesh	805.0847457627119	72.45762711864404	72.45762711864404	0	0	0	950	paid	950	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-11-10 04:04:45.879104	2025-11-10 04:04:45.879111	4	\N	\N	flat	0.00	t	0.00	0	0
27	11	SUB-20251112183905	2025-11-12	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	\N	\N	\N	0	0	0	0	0	0	500	paid	500	Cash	\N	\N	paid	\N	\N	2025-11-12 18:39:05.217682	2025-11-12 18:39:05.217687	3	\N	\N	flat	0.00	t	0.00	0	0
28	11	SUB-20251112184614	2025-11-12	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	\N	\N	\N	0	0	0	0	0	0	500	paid	500	Cash	\N	\N	paid	\N	\N	2025-11-12 18:46:14.809493	2025-11-12 18:46:14.809498	3	\N	\N	flat	0.00	t	0.00	0	0
29	11	SUB-20251113101248	2025-11-13	\N	Shubham Sethi	8983121212		\N	\N	\N	0	0	0	0	0	0	500	paid	500	Cash	\N	\N	paid	\N	\N	2025-11-13 10:12:48.825221	2025-11-13 10:12:48.825225	5	\N	\N	flat	0.00	t	0.00	0	0
30	11	INV-2025-0016	2025-11-20	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Madhya Pradesh	1250	112.5	112.5	0	0	0	1475	paid	1475	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-11-20 19:10:30.909026	2025-11-20 19:10:30.909032	3	\N	\N	flat	0.00	t	0.00	0	0
31	11	SUB-20251123035927	2025-11-23	\N	Rishi Samaiya	8983121201	rishijainwit@gmail.com	\N	\N	\N	0	0	0	0	0	0	1440	unpaid	0	\N	\N	\N	pending	\N	\N	2025-11-23 03:59:27.08351	2025-11-23 03:59:27.083515	6	\N	\N	flat	0.00	t	0.00	0	0
32	11	SUB-20251123041924	2025-11-23	\N	Khush Jain	8983121201	11rohit84@gmail.com	\N	\N	\N	0	0	0	0	0	0	840	unpaid	0	\N	\N	\N	pending	\N	\N	2025-11-23 04:19:24.625335	2025-11-23 04:19:24.62534	7	\N	\N	flat	0.00	t	0.00	0	0
38	11	INV-2025-017	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	1000	0	0	0	0	0	1000	unpaid	0	\N	Generated from customer order	\N	sent	\N	\N	2025-11-24 08:01:37.143585	2025-11-24 08:01:37.143592	8	\N	\N	flat	0.00	t	0.00	0	0
39	11	INV-2025-018	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	200	0	0	0	0	0	200	unpaid	0	\N	Generated from customer order	\N	sent	\N	\N	2025-11-24 08:22:58.705894	2025-11-24 08:22:58.7059	8	\N	\N	flat	0.00	t	0.00	0	0
40	11	INV-2025-019	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	200	0	0	0	0	0	200	unpaid	0	\N	Generated from customer order	\N	sent	\N	\N	2025-11-24 08:35:08.923354	2025-11-24 08:35:08.923361	8	\N	\N	flat	0.00	t	0.00	0	0
41	11	INV-2025-020	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	1000	0	0	0	0	0	1000	unpaid	0	\N	Generated from customer order	\N	sent	\N	\N	2025-11-24 08:41:39.134987	2025-11-24 08:41:39.134994	8	\N	\N	flat	0.00	t	0.00	0	0
42	11	INV-2025-021	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	200	0	0	0	0	0	200	unpaid	0	\N	Generated from customer order	\N	sent	\N	\N	2025-11-24 08:53:41.512748	2025-11-24 08:53:41.512754	8	\N	\N	flat	0.00	t	0.00	0	0
43	11	INV-2025-022	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	1000	0	0	0	0	0	1000	paid	1000	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 09:10:32.813087	2025-11-24 09:10:33.953441	8	\N	\N	flat	0.00	t	0.00	0	0
44	11	INV-2025-023	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	200	0	0	0	0	0	200	paid	200	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 09:23:20.887423	2025-11-24 09:23:22.017445	8	\N	\N	flat	0.00	t	0.00	0	0
45	11	INV-2025-024	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	1000	0	0	0	0	0	1000	paid	1000	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 09:40:54.053245	2025-11-24 09:40:55.188802	8	\N	\N	flat	0.00	t	0.00	0	0
46	11	INV-2025-025	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	500	0	0	0	0	0	500	paid	500	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 09:47:09.21749	2025-11-24 09:47:10.358457	8	\N	\N	flat	0.00	t	0.00	0	0
47	11	INV-2025-026	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	500	0	0	0	0	0	500	paid	500	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 10:00:39.549876	2025-11-24 10:00:40.791387	8	\N	\N	flat	0.00	t	0.00	0	0
48	11	INV-2025-027	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	80	0	0	0	0	0	80	paid	80	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 10:07:16.174161	2025-11-24 10:07:17.388248	8	\N	\N	flat	0.00	t	0.00	0	0
49	11	INV-2025-028	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	500	0	0	0	0	0	500	paid	500	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 10:28:56.507096	2025-11-24 10:28:57.662579	8	\N	\N	flat	0.00	t	0.00	0	0
50	11	INV-2025-029	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	80	0	0	0	0	0	80	paid	80	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 10:42:16.966818	2025-11-24 10:42:18.107059	8	\N	\N	flat	0.00	t	0.00	0	0
51	11	INV-2025-030	2025-11-24	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	80	0	0	0	0	0	80	paid	80	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 10:51:06.569302	2025-11-24 10:51:07.708418	8	\N	\N	flat	0.00	t	0.00	0	0
52	11	INV-2025-031	2025-11-24	\N	Shubham Sethi	7032018290	sethishubham@gmail.com	1/2 shalimar enclave		Madhya Pradesh	500	0	0	0	0	0	500	paid	500	UPI	Generated from customer order	\N	sent	\N	\N	2025-11-24 18:26:09.07334	2025-11-24 18:26:10.232965	5	\N	\N	flat	0.00	t	0.00	0	0
53	11	INV-2025-0032	2025-11-29	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Madhya Pradesh	2150	0	0	0	0	0	2150	paid	2150	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-11-29 12:13:46.142826	2025-11-29 12:13:46.142833	8	\N	\N	flat	0.00	t	0.00	0	0
55	11	INV-2025-0033	2025-11-29	\N	Rishi Samaiya	8983121201	rishijainwit@gmail.com	1/2 shalimar enclave E-3 arera colony		Madhya Pradesh	805.0847457627119	72.45762711864404	72.45762711864404	0	0	0	950	paid	950	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-11-29 16:50:08.001917	2025-11-29 16:50:08.001924	6	\N	\N	flat	0.00	t	0.00	0	0
56	11	INV-2025-0034	2025-11-29	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	1/2 shalimar enclave		Maharashtra	550.8474576271187	0	0	99.15254237288127	0	0	650	paid	650	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-11-29 18:23:22.513933	2025-11-29 18:23:22.51394	8	\N	\N	flat	0.00	t	0.00	0	0
57	11	INV-2025-0035	2025-11-29	\N	Shubham Sethi	7032018290	sethishubham@gmail.com	1/2 shalimar enclave		Madhya Pradesh	1016.949152542373	91.52542372881351	91.52542372881351	0	0	0	1200	unpaid	0	\N	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	draft	\N	\N	2025-11-29 18:24:53.215355	2025-11-29 18:24:53.215361	5	\N	\N	flat	0.00	t	0.00	0	0
58	11	INV-2025-0036	2025-11-29	\N	Shubham Sethi	7032018290	sethishubham@gmail.com	1/2 shalimar enclave		Madhya Pradesh	1016.949152542373	91.52542372881351	91.52542372881351	0	0	0	1200	paid	1200	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	draft	\N	\N	2025-11-29 19:07:31.410013	2025-11-29 19:18:52.677212	5	\N	\N	flat	0.00	t	0.00	0	0
59	11	SUB-20251202202054	2025-12-02	\N	Ayushi Samaiya	9617217821	ayushi.samaiya@gmail.com	\N	\N	\N	0	0	0	0	0	0	1040	unpaid	0	\N	\N	\N	pending	\N	\N	2025-12-02 20:20:54.498456	2025-12-02 20:20:54.498462	8	\N	\N	flat	0.00	t	0.00	0	0
60	11	INV-2025-0037	2025-12-08	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Madhya Pradesh	1449.1537288135594	130.42383559322033	130.42383559322033	0	76.27	-0.001399999999875945	1710	unpaid	0	\N	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	draft	\N	\N	2025-12-08 08:23:39.245931	2025-12-08 08:23:39.245937	3	\N	\N	flat	0.00	t	0.00	0	0
61	11	INV-2025-0038	2025-12-08	\N	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	Shop 12, MG Road, Indore	27AABCU9603R1ZM	Madhya Pradesh	1350	0	0	0	0	0	1350	paid	1350	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-12-08 08:26:52.405133	2025-12-08 08:26:52.40514	3	\N	\N	flat	0.00	f	0.00	0	0
62	11	INV-2025-0039	2025-12-10	\N	Rishi Samaiya	8983121201	rishijainwit@gmail.com	1/2 shalimar enclave E-3 arera colony		Madhya Pradesh	9152.542372881357	823.7288135593217	823.7288135593217	0	0	0	10800	paid	10800	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-12-10 05:47:12.838097	2025-12-10 05:47:17.462432	6	\N	\N	flat	0.00	t	0.00	0	308
63	11	INV-2025-0040	2025-12-10	\N	Rishi Samaiya	8983121201	rishijainwit@gmail.com	1/2 shalimar enclave E-3 arera colony		Madhya Pradesh	1525.4237288135594	137.28813559322032	137.28813559322032	0	0	0	1750	paid	1750	Cash	Payment due within 30 days.\r\nGoods once sold will not be taken back.\r\nSubject to Pune jurisdiction only.	\N	sent	\N	\N	2025-12-10 06:22:28.464537	2025-12-10 06:22:35.644229	6	\N	\N	flat	0.00	t	50.00	50	17
\.


--
-- Data for Name: item_categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.item_categories (id, tenant_id, name, description, parent_category_id, created_at, updated_at, group_id) FROM stdin;
73	21	Men's Wear	\N	\N	2025-12-10 12:02:52.151126	2025-12-10 12:02:52.151131	46
74	21	Men's Wear	\N	\N	2025-12-10 12:03:02.666577	2025-12-10 12:03:02.666583	47
75	21	Men's Wear	\N	\N	2025-12-10 12:03:14.251089	2025-12-10 12:03:14.251095	48
76	21	Men's Wear	\N	\N	2025-12-10 12:03:19.109343	2025-12-10 12:03:19.109349	49
77	21	Women's Wear	\N	\N	2025-12-10 12:03:29.57861	2025-12-10 12:03:29.578616	50
78	21	Women's Wear	\N	\N	2025-12-10 12:03:44.523908	2025-12-10 12:03:44.523915	51
79	21	Women's Wear	\N	\N	2025-12-10 12:03:48.261764	2025-12-10 12:03:48.26177	52
80	21	Women's Wear	\N	\N	2025-12-10 12:03:50.690011	2025-12-10 12:03:50.690016	46
81	21	Women's Wear	\N	\N	2025-12-10 12:03:58.922217	2025-12-10 12:03:58.922223	53
82	21	Kids Wear	\N	\N	2025-12-10 12:04:03.595874	2025-12-10 12:04:03.595881	49
83	21	Kids Wear	\N	\N	2025-12-10 12:04:08.272851	2025-12-10 12:04:08.272858	46
84	21	Kids Wear	\N	\N	2025-12-10 12:04:10.891582	2025-12-10 12:04:10.891588	54
85	21	Accessories	\N	\N	2025-12-10 12:04:12.385705	2025-12-10 12:04:12.385711	55
86	21	Accessories	\N	\N	2025-12-10 12:04:17.248106	2025-12-10 12:04:17.248111	56
15	11	Ceiling Fans	\N	\N	2025-11-02 11:06:04.925081	2025-11-02 11:06:04.925087	13
16	11	Table Fans	\N	\N	2025-11-02 11:06:10.762501	2025-11-02 11:06:10.762508	13
17	11	Exhaust Fans	\N	\N	2025-11-02 11:06:13.185623	2025-11-02 11:06:13.185629	13
18	11	Switches & Sockets	\N	\N	2025-11-02 11:06:15.792995	2025-11-02 11:06:15.793001	14
19	11	MCBs & Distribution	\N	\N	2025-11-02 11:06:23.80326	2025-11-02 11:06:23.803266	14
20	11	PVC Pipes & Conduits	\N	\N	2025-11-02 11:06:27.527792	2025-11-02 11:06:27.527798	15
21	11	Pipe Fittings	\N	\N	2025-11-02 11:06:32.185514	2025-11-02 11:06:32.185519	15
22	11	Clamps & Bands	\N	\N	2025-11-02 11:06:40.19997	2025-11-02 11:06:40.199975	15
23	11	LED Bulbs	\N	\N	2025-11-02 11:06:46.159352	2025-11-02 11:06:46.159358	16
24	11	LED Battens	\N	\N	2025-11-02 11:06:54.16638	2025-11-02 11:06:54.166386	16
25	11	Downlights	\N	\N	2025-11-02 11:06:58.821054	2025-11-02 11:06:58.821061	16
36	11	Contra	expense under contra category	\N	2025-11-30 10:46:45.65209	2025-11-30 10:46:45.652096	\N
38	16	Dairy Product		\N	2025-12-02 08:55:45.762428	2025-12-02 08:55:45.762432	\N
\.


--
-- Data for Name: item_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.item_groups (id, tenant_id, name, description, created_at, updated_at) FROM stdin;
13	11	Fans	\N	2025-11-02 11:06:04.537158	2025-11-02 11:06:04.537165
14	11	Electrical Accessories	\N	2025-11-02 11:06:15.420963	2025-11-02 11:06:15.42097
15	11	Wiring & Fittings	\N	2025-11-02 11:06:27.155405	2025-11-02 11:06:27.155411
16	11	Lighting	\N	2025-11-02 11:06:45.787093	2025-11-02 11:06:45.787099
17	16	Dairy Product		2025-12-02 08:56:56.988287	2025-12-02 08:56:56.988291
46	21	Jeans	\N	2025-12-10 12:02:51.771008	2025-12-10 12:02:51.771015
47	21	Shirts	\N	2025-12-10 12:03:02.292766	2025-12-10 12:03:02.292773
48	21	Trousers	\N	2025-12-10 12:03:13.877593	2025-12-10 12:03:13.877599
49	21	T-Shirts	\N	2025-12-10 12:03:18.736152	2025-12-10 12:03:18.736159
50	21	Kurtas	\N	2025-12-10 12:03:29.204913	2025-12-10 12:03:29.20492
51	21	Tops	\N	2025-12-10 12:03:44.150258	2025-12-10 12:03:44.150263
52	21	Dresses	\N	2025-12-10 12:03:47.888535	2025-12-10 12:03:47.88854
53	21	Leggings	\N	2025-12-10 12:03:58.549211	2025-12-10 12:03:58.549216
54	21	Shorts	\N	2025-12-10 12:04:10.518357	2025-12-10 12:04:10.518364
55	21	Bags	\N	2025-12-10 12:04:12.012289	2025-12-10 12:04:12.012296
56	21	Belts	\N	2025-12-10 12:04:16.87495	2025-12-10 12:04:16.874957
\.


--
-- Data for Name: item_images; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.item_images (id, item_id, image_url, is_primary, display_order, uploaded_at) FROM stdin;
\.


--
-- Data for Name: item_stock_movements; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.item_stock_movements (id, tenant_id, item_id, site_id, movement_type, quantity, unit_cost, total_value, reference_number, reference_type, reference_id, from_site_id, to_site_id, reason, notes, created_by, created_at, updated_at) FROM stdin;
3	11	13	12	stock_out	10	85	850	INV-2025-0002	invoice	12	\N	\N	Sale	Sold via Invoice (Customer: ABC Corporation)	Mahaveer Electricals	2025-11-03 06:08:48.039479	2025-11-03 06:08:49.026423
4	11	5	12	stock_out	1	1450	1450	INV-2025-0003	invoice	13	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-03 06:16:18.340091	2025-11-03 06:16:19.28167
5	11	11	12	stock_out	1	650	650	INV-2025-0004	invoice	14	\N	\N	Sale	Sold via Invoice (Customer: ABC Corporation)	Mahaveer Electricals	2025-11-06 10:03:17.864099	2025-11-06 10:03:18.832207
6	11	7	12	stock_out	10	1950	19500	INV-2025-0005	invoice	15	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-06 10:41:26.851276	2025-11-06 10:41:27.805568
7	11	7	12	stock_out	10	1950	19500	INV-2025-0006	invoice	16	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-06 10:42:20.11515	2025-11-06 10:42:21.046831
8	11	13	12	stock_out	50	85	4250	INV-2025-0007	invoice	17	\N	\N	Sale	Sold via Invoice (Customer: Sharma Traders)	Mahaveer Electricals	2025-11-06 10:50:55.38019	2025-11-06 10:50:56.321423
9	11	6	12	stock_out	10	1850	18500	\N	invoice	\N	\N	\N	Sale	Sold via Invoice (Customer: Sharma Traders)	Mahaveer Electricals	2025-11-06 11:24:56.289929	2025-11-06 11:24:56.289934
25	11	12	12	stock_out	1	950	950	INV-2025-0015	invoice	25	\N	\N	Sale	Sold via Invoice (Customer: Sharma Traders)	Mahaveer Electricals	2025-11-10 04:04:46.272134	2025-11-10 04:04:48.365169
10	11	6	12	stock_out	10	1850	18500	INV-2025-0009	invoice	19	\N	\N	Sale	Sold via Invoice (Customer: Sharma Traders)	Mahaveer Electricals	2025-11-06 11:33:45.709939	2025-11-06 11:33:46.647765
11	11	10	12	stock_out	5	950	4750	INV-2025-0010	invoice	20	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-06 14:29:23.793014	2025-11-06 14:29:24.74824
12	11	39	12	stock_out	10	120	1200	INV-2025-0011	invoice	21	\N	\N	Sale	Sold via Invoice (Customer: ABC Corporation)	Mahaveer Electricals	2025-11-06 18:22:31.64526	2025-11-06 18:22:32.669476
13	11	4	12	stock_in	5	1500	7500	PB-202511-0008	purchase_bill	27	\N	\N	Purchase Bill Approval	Vendor: Rishi Jain	Admin	2025-11-07 18:47:06.70351	2025-11-07 18:47:06.703517
14	11	5	12	stock_in	9	1500	13500	PB-202511-0008	purchase_bill	27	\N	\N	Purchase Bill Approval	Vendor: Rishi Jain	Admin	2025-11-07 18:47:07.847896	2025-11-07 18:47:07.847902
15	11	53	12	opening_stock	8	1411	11288	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-11-08 09:54:40.62074	2025-11-08 09:54:40.620745
16	11	53	12	stock_out	1	1411	1411	INV-2025-0012	invoice	22	\N	\N	Sale	Sold via Invoice (Customer: Shubham Sethi)	Mahaveer Electricals	2025-11-08 10:13:58.532559	2025-11-08 10:13:59.491202
18	11	53	12	transfer_out	-1	\N	\N	\N	transfer	\N	12	13	\N	Transfer to site 13: 	\N	2025-11-08 12:36:24.965102	2025-11-08 12:36:24.965108
19	11	53	13	transfer_in	1	\N	\N	\N	transfer	\N	12	13	\N	Transfer from site 12: 	\N	2025-11-08 12:36:24.96511	2025-11-08 12:36:24.965112
20	11	7	12	stock_out	1	1950	1950	INV-2025-0013	invoice	23	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-08 19:36:15.028339	2025-11-08 19:36:19.015818
21	11	5	12	stock_out	1	1472.5	1472.5	INV-2025-0013	invoice	23	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-08 19:36:15.987184	2025-11-08 19:36:19.015818
22	11	53	12	stock_out	1	1411	1411	INV-2025-0013	invoice	23	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-08 19:36:16.924661	2025-11-08 19:36:19.015818
23	11	6	12	stock_out	1	1850	1850	INV-2025-0013	invoice	23	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-08 19:36:18.065497	2025-11-08 19:36:19.015818
24	11	9	12	stock_out	1	850	850	\N	invoice	\N	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-09 20:20:58.372968	2025-11-09 20:20:58.372974
26	11	56	12	opening_stock	100	1100	110000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-11-17 04:59:37.416706	2025-11-17 04:59:37.416713
27	11	57	12	opening_stock	100	1800	180000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-11-17 05:47:12.749068	2025-11-17 05:47:12.749076
28	11	14	12	stock_out	10	125	1250	INV-2025-0016	invoice	30	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-11-20 19:10:31.318957	2025-11-20 19:10:33.424845
29	11	58	12	opening_stock	5	350	1750	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-11-23 12:30:37.378723	2025-11-23 12:30:37.378729
30	11	59	12	opening_stock	10	900	9000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-11-23 14:03:00.436431	2025-11-23 14:03:00.436436
31	11	59	12	stock_out	1	900	900	INV-2025-017	invoice	38	\N	\N	\N	Sold via invoice INV-2025-017 (Customer Order: ORD-00002)	\N	2025-11-24 08:01:38.462176	2025-11-24 08:01:38.462181
32	11	58	12	stock_out	0.5	350	175	INV-2025-018	invoice	39	\N	\N	\N	Sold via invoice INV-2025-018 (Customer Order: ORD-00001)	\N	2025-11-24 08:23:00.053424	2025-11-24 08:23:00.053429
33	11	58	12	stock_out	0.5	350	175	INV-2025-019	invoice	40	\N	\N	\N	Sold via invoice INV-2025-019 (Customer Order: ORD-00003)	\N	2025-11-24 08:35:10.255084	2025-11-24 08:35:10.25509
34	11	59	12	stock_out	1	900	900	INV-2025-020	invoice	41	\N	\N	\N	Sold via invoice INV-2025-020 (Customer Order: ORD-00004)	\N	2025-11-24 08:41:40.457077	2025-11-24 08:41:40.457083
35	11	58	12	stock_out	0.5	350	175	INV-2025-021	invoice	42	\N	\N	\N	Sold via invoice INV-2025-021 (Customer Order: ORD-00005)	\N	2025-11-24 08:53:42.833095	2025-11-24 08:53:42.833101
36	11	59	12	stock_out	1	900	900	INV-2025-022	invoice	43	\N	\N	\N	Sold via invoice INV-2025-022 (Customer Order: ORD-00006)	\N	2025-11-24 09:10:34.328668	2025-11-24 09:10:34.328674
37	11	58	12	stock_out	0.5	350	175	INV-2025-023	invoice	44	\N	\N	\N	Sold via invoice INV-2025-023 (Customer Order: ORD-00007)	\N	2025-11-24 09:23:22.39289	2025-11-24 09:23:22.392895
38	11	59	12	stock_out	1	900	900	INV-2025-024	invoice	45	\N	\N	\N	Sold via invoice INV-2025-024 (Customer Order: ORD-00008)	\N	2025-11-24 09:40:55.56498	2025-11-24 09:40:55.564986
39	11	59	12	stock_out	0.5	900	450	INV-2025-025	invoice	46	\N	\N	\N	Sold via invoice INV-2025-025 (Customer Order: ORD-00009)	\N	2025-11-24 09:47:10.735338	2025-11-24 09:47:10.735343
40	11	59	12	stock_out	0.5	900	450	INV-2025-026	invoice	47	\N	\N	\N	Sold via invoice INV-2025-026 (Customer Order: ORD-00010)	\N	2025-11-24 10:00:41.195611	2025-11-24 10:00:41.195617
41	11	58	12	stock_out	0.2	350	70	INV-2025-027	invoice	48	\N	\N	\N	Sold via invoice INV-2025-027 (Customer Order: ORD-00011)	\N	2025-11-24 10:07:17.792139	2025-11-24 10:07:17.792144
42	11	59	12	stock_out	0.5	900	450	INV-2025-028	invoice	49	\N	\N	\N	Sold via invoice INV-2025-028 (Customer Order: ORD-00012)	\N	2025-11-24 10:28:58.039841	2025-11-24 10:28:58.039846
43	11	58	12	stock_out	0.2	350	70	INV-2025-029	invoice	50	\N	\N	\N	Sold via invoice INV-2025-029 (Customer Order: ORD-00013)	\N	2025-11-24 10:42:18.481867	2025-11-24 10:42:18.481873
44	11	58	12	stock_out	0.2	350	70	INV-2025-030	invoice	51	\N	\N	\N	Sold via invoice INV-2025-030 (Customer Order: ORD-00014)	\N	2025-11-24 10:51:08.08327	2025-11-24 10:51:08.083275
45	11	59	12	stock_out	0.5	900	450	INV-2025-031	invoice	52	\N	\N	\N	Sold via invoice INV-2025-031 (Customer Order: ORD-00015)	\N	2025-11-24 18:26:10.610664	2025-11-24 18:26:10.61067
46	11	8	12	stock_out	1	2150	2150	INV-2025-0032	invoice	53	\N	\N	Sale	Sold via Invoice (Customer: Ayushi Samaiya)	Mahaveer Electricals	2025-11-29 12:13:46.580902	2025-11-29 12:13:47.557314
48	11	15	12	stock_out	10	95	950	INV-2025-0033	invoice	55	\N	\N	Sale	Sold via Invoice (Customer: Rishi Samaiya)	Mahaveer Electricals	2025-11-29 16:50:08.382331	2025-11-29 16:50:09.894201
49	11	11	12	stock_out	1	650	650	INV-2025-0034	invoice	56	\N	\N	Sale	Sold via Invoice (Customer: Ayushi Samaiya)	Mahaveer Electricals	2025-11-29 18:23:22.907274	2025-11-29 18:23:24.421617
50	11	39	12	stock_out	10	120	1200	\N	invoice	\N	\N	\N	Sale	Sold via Invoice (Customer: Shubham Sethi)	Mahaveer Electricals	2025-11-29 18:24:53.632737	2025-11-29 18:24:53.632744
51	11	39	12	stock_out	10	120	1200	INV-2025-0036	invoice	58	\N	\N	Sale	Sold via Invoice (Customer: Shubham Sethi)	Mahaveer Electricals	2025-11-29 19:07:31.816791	2025-11-29 19:07:32.778003
52	16	60	18	opening_stock	3.5	480	1680	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-12-02 08:59:17.471565	2025-12-02 08:59:17.47157
53	16	61	18	opening_stock	10	1000	10000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-12-02 09:01:33.707984	2025-12-02 09:01:33.70799
54	16	62	18	opening_stock	1000	20	20000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-12-02 09:21:56.58618	2025-12-02 09:21:56.586186
55	16	63	18	opening_stock	1000	40	40000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-12-02 09:24:46.960918	2025-12-02 09:24:46.960924
56	16	64	18	opening_stock	1000	30	30000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-12-02 09:29:30.751007	2025-12-02 09:29:30.751012
57	16	65	18	opening_stock	1000	60	60000	\N	\N	\N	\N	\N	Opening stock	\N	System	2025-12-02 09:31:15.27053	2025-12-02 09:31:15.270537
58	11	57	12	stock_out	1	1700	1700	INV-2025-0037	invoice	60	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-12-08 08:23:39.665622	2025-12-08 08:23:40.696956
59	11	56	12	stock_out	1	1100	1100	INV-2025-0038	invoice	61	\N	\N	Sale	Sold via Invoice (Customer: Rishi Enterprises)	Mahaveer Electricals	2025-12-08 08:26:52.825063	2025-12-08 08:26:54.47342
60	11	57	12	stock_out	6	1700	10200	INV-2025-0039	invoice	62	\N	\N	Sale	Sold via Invoice (Customer: Rishi Samaiya)	Mahaveer Electricals	2025-12-10 05:47:13.239924	2025-12-10 05:47:18.21647
61	11	57	12	stock_out	1	1700	1700	INV-2025-0040	invoice	63	\N	\N	Sale	Sold via Invoice (Customer: Rishi Samaiya)	Mahaveer Electricals	2025-12-10 06:22:28.876598	2025-12-10 06:22:36.396029
\.


--
-- Data for Name: item_stocks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.item_stocks (id, tenant_id, item_id, site_id, quantity_available, quantity_committed, stock_value, valuation_method, last_stock_date, created_at, updated_at) FROM stdin;
17	11	16	12	60	0	5700	FIFO	2025-11-02 11:06:19.890647	2025-11-02 11:06:19.890676	2025-11-02 11:06:19.89068
18	11	17	12	40	0	11400	FIFO	2025-11-02 11:06:21.008565	2025-11-02 11:06:21.008596	2025-11-02 11:06:21.008599
19	11	18	12	90	0	6750	FIFO	2025-11-02 11:06:22.126818	2025-11-02 11:06:22.126848	2025-11-02 11:06:22.126851
20	11	19	12	70	0	8050	FIFO	2025-11-02 11:06:23.245123	2025-11-02 11:06:23.245152	2025-11-02 11:06:23.245156
21	11	20	12	50	0	7500	FIFO	2025-11-02 11:06:24.548253	2025-11-02 11:06:24.548286	2025-11-02 11:06:24.548289
22	11	21	12	40	0	7200	FIFO	2025-11-02 11:06:25.666669	2025-11-02 11:06:25.666699	2025-11-02 11:06:25.666702
23	11	22	12	30	0	8550	FIFO	2025-11-02 11:06:26.783692	2025-11-02 11:06:26.783723	2025-11-02 11:06:26.783726
24	11	23	12	200	0	9000	FIFO	2025-11-02 11:06:28.273559	2025-11-02 11:06:28.273589	2025-11-02 11:06:28.273592
25	11	24	12	150	0	9750	FIFO	2025-11-02 11:06:29.391245	2025-11-02 11:06:29.391274	2025-11-02 11:06:29.391277
26	11	25	12	100	0	9500	FIFO	2025-11-02 11:06:30.510187	2025-11-02 11:06:30.510216	2025-11-02 11:06:30.510219
27	11	26	12	50	0	1250	FIFO	2025-11-02 11:06:31.627524	2025-11-02 11:06:31.627555	2025-11-02 11:06:31.627559
28	11	27	12	500	0	4000	FIFO	2025-11-02 11:06:32.930665	2025-11-02 11:06:32.930697	2025-11-02 11:06:32.9307
29	11	28	12	400	0	4800	FIFO	2025-11-02 11:06:34.048065	2025-11-02 11:06:34.048095	2025-11-02 11:06:34.048099
30	11	29	12	300	0	3000	FIFO	2025-11-02 11:06:35.16545	2025-11-02 11:06:35.165481	2025-11-02 11:06:35.165484
31	11	30	12	250	0	3750	FIFO	2025-11-02 11:06:36.284303	2025-11-02 11:06:36.284335	2025-11-02 11:06:36.284338
32	11	31	12	200	0	4400	FIFO	2025-11-02 11:06:37.408284	2025-11-02 11:06:37.408312	2025-11-02 11:06:37.408315
33	11	32	12	350	0	2100	FIFO	2025-11-02 11:06:38.525684	2025-11-02 11:06:38.525714	2025-11-02 11:06:38.525717
34	11	33	12	280	0	2520	FIFO	2025-11-02 11:06:39.642341	2025-11-02 11:06:39.642371	2025-11-02 11:06:39.642374
35	11	34	12	100	0	3500	FIFO	2025-11-02 11:06:40.945034	2025-11-02 11:06:40.945065	2025-11-02 11:06:40.945068
36	11	35	12	80	0	3600	FIFO	2025-11-02 11:06:42.061621	2025-11-02 11:06:42.061654	2025-11-02 11:06:42.061657
37	11	36	12	120	0	3000	FIFO	2025-11-02 11:06:43.180553	2025-11-02 11:06:43.180585	2025-11-02 11:06:43.180588
38	11	37	12	100	0	3200	FIFO	2025-11-02 11:06:44.29801	2025-11-02 11:06:44.29804	2025-11-02 11:06:44.298043
39	11	38	12	90	0	1620	FIFO	2025-11-02 11:06:45.415286	2025-11-02 11:06:45.415315	2025-11-02 11:06:45.415318
41	11	40	12	120	0	19800	FIFO	2025-11-02 11:06:48.020559	2025-11-02 11:06:48.02059	2025-11-02 11:06:48.020593
42	11	41	12	100	0	21000	FIFO	2025-11-02 11:06:49.137501	2025-11-02 11:06:49.137531	2025-11-02 11:06:49.137534
43	11	42	12	140	0	15400	FIFO	2025-11-02 11:06:50.255083	2025-11-02 11:06:50.255113	2025-11-02 11:06:50.255117
44	11	43	12	130	0	18850	FIFO	2025-11-02 11:06:51.373674	2025-11-02 11:06:51.373704	2025-11-02 11:06:51.373707
45	11	44	12	110	0	20350	FIFO	2025-11-02 11:06:52.491612	2025-11-02 11:06:52.491642	2025-11-02 11:06:52.491645
46	11	45	12	90	0	12150	FIFO	2025-11-02 11:06:53.608777	2025-11-02 11:06:53.608807	2025-11-02 11:06:53.608811
47	11	46	12	60	0	27000	FIFO	2025-11-02 11:06:54.911557	2025-11-02 11:06:54.911586	2025-11-02 11:06:54.911589
48	11	47	12	50	0	37500	FIFO	2025-11-02 11:06:56.027596	2025-11-02 11:06:56.027625	2025-11-02 11:06:56.027628
49	11	48	12	55	0	26400	FIFO	2025-11-02 11:06:57.145902	2025-11-02 11:06:57.145932	2025-11-02 11:06:57.145935
50	11	49	12	45	0	35100	FIFO	2025-11-02 11:06:58.263186	2025-11-02 11:06:58.263217	2025-11-02 11:06:58.26322
51	11	50	12	70	0	19950	FIFO	2025-11-02 11:06:59.566844	2025-11-02 11:06:59.566873	2025-11-02 11:06:59.566877
52	11	51	12	50	0	19250	FIFO	2025-11-02 11:07:00.683524	2025-11-02 11:07:00.683558	2025-11-02 11:07:00.683562
53	11	53	12	5	0	7055	FIFO	2025-11-08 09:54:40.390517	2025-11-08 09:54:40.390558	2025-11-08 19:36:16.738324
7	11	6	12	-11	0	-20350	FIFO	2025-11-02 11:06:07.969864	2025-11-02 11:06:07.969896	2025-11-08 19:36:17.879525
66	16	62	18	1000	0	20000	FIFO	2025-12-02 09:21:56.381869	2025-12-02 09:21:56.38191	2025-12-02 09:21:56.381914
10	11	9	12	19	0	16150	FIFO	2025-11-02 11:06:11.508864	2025-11-02 11:06:11.508894	2025-11-09 20:20:58.176776
67	16	63	18	1000	0	40000	FIFO	2025-12-02 09:24:46.770423	2025-12-02 09:24:46.770461	2025-12-02 09:24:46.770465
14	11	13	12	40	0	3400	FIFO	2025-11-02 11:06:16.53796	2025-11-02 11:06:16.537989	2025-11-06 10:50:55.192935
13	11	12	12	17	0	16150	FIFO	2025-11-02 11:06:15.049267	2025-11-02 11:06:15.049298	2025-11-10 04:04:46.082321
68	16	64	18	1000	0	30000	FIFO	2025-12-02 09:29:30.564696	2025-12-02 09:29:30.564736	2025-12-02 09:29:30.564739
11	11	10	12	10	0	9500	FIFO	2025-11-02 11:06:12.62712	2025-11-02 11:06:12.627149	2025-11-06 14:29:23.606003
69	16	65	18	1000	0	60000	FIFO	2025-12-02 09:31:15.07188	2025-12-02 09:31:15.071915	2025-12-02 09:31:15.071918
5	11	4	12	20	0	29250	FIFO	2025-11-07 18:47:06.312752	2025-11-02 11:06:05.712744	2025-11-07 18:47:06.510874
57	11	56	13	0	0	0	FIFO	2025-11-17 04:59:37.220918	2025-11-17 04:59:37.220926	2025-11-17 04:59:37.220928
59	11	57	13	0	0	0	FIFO	2025-11-17 05:47:12.555127	2025-11-17 05:47:12.555136	2025-11-17 05:47:12.555138
56	11	56	12	99	0	108900	FIFO	2025-11-17 04:59:37.220862	2025-11-17 04:59:37.220899	2025-12-08 08:26:52.625861
54	11	53	13	1	0	0	FIFO	2025-11-08 09:54:40.390578	2025-11-08 09:54:40.390587	2025-11-08 12:36:24.777307
8	11	7	12	-13	0	-25350	FIFO	2025-11-02 11:06:09.086675	2025-11-02 11:06:09.086703	2025-11-08 19:36:14.829612
6	11	5	12	19	0	27977.5	FIFO	2025-11-07 18:47:07.284926	2025-11-02 11:06:06.851504	2025-11-08 19:36:15.801056
15	11	14	12	70	0	8750	FIFO	2025-11-02 11:06:17.655827	2025-11-02 11:06:17.655856	2025-11-20 19:10:31.126782
61	11	58	13	0	0	0	FIFO	2025-11-23 12:30:37.179212	2025-11-23 12:30:37.179219	2025-11-23 12:30:37.179221
63	11	59	13	0	0	0	FIFO	2025-11-23 14:03:00.231499	2025-11-23 14:03:00.231507	2025-11-23 14:03:00.231509
60	11	58	12	2.4	0	840	FIFO	2025-11-23 12:30:37.179169	2025-11-23 12:30:37.179204	2025-11-24 10:51:07.895829
62	11	59	12	4	0	3600	FIFO	2025-11-23 14:03:00.231443	2025-11-23 14:03:00.231481	2025-11-24 18:26:10.421214
9	11	8	12	5	0	10750	FIFO	2025-11-02 11:06:10.204299	2025-11-02 11:06:10.204362	2025-11-29 12:13:46.383903
58	11	57	12	92	0	156400	FIFO	2025-11-17 05:47:12.555055	2025-11-17 05:47:12.555094	2025-12-10 06:22:28.682803
16	11	15	12	65	0	6175	FIFO	2025-11-02 11:06:18.774373	2025-11-02 11:06:18.774404	2025-11-29 16:50:08.19437
70	21	232	26	20	0	36000	FIFO	2025-12-10 12:02:52.93103	2025-12-10 12:02:52.931067	2025-12-10 12:02:52.93107
71	21	233	26	35	0	63000	FIFO	2025-12-10 12:02:54.063592	2025-12-10 12:02:54.063625	2025-12-10 12:02:54.063628
12	11	11	12	23	0	14950	FIFO	2025-11-02 11:06:13.93107	2025-11-02 11:06:13.931098	2025-11-29 18:23:22.718232
72	21	234	26	30	0	54000	FIFO	2025-12-10 12:02:55.18457	2025-12-10 12:02:55.184601	2025-12-10 12:02:55.184604
40	11	39	12	120	0	14400	FIFO	2025-11-02 11:06:46.90395	2025-11-02 11:06:46.90398	2025-11-29 19:07:31.62384
64	16	60	18	3.5	0	1680	FIFO	2025-12-02 08:59:17.275209	2025-12-02 08:59:17.275247	2025-12-02 08:59:17.275251
65	16	61	18	10	0	10000	FIFO	2025-12-02 09:01:33.520105	2025-12-02 09:01:33.520137	2025-12-02 09:01:33.52014
73	21	235	26	18	0	32400	FIFO	2025-12-10 12:02:56.306114	2025-12-10 12:02:56.306145	2025-12-10 12:02:56.306148
74	21	236	26	28	0	50400	FIFO	2025-12-10 12:02:57.427547	2025-12-10 12:02:57.427578	2025-12-10 12:02:57.427581
75	21	237	26	25	0	35000	FIFO	2025-12-10 12:02:58.55481	2025-12-10 12:02:58.554843	2025-12-10 12:02:58.554846
76	21	238	26	40	0	56000	FIFO	2025-12-10 12:02:59.678466	2025-12-10 12:02:59.678497	2025-12-10 12:02:59.6785
77	21	239	26	32	0	44800	FIFO	2025-12-10 12:03:00.79885	2025-12-10 12:03:00.798882	2025-12-10 12:03:00.798885
78	21	240	26	30	0	42000	FIFO	2025-12-10 12:03:01.920024	2025-12-10 12:03:01.920057	2025-12-10 12:03:01.92006
79	21	241	26	22	0	23100	FIFO	2025-12-10 12:03:03.41494	2025-12-10 12:03:03.414972	2025-12-10 12:03:03.414975
80	21	242	26	35	0	36750	FIFO	2025-12-10 12:03:04.535368	2025-12-10 12:03:04.535401	2025-12-10 12:03:04.535403
81	21	243	26	28	0	29400	FIFO	2025-12-10 12:03:05.655709	2025-12-10 12:03:05.655743	2025-12-10 12:03:05.655746
82	21	244	26	20	0	21000	FIFO	2025-12-10 12:03:06.775925	2025-12-10 12:03:06.775959	2025-12-10 12:03:06.775962
83	21	245	26	30	0	31500	FIFO	2025-12-10 12:03:07.898008	2025-12-10 12:03:07.898041	2025-12-10 12:03:07.898044
84	21	246	26	25	0	26250	FIFO	2025-12-10 12:03:09.01921	2025-12-10 12:03:09.019242	2025-12-10 12:03:09.019245
85	21	247	26	28	0	21000	FIFO	2025-12-10 12:03:10.140143	2025-12-10 12:03:10.140178	2025-12-10 12:03:10.140181
86	21	248	26	40	0	30000	FIFO	2025-12-10 12:03:11.261615	2025-12-10 12:03:11.261648	2025-12-10 12:03:11.261651
87	21	249	26	35	0	26250	FIFO	2025-12-10 12:03:12.382701	2025-12-10 12:03:12.382734	2025-12-10 12:03:12.382737
88	21	250	26	30	0	22500	FIFO	2025-12-10 12:03:13.503216	2025-12-10 12:03:13.50325	2025-12-10 12:03:13.503253
89	21	251	26	22	0	29700	FIFO	2025-12-10 12:03:14.998667	2025-12-10 12:03:14.998702	2025-12-10 12:03:14.998705
90	21	252	26	30	0	40500	FIFO	2025-12-10 12:03:16.121018	2025-12-10 12:03:16.121052	2025-12-10 12:03:16.121055
91	21	253	26	25	0	33750	FIFO	2025-12-10 12:03:17.241526	2025-12-10 12:03:17.241558	2025-12-10 12:03:17.241561
92	21	254	26	20	0	27000	FIFO	2025-12-10 12:03:18.362557	2025-12-10 12:03:18.362591	2025-12-10 12:03:18.362594
93	21	255	26	40	0	26000	FIFO	2025-12-10 12:03:19.856758	2025-12-10 12:03:19.85679	2025-12-10 12:03:19.856793
94	21	256	26	35	0	22750	FIFO	2025-12-10 12:03:20.9809	2025-12-10 12:03:20.980933	2025-12-10 12:03:20.980944
95	21	257	26	38	0	24700	FIFO	2025-12-10 12:03:22.102388	2025-12-10 12:03:22.102422	2025-12-10 12:03:22.102425
96	21	258	26	32	0	20800	FIFO	2025-12-10 12:03:23.22393	2025-12-10 12:03:23.223963	2025-12-10 12:03:23.223966
97	21	259	26	30	0	19500	FIFO	2025-12-10 12:03:24.345865	2025-12-10 12:03:24.345899	2025-12-10 12:03:24.345903
98	21	260	26	35	0	19250	FIFO	2025-12-10 12:03:25.465976	2025-12-10 12:03:25.466007	2025-12-10 12:03:25.46601
99	21	261	26	30	0	16500	FIFO	2025-12-10 12:03:26.590931	2025-12-10 12:03:26.590962	2025-12-10 12:03:26.590965
100	21	262	26	32	0	17600	FIFO	2025-12-10 12:03:27.711928	2025-12-10 12:03:27.711961	2025-12-10 12:03:27.711964
101	21	263	26	28	0	15400	FIFO	2025-12-10 12:03:28.832303	2025-12-10 12:03:28.832334	2025-12-10 12:03:28.832337
102	21	264	26	25	0	23750	FIFO	2025-12-10 12:03:30.32649	2025-12-10 12:03:30.326521	2025-12-10 12:03:30.326524
103	21	265	26	45	0	42750	FIFO	2025-12-10 12:03:31.447476	2025-12-10 12:03:31.44751	2025-12-10 12:03:31.447513
104	21	266	26	35	0	33250	FIFO	2025-12-10 12:03:32.568019	2025-12-10 12:03:32.568052	2025-12-10 12:03:32.568055
105	21	267	26	40	0	38000	FIFO	2025-12-10 12:03:33.688683	2025-12-10 12:03:33.688715	2025-12-10 12:03:33.688718
106	21	268	26	32	0	30400	FIFO	2025-12-10 12:03:34.808868	2025-12-10 12:03:34.808902	2025-12-10 12:03:34.808905
107	21	269	26	30	0	28500	FIFO	2025-12-10 12:03:35.929144	2025-12-10 12:03:35.929177	2025-12-10 12:03:35.92918
108	21	270	26	35	0	22750	FIFO	2025-12-10 12:03:37.049128	2025-12-10 12:03:37.049161	2025-12-10 12:03:37.049164
109	21	271	26	30	0	19500	FIFO	2025-12-10 12:03:38.169459	2025-12-10 12:03:38.169493	2025-12-10 12:03:38.169496
110	21	272	26	38	0	24700	FIFO	2025-12-10 12:03:39.291249	2025-12-10 12:03:39.29128	2025-12-10 12:03:39.291283
111	21	273	26	32	0	20800	FIFO	2025-12-10 12:03:40.412523	2025-12-10 12:03:40.412557	2025-12-10 12:03:40.41256
112	21	274	26	20	0	24000	FIFO	2025-12-10 12:03:41.534208	2025-12-10 12:03:41.534241	2025-12-10 12:03:41.534244
113	21	275	26	18	0	21600	FIFO	2025-12-10 12:03:42.655378	2025-12-10 12:03:42.65541	2025-12-10 12:03:42.655413
114	21	276	26	15	0	18000	FIFO	2025-12-10 12:03:43.777638	2025-12-10 12:03:43.777674	2025-12-10 12:03:43.777677
115	21	277	26	25	0	16250	FIFO	2025-12-10 12:03:45.272324	2025-12-10 12:03:45.272357	2025-12-10 12:03:45.27236
116	21	278	26	40	0	26000	FIFO	2025-12-10 12:03:46.393023	2025-12-10 12:03:46.393054	2025-12-10 12:03:46.393058
117	21	279	26	35	0	22750	FIFO	2025-12-10 12:03:47.514977	2025-12-10 12:03:47.515012	2025-12-10 12:03:47.515015
118	21	280	26	20	0	28000	FIFO	2025-12-10 12:03:49.009393	2025-12-10 12:03:49.009424	2025-12-10 12:03:49.009428
119	21	281	26	18	0	25200	FIFO	2025-12-10 12:03:50.130734	2025-12-10 12:03:50.130765	2025-12-10 12:03:50.130768
120	21	282	26	22	0	29700	FIFO	2025-12-10 12:03:51.443996	2025-12-10 12:03:51.444031	2025-12-10 12:03:51.444034
121	21	283	26	35	0	47250	FIFO	2025-12-10 12:03:52.566141	2025-12-10 12:03:52.566174	2025-12-10 12:03:52.566177
122	21	284	26	28	0	37800	FIFO	2025-12-10 12:03:53.687636	2025-12-10 12:03:53.687667	2025-12-10 12:03:53.68767
123	21	285	26	25	0	33750	FIFO	2025-12-10 12:03:54.809591	2025-12-10 12:03:54.809625	2025-12-10 12:03:54.809628
124	21	286	26	20	0	34000	FIFO	2025-12-10 12:03:55.932028	2025-12-10 12:03:55.932062	2025-12-10 12:03:55.932066
125	21	287	26	30	0	51000	FIFO	2025-12-10 12:03:57.053654	2025-12-10 12:03:57.053685	2025-12-10 12:03:57.053688
126	21	288	26	18	0	30600	FIFO	2025-12-10 12:03:58.175475	2025-12-10 12:03:58.175506	2025-12-10 12:03:58.175509
127	21	289	26	30	0	10500	FIFO	2025-12-10 12:03:59.670499	2025-12-10 12:03:59.670532	2025-12-10 12:03:59.670535
128	21	290	26	60	0	21000	FIFO	2025-12-10 12:04:00.791617	2025-12-10 12:04:00.791647	2025-12-10 12:04:00.79165
129	21	291	26	45	0	15750	FIFO	2025-12-10 12:04:01.913006	2025-12-10 12:04:01.913037	2025-12-10 12:04:01.91304
130	21	292	26	40	0	14000	FIFO	2025-12-10 12:04:03.034769	2025-12-10 12:04:03.034801	2025-12-10 12:04:03.034804
131	21	293	26	20	0	7000	FIFO	2025-12-10 12:04:04.344476	2025-12-10 12:04:04.344507	2025-12-10 12:04:04.34451
132	21	294	26	30	0	10500	FIFO	2025-12-10 12:04:05.468597	2025-12-10 12:04:05.46863	2025-12-10 12:04:05.468633
133	21	295	26	28	0	9800	FIFO	2025-12-10 12:04:06.589881	2025-12-10 12:04:06.589912	2025-12-10 12:04:06.589915
134	21	296	26	25	0	8750	FIFO	2025-12-10 12:04:07.713398	2025-12-10 12:04:07.713432	2025-12-10 12:04:07.713435
135	21	297	26	22	0	14300	FIFO	2025-12-10 12:04:09.022227	2025-12-10 12:04:09.022262	2025-12-10 12:04:09.022265
136	21	298	26	20	0	13000	FIFO	2025-12-10 12:04:10.14476	2025-12-10 12:04:10.144794	2025-12-10 12:04:10.144797
137	21	299	26	25	0	8750	FIFO	2025-12-10 12:04:11.639509	2025-12-10 12:04:11.639543	2025-12-10 12:04:11.639546
138	21	300	26	12	0	14400	FIFO	2025-12-10 12:04:13.135058	2025-12-10 12:04:13.13509	2025-12-10 12:04:13.135093
139	21	301	26	15	0	18000	FIFO	2025-12-10 12:04:14.256434	2025-12-10 12:04:14.256467	2025-12-10 12:04:14.25647
140	21	302	26	10	0	5500	FIFO	2025-12-10 12:04:15.379195	2025-12-10 12:04:15.379228	2025-12-10 12:04:15.37923
141	21	303	26	12	0	6600	FIFO	2025-12-10 12:04:16.501884	2025-12-10 12:04:16.501918	2025-12-10 12:04:16.501921
142	21	304	26	20	0	9000	FIFO	2025-12-10 12:04:17.995661	2025-12-10 12:04:17.995694	2025-12-10 12:04:17.995697
143	21	305	26	25	0	11250	FIFO	2025-12-10 12:04:19.117142	2025-12-10 12:04:19.117174	2025-12-10 12:04:19.117177
144	21	306	26	18	0	8100	FIFO	2025-12-10 12:04:20.23864	2025-12-10 12:04:20.238669	2025-12-10 12:04:20.238673
145	21	307	26	30	0	21000	FIFO	2025-12-10 12:04:21.3595	2025-12-10 12:04:21.359535	2025-12-10 12:04:21.359538
146	21	308	26	28	0	19600	FIFO	2025-12-10 12:04:22.48158	2025-12-10 12:04:22.481636	2025-12-10 12:04:22.481639
147	21	309	26	25	0	17500	FIFO	2025-12-10 12:04:23.601982	2025-12-10 12:04:23.602018	2025-12-10 12:04:23.60202
\.


--
-- Data for Name: items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.items (id, tenant_id, name, sku, type, category_id, item_group_id, unit, dimensions_length, dimensions_width, dimensions_height, dimensions_unit, weight, weight_unit, manufacturer, brand, upc, ean, mpn, isbn, selling_price, sales_description, sales_account, tax_preference, cost_price, purchase_description, purchase_account, preferred_vendor, track_inventory, opening_stock, opening_stock_value, reorder_point, primary_image, is_active, is_returnable, created_by, created_at, updated_at, hsn_code, gst_rate, mrp, discount_percent, barcode) FROM stdin;
232	21	Levi's Men's Jeans - Blue - 30	LEVI-JNS-BLU-30	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2499	Levi's 511 slim fit jeans, authentic denim	Sales	GST 12%	1800	Levi's 511 slim fit jeans, authentic denim	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:02:52.530451	2025-12-10 12:02:52.530457	6109	12	2999.00	0.00	8901234001001
233	21	Levi's Men's Jeans - Blue - 32	LEVI-JNS-BLU-32	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2499	Levi's 511 slim fit jeans, authentic denim	Sales	GST 12%	1800	Levi's 511 slim fit jeans, authentic denim	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:02:53.689677	2025-12-10 12:02:53.689683	6109	12	2999.00	0.00	8901234001002
6	11	HBL Premium Ceiling Fan 52" White	HBL-CF-52-WHT	goods	15	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1850	HBL premium model 52 inch ceiling fan	Sales	GST 18%	1850	HBL premium model 52 inch ceiling fan	Cost of Goods Sold	\N	t	10	0	0	\N	t	t	\N	2025-11-02 11:06:07.596196	2025-11-02 11:06:07.596202	\N	18	\N	0.00	\N
7	11	Havells SS-390 Ceiling Fan 48" Pearl White	HAV-CF-48-PWH	goods	15	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1950	Havells SS-390 energy saving fan	Sales	GST 18%	1950	Havells SS-390 energy saving fan	Cost of Goods Sold	\N	t	8	0	0	\N	t	t	\N	2025-11-02 11:06:08.714041	2025-11-02 11:06:08.714047	\N	18	\N	0.00	\N
8	11	Havells Leganza Ceiling Fan 52" Brown	HAV-CF-52-BRN	goods	15	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2150	Havells Leganza premium decorative fan	Sales	GST 18%	2150	Havells Leganza premium decorative fan	Cost of Goods Sold	\N	t	6	0	0	\N	t	t	\N	2025-11-02 11:06:09.831774	2025-11-02 11:06:09.83178	\N	18	\N	0.00	\N
9	11	Bajaj Table Fan 400mm White	BAJ-TF-400-WHT	goods	16	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	850	Bajaj high speed table fan 400mm	Sales	GST 18%	850	Bajaj high speed table fan 400mm	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-11-02 11:06:11.135257	2025-11-02 11:06:11.135263	\N	18	\N	0.00	\N
10	11	Orient Table Fan 400mm Blue	ORI-TF-400-BLU	goods	16	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	950	Orient aeroslim table fan 400mm	Sales	GST 18%	950	Orient aeroslim table fan 400mm	Cost of Goods Sold	\N	t	15	0	0	\N	t	t	\N	2025-11-02 11:06:12.25481	2025-11-02 11:06:12.254816	\N	18	\N	0.00	\N
11	11	Bajaj Exhaust Fan 8" (200mm)	BAJ-EF-200	goods	17	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	650	Bajaj window exhaust fan 200mm	Sales	GST 18%	650	Bajaj window exhaust fan 200mm	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-11-02 11:06:13.558077	2025-11-02 11:06:13.558083	\N	18	\N	0.00	\N
12	11	Havells Exhaust Fan 12" (300mm)	HAV-EF-300	goods	17	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	950	Havells ventil air exhaust fan 300mm	Sales	GST 18%	950	Havells ventil air exhaust fan 300mm	Cost of Goods Sold	\N	t	18	0	0	\N	t	t	\N	2025-11-02 11:06:14.676069	2025-11-02 11:06:14.676096	\N	18	\N	0.00	\N
13	11	Anchor Penta 6A Switch White	ANC-SW-6A-WHT	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	85	Anchor Penta modular 6A switch white	Sales	GST 18%	85	Anchor Penta modular 6A switch white	Cost of Goods Sold	\N	t	100	0	0	\N	t	t	\N	2025-11-02 11:06:16.165383	2025-11-02 11:06:16.165389	\N	18	\N	0.00	\N
14	11	Anchor Penta 16A Socket White	ANC-SK-16A-WHT	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	125	Anchor Penta 16A 3-pin socket white	Sales	GST 18%	125	Anchor Penta 16A 3-pin socket white	Cost of Goods Sold	\N	t	80	0	0	\N	t	t	\N	2025-11-02 11:06:17.282754	2025-11-02 11:06:17.28276	\N	18	\N	0.00	\N
15	11	Anchor Penta 6A 2-Way Switch White	ANC-SW-6A-2W-WHT	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	95	Anchor Penta 6A 2-way switch white	Sales	GST 18%	95	Anchor Penta 6A 2-way switch white	Cost of Goods Sold	\N	t	75	0	0	\N	t	t	\N	2025-11-02 11:06:18.401022	2025-11-02 11:06:18.401028	\N	18	\N	0.00	\N
16	11	Vega Modular Switch 6A Ivory	VEG-SW-6A-IVR	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	95	Vega modular 6A switch ivory color	Sales	GST 18%	95	Vega modular 6A switch ivory color	Cost of Goods Sold	\N	t	60	0	0	\N	t	t	\N	2025-11-02 11:06:19.518285	2025-11-02 11:06:19.518291	\N	18	\N	0.00	\N
17	11	Vega 16A Socket with USB Charger	VEG-SK-16A-USB	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	285	Vega 16A socket with 2.1A USB charger	Sales	GST 18%	285	Vega 16A socket with 2.1A USB charger	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-11-02 11:06:20.634232	2025-11-02 11:06:20.634239	\N	18	\N	0.00	\N
18	11	REO 6A Switch White	REO-SW-6A-WHT	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	75	REO standard 6A switch white	Sales	GST 18%	75	REO standard 6A switch white	Cost of Goods Sold	\N	t	90	0	0	\N	t	t	\N	2025-11-02 11:06:21.753436	2025-11-02 11:06:21.753441	\N	18	\N	0.00	\N
19	11	REO 16A Socket White	REO-SK-16A-WHT	goods	18	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	115	REO 16A 3-pin socket white	Sales	GST 18%	115	REO 16A 3-pin socket white	Cost of Goods Sold	\N	t	70	0	0	\N	t	t	\N	2025-11-02 11:06:22.872376	2025-11-02 11:06:22.872382	\N	18	\N	0.00	\N
20	11	Anchor MCB 16A Single Pole	ANC-MCB-16A-SP	goods	19	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	150	Anchor miniature circuit breaker 16A SP	Sales	GST 18%	150	Anchor miniature circuit breaker 16A SP	Cost of Goods Sold	\N	t	50	0	0	\N	t	t	\N	2025-11-02 11:06:24.175867	2025-11-02 11:06:24.175873	\N	18	\N	0.00	\N
21	11	Anchor MCB 32A Single Pole	ANC-MCB-32A-SP	goods	19	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	180	Anchor miniature circuit breaker 32A SP	Sales	GST 18%	180	Anchor miniature circuit breaker 32A SP	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-11-02 11:06:25.293772	2025-11-02 11:06:25.293778	\N	18	\N	0.00	\N
22	11	Havells MCB 16A Double Pole	HAV-MCB-16A-DP	goods	19	14	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	285	Havells MCB 16A double pole C-curve	Sales	GST 18%	285	Havells MCB 16A double pole C-curve	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-11-02 11:06:26.410777	2025-11-02 11:06:26.410783	\N	18	\N	0.00	\N
23	11	PVC Conduit Pipe 20mm (3 meter)	PVC-P-20-3M	goods	20	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	45	PVC electrical conduit pipe 20mm 3m length	Sales	GST 18%	45	PVC electrical conduit pipe 20mm 3m length	Cost of Goods Sold	\N	t	200	0	0	\N	t	t	\N	2025-11-02 11:06:27.901176	2025-11-02 11:06:27.901181	\N	18	\N	0.00	\N
24	11	PVC Conduit Pipe 25mm (3 meter)	PVC-P-25-3M	goods	20	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	65	PVC electrical conduit pipe 25mm 3m length	Sales	GST 18%	65	PVC electrical conduit pipe 25mm 3m length	Cost of Goods Sold	\N	t	150	0	0	\N	t	t	\N	2025-11-02 11:06:29.01883	2025-11-02 11:06:29.018836	\N	18	\N	0.00	\N
25	11	PVC Conduit Pipe 32mm (3 meter)	PVC-P-32-3M	goods	20	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	95	PVC electrical conduit pipe 32mm 3m length	Sales	GST 18%	95	PVC electrical conduit pipe 32mm 3m length	Cost of Goods Sold	\N	t	100	0	0	\N	t	t	\N	2025-11-02 11:06:30.136852	2025-11-02 11:06:30.136857	\N	18	\N	0.00	\N
26	11	Flexible Conduit Pipe 20mm	FLX-P-20	goods	20	15	Meter	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	25	Flexible PVC conduit pipe 20mm per meter	Sales	GST 18%	25	Flexible PVC conduit pipe 20mm per meter	Cost of Goods Sold	\N	t	50	0	0	\N	t	t	\N	2025-11-02 11:06:31.254337	2025-11-02 11:06:31.254343	\N	18	\N	0.00	\N
27	11	PVC Elbow 20mm 90 Degree	PVC-ELB-20-90	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	8	PVC elbow 20mm 90 degree bend	Sales	GST 18%	8	PVC elbow 20mm 90 degree bend	Cost of Goods Sold	\N	t	500	0	0	\N	t	t	\N	2025-11-02 11:06:32.558073	2025-11-02 11:06:32.558079	\N	18	\N	0.00	\N
28	11	PVC Elbow 25mm 90 Degree	PVC-ELB-25-90	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	12	PVC elbow 25mm 90 degree bend	Sales	GST 18%	12	PVC elbow 25mm 90 degree bend	Cost of Goods Sold	\N	t	400	0	0	\N	t	t	\N	2025-11-02 11:06:33.675592	2025-11-02 11:06:33.675597	\N	18	\N	0.00	\N
29	11	PVC Bend 20mm 45 Degree	PVC-BND-20-45	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	10	PVC bend 20mm 45 degree	Sales	GST 18%	10	PVC bend 20mm 45 degree	Cost of Goods Sold	\N	t	300	0	0	\N	t	t	\N	2025-11-02 11:06:34.792799	2025-11-02 11:06:34.792805	\N	18	\N	0.00	\N
30	11	PVC T-Joint 20mm	PVC-T-20	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	15	PVC T-junction 20mm 3-way	Sales	GST 18%	15	PVC T-junction 20mm 3-way	Cost of Goods Sold	\N	t	250	0	0	\N	t	t	\N	2025-11-02 11:06:35.911002	2025-11-02 11:06:35.911008	\N	18	\N	0.00	\N
31	11	PVC T-Joint 25mm	PVC-T-25	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	22	PVC T-junction 25mm 3-way	Sales	GST 18%	22	PVC T-junction 25mm 3-way	Cost of Goods Sold	\N	t	200	0	0	\N	t	t	\N	2025-11-02 11:06:37.028955	2025-11-02 11:06:37.02896	\N	18	\N	0.00	\N
32	11	PVC Coupler 20mm	PVC-CPL-20	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	6	PVC pipe coupler 20mm straight connector	Sales	GST 18%	6	PVC pipe coupler 20mm straight connector	Cost of Goods Sold	\N	t	350	0	0	\N	t	t	\N	2025-11-02 11:06:38.152946	2025-11-02 11:06:38.152956	\N	18	\N	0.00	\N
33	11	PVC Coupler 25mm	PVC-CPL-25	goods	21	15	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	9	PVC pipe coupler 25mm straight connector	Sales	GST 18%	9	PVC pipe coupler 25mm straight connector	Cost of Goods Sold	\N	t	280	0	0	\N	t	t	\N	2025-11-02 11:06:39.269563	2025-11-02 11:06:39.269568	\N	18	\N	0.00	\N
34	11	Saddle Clamp 20mm (Pack of 10)	SDL-CLP-20-P10	goods	22	15	Pack	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	35	Plastic saddle clamp 20mm pack of 10	Sales	GST 18%	35	Plastic saddle clamp 20mm pack of 10	Cost of Goods Sold	\N	t	100	0	0	\N	t	t	\N	2025-11-02 11:06:40.572681	2025-11-02 11:06:40.572687	\N	18	\N	0.00	\N
35	11	Saddle Clamp 25mm (Pack of 10)	SDL-CLP-25-P10	goods	22	15	Pack	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	45	Plastic saddle clamp 25mm pack of 10	Sales	GST 18%	45	Plastic saddle clamp 25mm pack of 10	Cost of Goods Sold	\N	t	80	0	0	\N	t	t	\N	2025-11-02 11:06:41.689147	2025-11-02 11:06:41.689153	\N	18	\N	0.00	\N
36	11	Metal Band 20mm (Pack of 10)	MTL-BND-20-P10	goods	22	15	Pack	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	25	Metal pipe clamp band 20mm pack of 10	Sales	GST 18%	25	Metal pipe clamp band 20mm pack of 10	Cost of Goods Sold	\N	t	120	0	0	\N	t	t	\N	2025-11-02 11:06:42.806445	2025-11-02 11:06:42.80645	\N	18	\N	0.00	\N
37	11	Metal Band 25mm (Pack of 10)	MTL-BND-25-P10	goods	22	15	Pack	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	32	Metal pipe clamp band 25mm pack of 10	Sales	GST 18%	32	Metal pipe clamp band 25mm pack of 10	Cost of Goods Sold	\N	t	100	0	0	\N	t	t	\N	2025-11-02 11:06:43.925561	2025-11-02 11:06:43.925566	\N	18	\N	0.00	\N
38	11	Pipe Clip 20mm (Pack of 10)	PIP-CLP-20-P10	goods	22	15	Pack	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	18	Plastic pipe clip 20mm pack of 10	Sales	GST 18%	18	Plastic pipe clip 20mm pack of 10	Cost of Goods Sold	\N	t	90	0	0	\N	t	t	\N	2025-11-02 11:06:45.042424	2025-11-02 11:06:45.04243	\N	18	\N	0.00	\N
39	11	Bajaj LED Bulb 9W Cool White B22	BAJ-LED-9W-CW	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	120	Bajaj 9W LED bulb cool white B22 base	Sales	GST 12%	120	Bajaj 9W LED bulb cool white B22 base	Cost of Goods Sold	\N	t	150	0	0	\N	t	t	\N	2025-11-02 11:06:46.531558	2025-11-02 11:06:46.531564	\N	18	\N	0.00	\N
40	11	Bajaj LED Bulb 12W Warm White B22	BAJ-LED-12W-WW	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	165	Bajaj 12W LED bulb warm white B22 base	Sales	GST 12%	165	Bajaj 12W LED bulb warm white B22 base	Cost of Goods Sold	\N	t	120	0	0	\N	t	t	\N	2025-11-02 11:06:47.648195	2025-11-02 11:06:47.648201	\N	18	\N	0.00	\N
41	11	Bajaj LED Bulb 15W Cool White B22	BAJ-LED-15W-CW	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	210	Bajaj 15W LED bulb cool white B22 base	Sales	GST 12%	210	Bajaj 15W LED bulb cool white B22 base	Cost of Goods Sold	\N	t	100	0	0	\N	t	t	\N	2025-11-02 11:06:48.764921	2025-11-02 11:06:48.764927	\N	18	\N	0.00	\N
42	11	Orient LED Bulb 7W Cool Day B22	ORI-LED-7W-CD	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	110	Orient 7W LED bulb cool daylight B22 base	Sales	GST 12%	110	Orient 7W LED bulb cool daylight B22 base	Cost of Goods Sold	\N	t	140	0	0	\N	t	t	\N	2025-11-02 11:06:49.881855	2025-11-02 11:06:49.881861	\N	18	\N	0.00	\N
43	11	Orient LED Bulb 9W Warm White B22	ORI-LED-9W-WW	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	145	Orient 9W LED bulb warm white B22 base	Sales	GST 12%	145	Orient 9W LED bulb warm white B22 base	Cost of Goods Sold	\N	t	130	0	0	\N	t	t	\N	2025-11-02 11:06:50.999766	2025-11-02 11:06:50.999772	\N	18	\N	0.00	\N
44	11	Orient LED Bulb 12W Cool Day B22	ORI-LED-12W-CD	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	185	Orient 12W LED bulb cool daylight B22 base	Sales	GST 12%	185	Orient 12W LED bulb cool daylight B22 base	Cost of Goods Sold	\N	t	110	0	0	\N	t	t	\N	2025-11-02 11:06:52.118846	2025-11-02 11:06:52.118852	\N	18	\N	0.00	\N
45	11	Havells LED Bulb 9W Cool White B22	HAV-LED-9W-CW	goods	23	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	135	Havells 9W LED bulb cool white B22 base	Sales	GST 12%	135	Havells 9W LED bulb cool white B22 base	Cost of Goods Sold	\N	t	90	0	0	\N	t	t	\N	2025-11-02 11:06:53.236311	2025-11-02 11:06:53.236317	\N	18	\N	0.00	\N
46	11	Bajaj LED Batten 20W (2 feet)	BAJ-BTN-20W-2F	goods	24	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	450	Bajaj 20W LED batten 2 feet cool white	Sales	GST 12%	450	Bajaj 20W LED batten 2 feet cool white	Cost of Goods Sold	\N	t	60	0	0	\N	t	t	\N	2025-11-02 11:06:54.538748	2025-11-02 11:06:54.538754	\N	18	\N	0.00	\N
47	11	Bajaj LED Batten 40W (4 feet)	BAJ-BTN-40W-4F	goods	24	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	750	Bajaj 40W LED batten 4 feet cool white	Sales	GST 12%	750	Bajaj 40W LED batten 4 feet cool white	Cost of Goods Sold	\N	t	50	0	0	\N	t	t	\N	2025-11-02 11:06:55.655237	2025-11-02 11:06:55.655242	\N	18	\N	0.00	\N
48	11	Orient LED Batten 20W (2 feet)	ORI-BTN-20W-2F	goods	24	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	480	Orient 20W LED batten 2 feet cool day	Sales	GST 12%	480	Orient 20W LED batten 2 feet cool day	Cost of Goods Sold	\N	t	55	0	0	\N	t	t	\N	2025-11-02 11:06:56.772587	2025-11-02 11:06:56.772593	\N	18	\N	0.00	\N
49	11	Orient LED Batten 40W (4 feet)	ORI-BTN-40W-4F	goods	24	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	780	Orient 40W LED batten 4 feet cool day	Sales	GST 12%	780	Orient 40W LED batten 4 feet cool day	Cost of Goods Sold	\N	t	45	0	0	\N	t	t	\N	2025-11-02 11:06:57.890339	2025-11-02 11:06:57.890345	\N	18	\N	0.00	\N
50	11	Bajaj LED Downlight 7W Round White	BAJ-DWN-7W-RD	goods	25	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	285	Bajaj 7W LED recessed downlight round	Sales	GST 12%	285	Bajaj 7W LED recessed downlight round	Cost of Goods Sold	\N	t	70	0	0	\N	t	t	\N	2025-11-02 11:06:59.193712	2025-11-02 11:06:59.193718	\N	18	\N	0.00	\N
51	11	Orient LED Downlight 12W Square White	ORI-DWN-12W-SQ	goods	25	16	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	385	Orient 12W LED recessed downlight square	Sales	GST 12%	385	Orient 12W LED recessed downlight square	Cost of Goods Sold	\N	t	50	0	0	\N	t	t	\N	2025-11-02 11:07:00.311	2025-11-02 11:07:00.311006	\N	18	\N	0.00	\N
52	12	test	ITEM-0001	service	\N	\N	nos	0	0	0	cm	0	kg						\N	12	sas	Sales	\N	11		Cost of Goods Sold		t	0	0	0	\N	t	t	Admin	2025-11-03 18:21:28.641687	2025-11-03 18:21:28.641694	\N	18	\N	0.00	\N
5	11	Bajaj Ceiling Fan 48" (1200mm) Brown	BAJ-CF-48-BRN	goods	15	13	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1450	Bajaj standard ceiling fan 48 inch brown color	Sales	GST 18%	1472.5	Bajaj standard ceiling fan 48 inch brown color	Cost of Goods Sold	\N	t	12	0	0	\N	t	t	\N	2025-11-02 11:06:06.478503	2025-11-07 18:47:07.286431	\N	18	\N	0.00	\N
4	11	Bajaj Ceiling Fan 48" (1200mm) White	BAJ-CF-48-WHT	goods	15	13	nos	0	0	0	cm	0	kg	\N	\N	\N	\N	\N	\N	1550	\N	Sales	GST 18%	1462.5	\N	Cost of Goods Sold	\N	t	15	0	0	\N	t	t	\N	2025-11-02 11:06:05.306746	2025-11-07 18:49:32.331876	\N	18	\N	0.00	\N
53	11	Bajaj Edge Fan 48" (1200mm) Brown	BAJ-Edg-48-BRN	goods	15	13	nos	0	0	0	cm	0	kg	\N	\N	\N	\N	\N	\N	1411	\N	Sales	\N	1411	\N	Cost of Goods Sold	\N	t	8	11288	7	\N	t	t	Admin	2025-11-08 09:54:39.909525	2025-11-09 12:34:18.601414	8414	18	\N	0.00	\N
234	21	Levi's Men's Jeans - Blue - 34	LEVI-JNS-BLU-34	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2499	Levi's 511 slim fit jeans, authentic denim	Sales	GST 12%	1800	Levi's 511 slim fit jeans, authentic denim	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:02:54.80962	2025-12-10 12:02:54.809625	6109	12	2999.00	0.00	8901234001003
235	21	Levi's Men's Jeans - Black - 30	LEVI-JNS-BLK-30	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2499	Levi's 511 slim fit jeans, black denim	Sales	GST 12%	1800	Levi's 511 slim fit jeans, black denim	Cost of Goods Sold	\N	t	18	0	0	\N	t	t	\N	2025-12-10 12:02:55.931976	2025-12-10 12:02:55.931981	6109	12	2999.00	0.00	8901234001004
236	21	Levi's Men's Jeans - Black - 32	LEVI-JNS-BLK-32	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2499	Levi's 511 slim fit jeans, black denim	Sales	GST 12%	1800	Levi's 511 slim fit jeans, black denim	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:02:57.053407	2025-12-10 12:02:57.053413	6109	12	2999.00	0.00	8901234001005
58	11	Paneer	ITEM-0004	goods	\N	\N	kg	0	0	0	cm	0	kg						\N	400		Sales	\N	350		Cost of Goods Sold	self	t	5	1750	2	\N	t	f	Admin	2025-11-23 12:30:36.788354	2025-11-23 12:30:36.78836		0	\N	0.00	\N
59	11	Ghee	ITEM-0005	goods	\N	\N	ltr	0	0	0	cm	0	kg						\N	1000		Sales	\N	900		Cost of Goods Sold	self	t	10	9000	2	\N	t	t	Admin	2025-11-23 14:02:59.797813	2025-11-23 14:02:59.797818		0	\N	0.00	\N
60	16	Paneer	ITEM-0001	goods	38	17	kg	0	0	0	cm	0	kg						\N	480		Sales	\N	480		Cost of Goods Sold		t	3.5	1680	0	\N	t	t	Admin	2025-12-02 08:59:16.863653	2025-12-02 08:59:16.863658		0	\N	0.00	\N
61	16	Ghee	ITEM-0002	goods	38	17	ltr	0	0	0	cm	0	kg						\N	1000		Sales	\N	1000		Cost of Goods Sold		t	10	10000	0	\N	t	t	Admin	2025-12-02 09:01:33.145003	2025-12-02 09:01:33.145008		0	\N	0.00	\N
62	16	Cow Milk- Half litre	ITEM-0003	goods	38	17	ltr	0	0	0	cm	0	kg						\N	35		Sales	\N	20		Cost of Goods Sold		t	1000	20000	100	\N	t	f	Admin	2025-12-02 09:21:55.930126	2025-12-02 09:21:55.930132		0	\N	0.00	\N
63	16	Cow Milk - 1 Litre	ITEM-0004	goods	38	17	ltr	0	0	0	cm	0	kg						\N	70		Sales	\N	40		Cost of Goods Sold		t	1000	40000	100	\N	t	t	Admin	2025-12-02 09:24:46.365813	2025-12-02 09:24:46.365819		0	\N	0.00	\N
237	21	Wrangler Men's Jeans - Blue - 30	WRAN-JNS-BLU-30	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Wrangler regular fit jeans, comfortable	Sales	GST 12%	1400	Wrangler regular fit jeans, comfortable	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:02:58.179865	2025-12-10 12:02:58.179871	6109	12	2299.00	0.00	8901234002001
64	16	Buffalo - Half Liter	ITEM-0005	goods	38	17	ltr	0	0	0	cm	0	kg	\N	\N	\N	\N	\N	\N	40	\N	Sales	\N	30	\N	Cost of Goods Sold	\N	t	1000	30000	100	\N	t	t	Admin	2025-12-02 09:29:30.191122	2025-12-02 09:30:18.019247		0	\N	0.00	\N
65	16	Buffalo - 1 Litre	ITEM-0006	goods	38	17	ltr	0	0	0	cm	0	kg						\N	80		Sales	\N	60		Cost of Goods Sold		t	1000	60000	100	\N	t	t	Admin	2025-12-02 09:31:14.674354	2025-12-02 09:31:14.674363		0	\N	0.00	\N
57	11	Anchor wire 1.5 Sq mm	ITEM-0003	goods	20	15	box	0	0	0	cm	0	kg	\N	\N	\N	\N	\N	\N	1800	\N	Sales	\N	1700	\N	Cost of Goods Sold	\N	t	100	180000	20	\N	t	t	Admin	2025-11-17 05:47:12.129485	2025-12-08 08:21:59.808136		18	2000.00	10.00	\N
56	11	Anchor wire 1 Sq mm	ITEM-0002	goods	20	14	box	0	0	0	cm	0	kg	\N	\N	\N	\N	\N	\N	1350	\N	Sales	\N	1100	\N	Cost of Goods Sold	\N	t	100	110000	20	\N	t	t	Admin	2025-11-17 04:59:36.807916	2025-12-08 08:22:21.902653		18	1500.00	10.00	\N
238	21	Wrangler Men's Jeans - Blue - 32	WRAN-JNS-BLU-32	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Wrangler regular fit jeans, comfortable	Sales	GST 12%	1400	Wrangler regular fit jeans, comfortable	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-12-10 12:02:59.302746	2025-12-10 12:02:59.302752	6109	12	2299.00	0.00	8901234002002
239	21	Wrangler Men's Jeans - Blue - 34	WRAN-JNS-BLU-34	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Wrangler regular fit jeans, comfortable	Sales	GST 12%	1400	Wrangler regular fit jeans, comfortable	Cost of Goods Sold	\N	t	32	0	0	\N	t	t	\N	2025-12-10 12:03:00.425278	2025-12-10 12:03:00.425284	6109	12	2299.00	0.00	8901234002003
240	21	Wrangler Men's Jeans - Black - 32	WRAN-JNS-BLK-32	goods	73	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Wrangler regular fit jeans, black	Sales	GST 12%	1400	Wrangler regular fit jeans, black	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:01.545707	2025-12-10 12:03:01.545714	6109	12	2299.00	0.00	8901234002004
241	21	Allen Solly Men's Shirt - White - 38	AS-SH-WHT-38	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1499	Allen Solly formal shirt, slim fit	Sales	GST 12%	1050	Allen Solly formal shirt, slim fit	Cost of Goods Sold	\N	t	22	0	0	\N	t	t	\N	2025-12-10 12:03:03.040946	2025-12-10 12:03:03.040952	6109	12	1799.00	0.00	8901234003001
242	21	Allen Solly Men's Shirt - White - 40	AS-SH-WHT-40	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1499	Allen Solly formal shirt, slim fit	Sales	GST 12%	1050	Allen Solly formal shirt, slim fit	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:04.16152	2025-12-10 12:03:04.161526	6109	12	1799.00	0.00	8901234003002
243	21	Allen Solly Men's Shirt - White - 42	AS-SH-WHT-42	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1499	Allen Solly formal shirt, slim fit	Sales	GST 12%	1050	Allen Solly formal shirt, slim fit	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:03:05.282051	2025-12-10 12:03:05.282057	6109	12	1799.00	0.00	8901234003003
244	21	Allen Solly Men's Shirt - Blue - 38	AS-SH-BLU-38	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1499	Allen Solly formal shirt, blue, slim fit	Sales	GST 12%	1050	Allen Solly formal shirt, blue, slim fit	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:03:06.402242	2025-12-10 12:03:06.402247	6109	12	1799.00	0.00	8901234003004
245	21	Allen Solly Men's Shirt - Blue - 40	AS-SH-BLU-40	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1499	Allen Solly formal shirt, blue, slim fit	Sales	GST 12%	1050	Allen Solly formal shirt, blue, slim fit	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:07.524369	2025-12-10 12:03:07.524376	6109	12	1799.00	0.00	8901234003005
246	21	Allen Solly Men's Shirt - Pink - 40	AS-SH-PNK-40	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1499	Allen Solly formal shirt, pink, slim fit	Sales	GST 12%	1050	Allen Solly formal shirt, pink, slim fit	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:03:08.64463	2025-12-10 12:03:08.644636	6109	12	1799.00	0.00	8901234003006
247	21	Peter England Men's Shirt - White - 38	PE-SH-WHT-38	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Peter England formal shirt, regular fit	Sales	GST 12%	750	Peter England formal shirt, regular fit	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:03:09.766072	2025-12-10 12:03:09.766077	6109	12	1199.00	0.00	8901234004001
248	21	Peter England Men's Shirt - White - 40	PE-SH-WHT-40	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Peter England formal shirt, regular fit	Sales	GST 12%	750	Peter England formal shirt, regular fit	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-12-10 12:03:10.887453	2025-12-10 12:03:10.887459	6109	12	1199.00	0.00	8901234004002
249	21	Peter England Men's Shirt - Blue - 40	PE-SH-BLU-40	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Peter England formal shirt, blue	Sales	GST 12%	750	Peter England formal shirt, blue	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:12.008913	2025-12-10 12:03:12.00892	6109	12	1199.00	0.00	8901234004003
250	21	Peter England Men's Shirt - Blue - 42	PE-SH-BLU-42	goods	74	47	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Peter England formal shirt, blue	Sales	GST 12%	750	Peter England formal shirt, blue	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:13.12939	2025-12-10 12:03:13.129397	6109	12	1199.00	0.00	8901234004004
251	21	Van Heusen Men's Trousers - Black - 32	VH-TRS-BLK-32	goods	75	48	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Van Heusen formal trousers, flat front	Sales	GST 12%	1350	Van Heusen formal trousers, flat front	Cost of Goods Sold	\N	t	22	0	0	\N	t	t	\N	2025-12-10 12:03:14.62494	2025-12-10 12:03:14.624946	6109	12	2299.00	0.00	8901234005001
252	21	Van Heusen Men's Trousers - Black - 34	VH-TRS-BLK-34	goods	75	48	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Van Heusen formal trousers, flat front	Sales	GST 12%	1350	Van Heusen formal trousers, flat front	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:15.745069	2025-12-10 12:03:15.745075	6109	12	2299.00	0.00	8901234005002
253	21	Van Heusen Men's Trousers - Black - 36	VH-TRS-BLK-36	goods	75	48	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Van Heusen formal trousers, flat front	Sales	GST 12%	1350	Van Heusen formal trousers, flat front	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:03:16.867685	2025-12-10 12:03:16.86769	6109	12	2299.00	0.00	8901234005003
254	21	Van Heusen Men's Trousers - Grey - 32	VH-TRS-GRY-32	goods	75	48	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1899	Van Heusen formal trousers, grey	Sales	GST 12%	1350	Van Heusen formal trousers, grey	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:03:17.988838	2025-12-10 12:03:17.988844	6109	12	2299.00	0.00	8901234005004
255	21	Nike Men's T-Shirt - White - M	NIKE-TSH-WHT-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Nike Dri-FIT t-shirt, breathable fabric	Sales	GST 12%	650	Nike Dri-FIT t-shirt, breathable fabric	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-12-10 12:03:19.482904	2025-12-10 12:03:19.48291	6109	12	1099.00	0.00	8901234006001
256	21	Nike Men's T-Shirt - White - L	NIKE-TSH-WHT-L	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Nike Dri-FIT t-shirt, breathable fabric	Sales	GST 12%	650	Nike Dri-FIT t-shirt, breathable fabric	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:20.606717	2025-12-10 12:03:20.606724	6109	12	1099.00	0.00	8901234006002
257	21	Nike Men's T-Shirt - Black - M	NIKE-TSH-BLK-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Nike Dri-FIT t-shirt, black	Sales	GST 12%	650	Nike Dri-FIT t-shirt, black	Cost of Goods Sold	\N	t	38	0	0	\N	t	t	\N	2025-12-10 12:03:21.727969	2025-12-10 12:03:21.727975	6109	12	1099.00	0.00	8901234006003
258	21	Nike Men's T-Shirt - Black - L	NIKE-TSH-BLK-L	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Nike Dri-FIT t-shirt, black	Sales	GST 12%	650	Nike Dri-FIT t-shirt, black	Cost of Goods Sold	\N	t	32	0	0	\N	t	t	\N	2025-12-10 12:03:22.849363	2025-12-10 12:03:22.849369	6109	12	1099.00	0.00	8901234006004
259	21	Nike Men's T-Shirt - Grey - M	NIKE-TSH-GRY-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Nike Dri-FIT t-shirt, grey heather	Sales	GST 12%	650	Nike Dri-FIT t-shirt, grey heather	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:23.970783	2025-12-10 12:03:23.970788	6109	12	1099.00	0.00	8901234006005
260	21	Puma Men's T-Shirt - White - M	PUMA-TSH-WHT-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	799	Puma essential t-shirt, cotton blend	Sales	GST 12%	550	Puma essential t-shirt, cotton blend	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:25.09237	2025-12-10 12:03:25.092376	6109	12	999.00	0.00	8901234007001
261	21	Puma Men's T-Shirt - White - L	PUMA-TSH-WHT-L	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	799	Puma essential t-shirt, cotton blend	Sales	GST 12%	550	Puma essential t-shirt, cotton blend	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:26.213571	2025-12-10 12:03:26.213577	6109	12	999.00	0.00	8901234007002
262	21	Puma Men's T-Shirt - Black - M	PUMA-TSH-BLK-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	799	Puma essential t-shirt, black	Sales	GST 12%	550	Puma essential t-shirt, black	Cost of Goods Sold	\N	t	32	0	0	\N	t	t	\N	2025-12-10 12:03:27.337297	2025-12-10 12:03:27.337302	6109	12	999.00	0.00	8901234007003
263	21	Puma Men's T-Shirt - Navy - M	PUMA-TSH-NVY-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	799	Puma essential t-shirt, navy	Sales	GST 12%	550	Puma essential t-shirt, navy	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:03:28.458745	2025-12-10 12:03:28.458751	6109	12	999.00	0.00	8901234007004
264	21	Biba Women's Kurta - Pink - S	BIBA-KRT-PNK-S	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1299	Biba printed kurta, cotton blend	Sales	GST 12%	950	Biba printed kurta, cotton blend	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:03:29.952772	2025-12-10 12:03:29.952778	6109	12	1599.00	0.00	8901234008001
265	21	Biba Women's Kurta - Pink - M	BIBA-KRT-PNK-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1299	Biba printed kurta, cotton blend	Sales	GST 12%	950	Biba printed kurta, cotton blend	Cost of Goods Sold	\N	t	45	0	0	\N	t	t	\N	2025-12-10 12:03:31.073387	2025-12-10 12:03:31.073393	6109	12	1599.00	0.00	8901234008002
266	21	Biba Women's Kurta - Pink - L	BIBA-KRT-PNK-L	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1299	Biba printed kurta, cotton blend	Sales	GST 12%	950	Biba printed kurta, cotton blend	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:32.193924	2025-12-10 12:03:32.19393	6109	12	1599.00	0.00	8901234008003
267	21	Biba Women's Kurta - Blue - M	BIBA-KRT-BLU-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1299	Biba printed kurta, blue, cotton blend	Sales	GST 12%	950	Biba printed kurta, blue, cotton blend	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-12-10 12:03:33.314742	2025-12-10 12:03:33.314748	6109	12	1599.00	0.00	8901234008004
268	21	Biba Women's Kurta - Blue - L	BIBA-KRT-BLU-L	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1299	Biba printed kurta, blue, cotton blend	Sales	GST 12%	950	Biba printed kurta, blue, cotton blend	Cost of Goods Sold	\N	t	32	0	0	\N	t	t	\N	2025-12-10 12:03:34.435076	2025-12-10 12:03:34.435082	6109	12	1599.00	0.00	8901234008005
269	21	Biba Women's Kurta - Green - M	BIBA-KRT-GRN-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1299	Biba printed kurta, green, cotton blend	Sales	GST 12%	950	Biba printed kurta, green, cotton blend	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:35.555511	2025-12-10 12:03:35.555516	6109	12	1599.00	0.00	8901234008006
270	21	W Women's Kurta - Blue - M	W-KRT-BLU-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	W by Westside kurta, casual wear	Sales	GST 12%	650	W by Westside kurta, casual wear	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:36.675362	2025-12-10 12:03:36.675368	6109	12	1099.00	0.00	8901234009001
271	21	W Women's Kurta - Blue - L	W-KRT-BLU-L	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	W by Westside kurta, casual wear	Sales	GST 12%	650	W by Westside kurta, casual wear	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:37.795596	2025-12-10 12:03:37.795602	6109	12	1099.00	0.00	8901234009002
272	21	W Women's Kurta - Pink - M	W-KRT-PNK-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	W by Westside kurta, pink, casual wear	Sales	GST 12%	650	W by Westside kurta, pink, casual wear	Cost of Goods Sold	\N	t	38	0	0	\N	t	t	\N	2025-12-10 12:03:38.916467	2025-12-10 12:03:38.916473	6109	12	1099.00	0.00	8901234009003
273	21	W Women's Kurta - White - M	W-KRT-WHT-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	W by Westside kurta, white, casual wear	Sales	GST 12%	650	W by Westside kurta, white, casual wear	Cost of Goods Sold	\N	t	32	0	0	\N	t	t	\N	2025-12-10 12:03:40.038561	2025-12-10 12:03:40.038568	6109	12	1099.00	0.00	8901234009004
274	21	FabIndia Women's Kurta - Beige - M	FBI-KRT-BGE-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1699	FabIndia handloom kurta, pure cotton	Sales	GST 12%	1200	FabIndia handloom kurta, pure cotton	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:03:41.159721	2025-12-10 12:03:41.159727	6109	12	2099.00	0.00	8901234010001
275	21	FabIndia Women's Kurta - Beige - L	FBI-KRT-BGE-L	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1699	FabIndia handloom kurta, pure cotton	Sales	GST 12%	1200	FabIndia handloom kurta, pure cotton	Cost of Goods Sold	\N	t	18	0	0	\N	t	t	\N	2025-12-10 12:03:42.281609	2025-12-10 12:03:42.281616	6109	12	2099.00	0.00	8901234010002
276	21	FabIndia Women's Kurta - Maroon - M	FBI-KRT-MAR-M	goods	77	50	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1699	FabIndia handloom kurta, maroon	Sales	GST 12%	1200	FabIndia handloom kurta, maroon	Cost of Goods Sold	\N	t	15	0	0	\N	t	t	\N	2025-12-10 12:03:43.402393	2025-12-10 12:03:43.402399	6109	12	2099.00	0.00	8901234010003
277	21	Zara Women's Top - White - S	ZARA-TOP-WHT-S	goods	78	51	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Zara casual top, trendy design	Sales	GST 12%	650	Zara casual top, trendy design	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:03:44.897913	2025-12-10 12:03:44.897919	6109	12	1299.00	0.00	8901234011001
278	21	Zara Women's Top - White - M	ZARA-TOP-WHT-M	goods	78	51	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Zara casual top, trendy design	Sales	GST 12%	650	Zara casual top, trendy design	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-12-10 12:03:46.019298	2025-12-10 12:03:46.019304	6109	12	1299.00	0.00	8901234011002
279	21	Zara Women's Top - Black - M	ZARA-TOP-BLK-M	goods	78	51	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Zara casual top, black	Sales	GST 12%	650	Zara casual top, black	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:47.140549	2025-12-10 12:03:47.140556	6109	12	1299.00	0.00	8901234011003
280	21	Zara Women's Dress - Floral - M	ZARA-DRS-FLR-M	goods	79	52	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1999	Zara floral dress, summer collection	Sales	GST 12%	1400	Zara floral dress, summer collection	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:03:48.635702	2025-12-10 12:03:48.635707	6109	12	2499.00	0.00	8901234011004
281	21	Zara Women's Dress - Floral - L	ZARA-DRS-FLR-L	goods	79	52	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1999	Zara floral dress, summer collection	Sales	GST 12%	1400	Zara floral dress, summer collection	Cost of Goods Sold	\N	t	18	0	0	\N	t	t	\N	2025-12-10 12:03:49.756704	2025-12-10 12:03:49.75671	6109	12	2499.00	0.00	8901234011005
282	21	Only Women's Jeans - Blue - 28	ONLY-JNS-BLU-28	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1799	Only skinny jeans, stretch denim	Sales	GST 12%	1350	Only skinny jeans, stretch denim	Cost of Goods Sold	\N	t	22	0	0	\N	t	t	\N	2025-12-10 12:03:51.069892	2025-12-10 12:03:51.069897	6109	12	2199.00	0.00	8901234012001
283	21	Only Women's Jeans - Blue - 30	ONLY-JNS-BLU-30	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1799	Only skinny jeans, stretch denim	Sales	GST 12%	1350	Only skinny jeans, stretch denim	Cost of Goods Sold	\N	t	35	0	0	\N	t	t	\N	2025-12-10 12:03:52.19244	2025-12-10 12:03:52.192445	6109	12	2199.00	0.00	8901234012002
284	21	Only Women's Jeans - Blue - 32	ONLY-JNS-BLU-32	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1799	Only skinny jeans, stretch denim	Sales	GST 12%	1350	Only skinny jeans, stretch denim	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:03:53.312912	2025-12-10 12:03:53.312918	6109	12	2199.00	0.00	8901234012003
285	21	Only Women's Jeans - Black - 30	ONLY-JNS-BLK-30	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1799	Only skinny jeans, black	Sales	GST 12%	1350	Only skinny jeans, black	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:03:54.435138	2025-12-10 12:03:54.435144	6109	12	2199.00	0.00	8901234012004
286	21	Levi's Women's Jeans - Blue - 28	LEVI-JNS-BLU-W28	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2299	Levi's 721 high rise skinny jeans	Sales	GST 12%	1700	Levi's 721 high rise skinny jeans	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:03:55.558189	2025-12-10 12:03:55.558195	6109	12	2799.00	0.00	8901234013001
287	21	Levi's Women's Jeans - Blue - 30	LEVI-JNS-BLU-W30	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2299	Levi's 721 high rise skinny jeans	Sales	GST 12%	1700	Levi's 721 high rise skinny jeans	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:56.679738	2025-12-10 12:03:56.679744	6109	12	2799.00	0.00	8901234013002
288	21	Levi's Women's Jeans - Black - 28	LEVI-JNS-BLK-W28	goods	80	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	2299	Levi's 721 high rise skinny, black	Sales	GST 12%	1700	Levi's 721 high rise skinny, black	Cost of Goods Sold	\N	t	18	0	0	\N	t	t	\N	2025-12-10 12:03:57.801213	2025-12-10 12:03:57.801219	6109	12	2799.00	0.00	8901234013003
289	21	Vero Moda Leggings - Black - S	VM-LGG-BLK-S	goods	81	53	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	Vero Moda ankle length leggings	Sales	GST 12%	350	Vero Moda ankle length leggings	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:03:59.295908	2025-12-10 12:03:59.295913	6109	12	599.00	0.00	8901234014001
290	21	Vero Moda Leggings - Black - M	VM-LGG-BLK-M	goods	81	53	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	Vero Moda ankle length leggings	Sales	GST 12%	350	Vero Moda ankle length leggings	Cost of Goods Sold	\N	t	60	0	0	\N	t	t	\N	2025-12-10 12:04:00.41784	2025-12-10 12:04:00.417846	6109	12	599.00	0.00	8901234014002
291	21	Vero Moda Leggings - Black - L	VM-LGG-BLK-L	goods	81	53	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	Vero Moda ankle length leggings	Sales	GST 12%	350	Vero Moda ankle length leggings	Cost of Goods Sold	\N	t	45	0	0	\N	t	t	\N	2025-12-10 12:04:01.539035	2025-12-10 12:04:01.539041	6109	12	599.00	0.00	8901234014003
292	21	Vero Moda Leggings - Navy - M	VM-LGG-NVY-M	goods	81	53	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	Vero Moda ankle length leggings, navy	Sales	GST 12%	350	Vero Moda ankle length leggings, navy	Cost of Goods Sold	\N	t	40	0	0	\N	t	t	\N	2025-12-10 12:04:02.661167	2025-12-10 12:04:02.661173	6109	12	599.00	0.00	8901234014004
293	21	US Polo Kids T-Shirt - Blue - 6-7Y	USP-TSH-BLU-6-7Y	goods	82	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	US Polo Kids cotton t-shirt	Sales	GST 5%	350	US Polo Kids cotton t-shirt	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:04:03.969841	2025-12-10 12:04:03.969848	6109	5	599.00	0.00	8901234015001
294	21	US Polo Kids T-Shirt - Blue - 8-9Y	USP-TSH-BLU-8-9Y	goods	82	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	US Polo Kids cotton t-shirt	Sales	GST 5%	350	US Polo Kids cotton t-shirt	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:04:05.094552	2025-12-10 12:04:05.094558	6109	5	599.00	0.00	8901234015002
295	21	US Polo Kids T-Shirt - White - 8-9Y	USP-TSH-WHT-8-9Y	goods	82	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	US Polo Kids cotton t-shirt, white	Sales	GST 5%	350	US Polo Kids cotton t-shirt, white	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:04:06.215902	2025-12-10 12:04:06.215908	6109	5	599.00	0.00	8901234015003
296	21	US Polo Kids T-Shirt - White - 10-11Y	USP-TSH-WHT-10-11Y	goods	82	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	US Polo Kids cotton t-shirt, white	Sales	GST 5%	350	US Polo Kids cotton t-shirt, white	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:04:07.338149	2025-12-10 12:04:07.338155	6109	5	599.00	0.00	8901234015004
297	21	Gini & Jony Kids Jeans - Blue - 8-9Y	GJ-JNS-BLU-8-9Y	goods	83	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Gini & Jony kids denim jeans	Sales	GST 5%	650	Gini & Jony kids denim jeans	Cost of Goods Sold	\N	t	22	0	0	\N	t	t	\N	2025-12-10 12:04:08.647267	2025-12-10 12:04:08.647272	6109	5	1099.00	0.00	8901234016001
298	21	Gini & Jony Kids Jeans - Blue - 10-11Y	GJ-JNS-BLU-10-11Y	goods	83	46	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	899	Gini & Jony kids denim jeans	Sales	GST 5%	650	Gini & Jony kids denim jeans	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:04:09.770058	2025-12-10 12:04:09.770064	6109	5	1099.00	0.00	8901234016002
299	21	Gini & Jony Kids Shorts - Blue - 8-9Y	GJ-SHT-BLU-8-9Y	goods	84	54	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	499	Gini & Jony kids shorts, comfortable	Sales	GST 5%	350	Gini & Jony kids shorts, comfortable	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:04:11.265236	2025-12-10 12:04:11.265242	6109	5	599.00	0.00	8901234016003
300	21	Baggit Handbag - Brown	BGT-BAG-BRN-001	goods	85	55	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1699	Baggit stylish handbag, vegan leather	Sales	GST 12%	1200	Baggit stylish handbag, vegan leather	Cost of Goods Sold	\N	t	12	0	0	\N	t	t	\N	2025-12-10 12:04:12.759374	2025-12-10 12:04:12.75938	4203	12	1999.00	0.00	8901234017001
301	21	Baggit Handbag - Black	BGT-BAG-BLK-001	goods	85	55	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	1699	Baggit stylish handbag, black, vegan leather	Sales	GST 12%	1200	Baggit stylish handbag, black, vegan leather	Cost of Goods Sold	\N	t	15	0	0	\N	t	t	\N	2025-12-10 12:04:13.882414	2025-12-10 12:04:13.88242	4203	12	1999.00	0.00	8901234017002
302	21	Baggit Purse - Red	BGT-PURSE-RED-001	goods	85	55	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	799	Baggit compact purse, red	Sales	GST 12%	550	Baggit compact purse, red	Cost of Goods Sold	\N	t	10	0	0	\N	t	t	\N	2025-12-10 12:04:15.004483	2025-12-10 12:04:15.004489	4203	12	999.00	0.00	8901234017003
303	21	Baggit Purse - Black	BGT-PURSE-BLK-001	goods	85	55	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	799	Baggit compact purse, black	Sales	GST 12%	550	Baggit compact purse, black	Cost of Goods Sold	\N	t	12	0	0	\N	t	t	\N	2025-12-10 12:04:16.125841	2025-12-10 12:04:16.125848	4203	12	999.00	0.00	8901234017004
304	21	Fastrack Belt - Black - M	FT-BLT-BLK-M	goods	86	56	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	649	Fastrack leather belt, size M (32-34)	Sales	GST 12%	450	Fastrack leather belt, size M (32-34)	Cost of Goods Sold	\N	t	20	0	0	\N	t	t	\N	2025-12-10 12:04:17.621956	2025-12-10 12:04:17.621962	4203	12	799.00	0.00	8901234018001
305	21	Fastrack Belt - Black - L	FT-BLT-BLK-L	goods	86	56	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	649	Fastrack leather belt, size L (36-38)	Sales	GST 12%	450	Fastrack leather belt, size L (36-38)	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:04:18.74313	2025-12-10 12:04:18.743136	4203	12	799.00	0.00	8901234018002
306	21	Fastrack Belt - Brown - M	FT-BLT-BRN-M	goods	86	56	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	649	Fastrack leather belt, brown, size M	Sales	GST 12%	450	Fastrack leather belt, brown, size M	Cost of Goods Sold	\N	t	18	0	0	\N	t	t	\N	2025-12-10 12:04:19.864364	2025-12-10 12:04:19.86437	4203	12	799.00	0.00	8901234018003
307	21	Adidas Men's T-Shirt - White - M	ADI-TSH-WHT-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Adidas essential t-shirt, 3-stripes	Sales	GST 12%	700	Adidas essential t-shirt, 3-stripes	Cost of Goods Sold	\N	t	30	0	0	\N	t	t	\N	2025-12-10 12:04:20.985629	2025-12-10 12:04:20.985635	6109	12	1299.00	0.00	8901234019001
308	21	Adidas Men's T-Shirt - White - L	ADI-TSH-WHT-L	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Adidas essential t-shirt, 3-stripes	Sales	GST 12%	700	Adidas essential t-shirt, 3-stripes	Cost of Goods Sold	\N	t	28	0	0	\N	t	t	\N	2025-12-10 12:04:22.106917	2025-12-10 12:04:22.106923	6109	12	1299.00	0.00	8901234019002
309	21	Adidas Men's T-Shirt - Black - M	ADI-TSH-BLK-M	goods	76	49	Pcs	\N	\N	\N	cm	\N	kg	\N	\N	\N	\N	\N	\N	999	Adidas essential t-shirt, black	Sales	GST 12%	700	Adidas essential t-shirt, black	Cost of Goods Sold	\N	t	25	0	0	\N	t	t	\N	2025-12-10 12:04:23.228664	2025-12-10 12:04:23.22867	6109	12	1299.00	0.00	8901234019003
\.


--
-- Data for Name: loyalty_programs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.loyalty_programs (id, tenant_id, program_name, is_active, points_per_100_rupees, minimum_purchase_for_points, maximum_points_per_invoice, enable_threshold_bonuses, threshold_1_amount, threshold_1_bonus_points, threshold_2_amount, threshold_2_bonus_points, threshold_3_amount, threshold_3_bonus_points, points_to_rupees_ratio, minimum_points_to_redeem, maximum_discount_percent, maximum_points_per_redemption, show_points_on_invoice, invoice_footer_text, created_at, updated_at, enable_birthday_bonus, birthday_bonus_points, enable_anniversary_bonus, anniversary_bonus_points, enable_membership_tiers, tier_bronze_name, tier_bronze_min_points, tier_silver_name, tier_silver_min_points, tier_gold_name, tier_gold_min_points, tier_platinum_name, tier_platinum_min_points, tier_bronze_earning_multiplier, tier_bronze_redemption_multiplier, tier_bronze_max_discount_percent, tier_silver_earning_multiplier, tier_silver_redemption_multiplier, tier_silver_max_discount_percent, tier_gold_earning_multiplier, tier_gold_redemption_multiplier, tier_gold_max_discount_percent, tier_platinum_earning_multiplier, tier_platinum_redemption_multiplier, tier_platinum_max_discount_percent) FROM stdin;
1	17	Loyalty Program	f	1.00	0.00	\N	f	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	\N	\N	\N	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
4	13	Loyalty Program	f	1.00	0.00	\N	f	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	\N	\N	\N	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
6	18	Loyalty Program	f	1.00	0.00	\N	f	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	\N	\N	\N	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
7	19	Loyalty Program	f	1.00	0.00	\N	f	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	\N	\N	\N	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
8	16	Loyalty Program	f	1.00	0.00	\N	f	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	\N	\N	\N	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
9	12	Loyalty Program	f	1.00	0.00	\N	f	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	\N	\N	\N	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
3	11	Loyalty Program	t	1.00	0.00	\N	t	5000.00	50	10000.00	200	\N	\N	1.00	10	\N	\N	t	you have earned {balance} points. Thank you for shopping with us!	\N	2025-12-10 05:44:38.213054	t	100	t	100	t	Bronze	0	Silver	600	Gold	1500	Platinum	5000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
10	21	Loyalty Program	f	1.00	0.00	\N	f	\N	\N	\N	\N	\N	\N	1.00	10	\N	\N	t	Points Balance: {balance} pts | Next visit: ₹{value} off!	2025-12-10 11:20:21.451793	2025-12-10 11:20:21.4518	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
11	20	Loyalty Program	f	1.00	0.00	\N	f	\N	\N	\N	\N	\N	\N	1.00	10	\N	\N	t	Points Balance: {balance} pts | Next visit: ₹{value} off!	2025-12-10 11:29:24.888432	2025-12-10 11:29:24.888437	f	0	f	0	f	Bronze	0	Silver	1000	Gold	5000	Platinum	10000	1.00	1.00	\N	1.20	1.10	\N	1.50	1.25	\N	2.00	1.50	\N
\.


--
-- Data for Name: loyalty_transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.loyalty_transactions (id, tenant_id, customer_id, transaction_type, points, points_before, points_after, invoice_id, invoice_number, description, base_points, bonus_points, invoice_amount, created_at, created_by) FROM stdin;
1	11	6	earned	308	0	308	62	INV-2025-0039	Points earned from invoice INV-2025-0039	108	200	10800.00	2025-12-10 05:47:15.567919	\N
2	11	6	redeemed	-50	308	258	63	INV-2025-0040	Points redeemed for invoice INV-2025-0040	\N	\N	\N	2025-12-10 06:22:32.281243	\N
3	11	6	earned	17	258	275	63	INV-2025-0040	Points earned from invoice INV-2025-0040	17	0	1750.00	2025-12-10 06:22:33.777772	\N
\.


--
-- Data for Name: materials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.materials (id, tenant_id, name, category, unit, description, image, active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: password_reset_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.password_reset_tokens (id, tenant_id, token, created_at, expires_at, used, used_at, ip_address) FROM stdin;
1	11	d82Ng5YQ5nnLvsehSrbr0YFCL4aXyc5SQO2nwEOylbc	2025-12-02 15:43:18.208111	2025-12-02 16:43:18.699782	f	\N	49.43.43.241
2	11	fICJzE3YjBWjiitiAoTFEgu5-QD7zkWy5sWUBMgY6hw	2025-12-02 15:53:21.665777	2025-12-02 16:53:22.183765	f	\N	49.43.43.241
3	11	T7Zxwpala8NNum1qNK7jPtDUc3dxrI6TnLZIQvGCa8I	2025-12-02 16:02:11.126503	2025-12-02 17:02:11.602537	t	2025-12-02 16:02:35.951065	49.43.43.241
\.


--
-- Data for Name: payment_allocations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payment_allocations (id, payment_id, purchase_bill_id, amount_allocated) FROM stdin;
1	2	1	2000.00
2	3	28	4000.00
\.


--
-- Data for Name: payroll_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.payroll_payments (id, tenant_id, payment_month, payment_year, payment_date, total_amount, paid_from_account_id, notes, created_at, created_by) FROM stdin;
2	11	12	2025	2025-12-01	22000.00	4	\N	2025-11-30 19:54:13.285082	\N
3	11	11	2025	2025-12-01	24000.00	9	\N	2025-11-30 20:08:56.708595	\N
\.


--
-- Data for Name: purchase_bill_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.purchase_bill_items (id, tenant_id, purchase_bill_id, item_id, item_name, description, hsn_code, quantity, unit, rate, discount_percentage, discount_amount, taxable_value, gst_rate, cgst_amount, sgst_amount, igst_amount, total_amount, site_id, received_quantity, batch_number, expiry_date, notes, created_at, updated_at) FROM stdin;
1	11	1	\N	LED panel 50W			10.000	pcs	700.00	0.00	0.00	7000.00	5.00	0.00	0.00	350.00	7350.00	\N	0.000	\N	\N	\N	2025-11-07 05:06:38.163578	2025-11-07 05:06:38.163585
2	11	2	\N	LED 12W			10.000	pcs	80.00	0.00	0.00	800.00	12.00	48.00	48.00	0.00	896.00	\N	0.000	\N	\N	\N	2025-11-07 05:22:30.204698	2025-11-07 05:22:30.204703
3	11	3	\N	LED 15W			10.000	pcs	120.00	0.00	0.00	1200.00	18.00	108.00	108.00	0.00	1416.00	\N	0.000	\N	\N	\N	2025-11-07 05:35:37.23667	2025-11-07 05:35:37.236675
4	11	4	\N	LED 20W			10.000	pcs	150.00	0.00	0.00	1500.00	18.00	135.00	135.00	0.00	1770.00	\N	0.000	\N	\N	\N	2025-11-07 05:38:36.303361	2025-11-07 05:38:36.303368
5	11	5	39	Bajaj LED Bulb 9W Cool White B22			10.000	Pcs	112.00	0.00	0.00	1120.00	18.00	100.80	100.80	0.00	1321.60	\N	0.000	\N	\N	\N	2025-11-07 07:41:55.92966	2025-11-07 07:41:55.929666
25	11	26	39	Bajaj LED Bulb 9W Cool White B22			1.000	Pcs	120.00	0.00	0.00	120.00	18.00	10.80	10.80	0.00	141.60	\N	0.000	\N	\N	\N	2025-11-07 18:29:26.958994	2025-11-07 18:29:26.959
26	11	26	40	Bajaj LED Bulb 12W Warm White B22			1.000	Pcs	165.00	0.00	0.00	165.00	18.00	14.85	14.85	0.00	194.70	\N	0.000	\N	\N	\N	2025-11-07 18:29:26.959003	2025-11-07 18:29:26.959005
27	11	27	4	Bajaj Ceiling Fan 48" (1200mm) White			5.000	Pcs	1500.00	0.00	0.00	7500.00	0.00	0.00	0.00	0.00	7500.00	\N	0.000	\N	\N	\N	2025-11-07 18:42:38.330708	2025-11-07 18:42:38.330714
28	11	27	5	Bajaj Ceiling Fan 48" (1200mm) Brown			9.000	Pcs	1500.00	0.00	0.00	13500.00	0.00	0.00	0.00	0.00	13500.00	\N	0.000	\N	\N	\N	2025-11-07 18:42:38.330717	2025-11-07 18:42:38.330719
29	11	28	\N	paneer			10.000	kgs	400.00	0.00	0.00	4000.00	0.00	0.00	0.00	0.00	4000.00	\N	0.000	\N	\N	\N	2025-11-23 12:27:09.735741	2025-11-23 12:27:09.735747
\.


--
-- Data for Name: purchase_bills; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.purchase_bills (id, tenant_id, bill_number, bill_date, due_date, vendor_id, vendor_name, vendor_phone, vendor_email, vendor_gstin, vendor_address, vendor_state, purchase_request_id, subtotal, discount_amount, cgst_amount, sgst_amount, igst_amount, other_charges, round_off, total_amount, payment_status, paid_amount, balance_due, payment_terms, reference_number, notes, terms_conditions, document_url, status, approved_at, approved_by, created_at, updated_at) FROM stdin;
2	11	PB-202511-0002	2025-11-07	\N	\N	Rishi Jain	123456789				Maharashtra	\N	800.00	0.00	48.00	48.00	0.00	0.00	0.00	896.00	unpaid	0.00	896.00		23456			\N	approved	2025-11-07 05:22:38.28761	11	2025-11-07 05:22:29.989588	2025-11-07 05:22:38.288762
3	11	PB-202511-0003	2025-11-07	\N	\N	Rishi Jain	123456789				Maharashtra	\N	1200.00	0.00	108.00	108.00	0.00	0.00	0.00	1416.00	unpaid	0.00	1416.00					\N	approved	2025-11-07 05:36:01.350715	11	2025-11-07 05:35:37.046224	2025-11-07 05:36:01.351825
4	11	PB-202511-0004	2025-11-07	\N	\N	Rishi Jain	123456789				Maharashtra	\N	1500.00	0.00	135.00	135.00	0.00	0.00	0.00	1770.00	unpaid	0.00	1770.00					\N	approved	2025-11-07 05:38:42.814428	11	2025-11-07 05:38:36.114517	2025-11-07 05:38:42.815632
1	11	PB-202511-0001	2025-11-07	\N	1	Rishi Jain	123456789				madhya pradesh	\N	7000.00	0.00	0.00	0.00	350.00	0.00	0.00	7350.00	partial	2000.00	5350.00	45	12345			\N	approved	2025-11-07 05:18:07.668072	11	2025-11-07 05:06:37.970141	2025-11-07 05:55:21.689142
5	11	PB-202511-0005	2025-11-07	\N	2	Ayushi Samaiya	8983121201				Maharashtra	\N	1120.00	0.00	100.80	100.80	0.00	0.00	0.00	1321.60	unpaid	0.00	1321.60					\N	approved	2025-11-07 07:42:08.312958	11	2025-11-07 07:41:55.727218	2025-11-07 07:42:08.314088
26	11	PB-202511-0007	2025-11-07	\N	2	Ayushi Samaiya	8983121201				Maharashtra	\N	285.00	0.00	25.65	25.65	0.00	0.00	0.00	336.30	unpaid	0.00	336.30					\N	draft	\N	\N	2025-11-07 18:29:26.758834	2025-11-07 18:29:26.758839
27	11	PB-202511-0008	2025-11-07	\N	1	Rishi Jain	123456789				Madhya Pradesh	\N	21000.00	0.00	0.00	0.00	0.00	0.00	0.00	21000.00	unpaid	0.00	21000.00		22222			\N	approved	2025-11-07 18:47:07.285304	11	2025-11-07 18:42:38.136172	2025-11-07 18:47:07.473593
28	11	PB-202511-0009	2025-11-23	\N	6	self					Maharashtra	\N	4000.00	0.00	0.00	0.00	0.00	0.00	0.00	4000.00	paid	4000.00	0.00		123456			\N	approved	2025-11-23 12:28:16.792471	11	2025-11-23 12:27:09.512722	2025-11-29 19:24:44.527323
\.


--
-- Data for Name: purchase_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.purchase_requests (id, tenant_id, employee_id, item_name, quantity, estimated_price, vendor_name, request_type, category_id, reason, document_url, status, admin_notes, rejection_reason, processed_by, processed_at, created_expense_id, created_item_id, created_at, updated_at) FROM stdin;
11	11	13	Paint	1	1000	Ta shah	expense	3	Needed for paint	\N	approved		\N	Mahaveer Electricals	2025-11-02 19:27:01.425242	7	\N	2025-11-02 19:18:40.506774	2025-11-02 19:27:01.81958
12	11	13	Playwood	2	800	Ta shah	expense	3	Need for fixing door	\N	rejected	\N	already bought	Mahaveer Electricals	2025-11-02 19:34:51.093989	\N	\N	2025-11-02 19:33:34.932264	2025-11-02 19:34:51.095218
15	11	13	Jdhdh	2	400	Jdbb	expense	3	Hzb	\N	rejected	\N	send the image	Mahaveer Electricals	2025-11-02 20:08:53.089288	\N	\N	2025-11-02 20:06:43.503795	2025-11-02 20:08:53.090387
13	11	13	Playwood	5	1000	TA shah	expense	3	Need for fixing windows	\N	approved		\N	Mahaveer Electricals	2025-11-03 04:17:41.950794	8	\N	2025-11-02 19:42:44.167511	2025-11-03 04:17:42.347879
14	11	13	Hshsh	2	300	Nsb	expense	3	Bdb	\N	approved		\N	Mahaveer Electricals	2025-11-03 04:17:53.488605	9	\N	2025-11-02 19:58:48.53546	2025-11-03 04:17:53.861901
16	11	13	This	1	100	T	expense	3	Hsv	\N	rejected	\N	not needed now	Mahaveer Electricals	2025-11-03 04:18:18.847106	\N	\N	2025-11-02 20:16:12.026204	2025-11-03 04:18:18.848023
17	11	13	This is test	1	100	Ta	expense	3	Bsnsb	https://pyr7htm7ayy38zig.public.blob.vercel-storage.com/purchase_requests/rishi_jain_20251102_202311-IhLwQ7oCSI47OLv0nbXf2WQwUXhxBr.jpg	approved		\N	Mahaveer Electricals	2025-11-03 04:18:33.23731	10	\N	2025-11-02 20:23:12.761292	2025-11-03 04:18:33.610557
18	11	13	Cemet	2	600	Mp stone	expense	3	Shortage for completing floor	https://pyr7htm7ayy38zig.public.blob.vercel-storage.com/purchase_requests/rishi_jain_20251103_054323-1be5ZazozxDaOfFprEBov2M88lWbdM.jpg	approved		\N	Mahaveer Electricals	2025-11-03 05:45:16.634851	11	\N	2025-11-03 05:43:25.278186	2025-11-03 05:45:17.019658
\.


--
-- Data for Name: salary_slips; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.salary_slips (id, tenant_id, payroll_payment_id, employee_id, payment_month, payment_year, salary_amount, payment_date, payment_method, notes, created_at) FROM stdin;
1	11	2	14	12	2025	12000.00	2025-12-01	Cash	\N	2025-11-30 19:54:13.285082
2	11	2	13	12	2025	10000.00	2025-12-01	Cash	\N	2025-11-30 19:54:13.285082
3	11	3	16	11	2025	15000.00	2025-12-01	Cash	\N	2025-11-30 20:08:56.708595
4	11	3	17	11	2025	9000.00	2025-12-01	Cash	\N	2025-11-30 20:13:00.349664
\.


--
-- Data for Name: sales_order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sales_order_items (id, sales_order_id, tenant_id, item_id, item_name, description, hsn_code, quantity, unit, rate, gst_rate, price_inclusive, discount_type, discount_value, taxable_amount, tax_amount, total_amount, quantity_delivered, quantity_invoiced, stock_reserved, site_id, created_at) FROM stdin;
19	15	11	39	Bajaj LED Bulb 9W Cool White B22			25.000	pcs	120.00	12.00	f	percentage	0.00	3000.00	360.00	3360.00	25.000	0.000	t	12	2025-11-06 12:38:58.080075
18	14	11	39	Bajaj LED Bulb 9W Cool White B22			10.000	pcs	120.00	12.00	f	percentage	0.00	1200.00	144.00	1344.00	10.000	0.000	t	12	2025-11-06 12:31:52.580285
17	13	11	9	Bajaj Table Fan 400mm White			10.000	pcs	850.00	18.00	f	percentage	0.00	8500.00	1530.00	10030.00	10.000	0.000	t	12	2025-11-06 12:23:31.060939
20	16	11	10	Orient Table Fan 400mm Blue			5.000	pcs	950.00	18.00	f	percentage	0.00	4750.00	855.00	5605.00	5.000	5.000	t	12	2025-11-06 12:43:10.491964
11	7	11	41	Bajaj LED Bulb 15W Cool White B22			70.000	pcs	210.00	12.00	f	percentage	0.00	14700.00	1764.00	16464.00	0.000	0.000	f	\N	2025-11-06 11:11:59.811371
10	6	11	40	Bajaj LED Bulb 12W Warm White B22			80.000	pcs	165.00	12.00	f	percentage	0.00	13200.00	1584.00	14784.00	0.000	0.000	t	12	2025-11-06 10:54:54.855644
12	8	11	6	HBL Premium Ceiling Fan 52" White			10.000	pcs	1850.00	18.00	f	percentage	0.00	18500.00	3330.00	21830.00	0.000	10.000	t	12	2025-11-06 11:20:26.876535
\.


--
-- Data for Name: sales_orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sales_orders (id, tenant_id, order_number, order_date, expected_delivery_date, customer_id, customer_name, customer_phone, customer_email, customer_gstin, billing_address, shipping_address, subtotal, discount_amount, tax_amount, total_amount, status, quantity_ordered, quantity_delivered, quantity_invoiced, quotation_id, terms_and_conditions, notes, created_at, updated_at, created_by) FROM stdin;
6	11	SO-2511-0002	2025-11-06	2025-11-13	3	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	27AABCU9603R1ZM	Shop 12, MG Road, Indore		13200.00	0.00	1584.00	14784.00	confirmed	80	0	0	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 10:54:54.659185	2025-11-06 11:01:14.780926	Mahaveer Electricals
8	11	SO-2511-0004	2025-11-06	\N	4	Sharma Traders	9988776655	sharma@gmail.com		Main Market, Indore		18500.00	0.00	3330.00	21830.00	invoiced	10	0	10	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 11:20:26.680759	2025-11-06 11:33:47.772653	Mahaveer Electricals
14	11	SO-2511-0007	2025-11-06	\N	2	ABC Corporation	9876543210	contact@abc.com	27AABCU9603R1ZM	123 Business Park, Mumbai, 400001		1200.00	0.00	144.00	1344.00	delivered	10	10	0	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 12:31:52.389554	2025-11-06 13:01:58.532305	Mahaveer Electricals
13	11	SO-2511-0006	2025-11-06	\N	4	Sharma Traders	9988776655	sharma@gmail.com		Main Market, Indore		8500.00	0.00	1530.00	10030.00	delivered	10	10	0	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 12:23:30.860486	2025-11-06 13:42:33.101806	Mahaveer Electricals
16	11	SO-2511-0009	2025-11-06	\N	3	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	27AABCU9603R1ZM	Shop 12, MG Road, Indore		4750.00	0.00	855.00	5605.00	invoiced	5	5	5	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 12:43:10.272693	2025-11-06 14:29:25.874319	Mahaveer Electricals
7	11	SO-2511-0003	2025-11-06	2025-11-20	2	ABC Corporation	9876543210	contact@abc.com	27AABCU9603R1ZM	123 Business Park, Mumbai, 400001		14700.00	0.00	1764.00	16464.00	cancelled	70	0	0	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 11:11:59.60509	2025-11-08 18:18:20.811207	Mahaveer Electricals
15	11	SO-2511-0008	2025-11-06	\N	3	Rishi Enterprises	9876543210	rishi.samaiya@gmail.com	27AABCU9603R1ZM	Shop 12, MG Road, Indore		3000.00	0.00	360.00	3360.00	cancelled	25	25	0	\N	Payment within 30 days\r\nDelivery as per schedule\r\nSubject to Mumbai jurisdiction		2025-11-06 12:38:57.889639	2025-11-08 18:20:45.898922	Mahaveer Electricals
\.


--
-- Data for Name: sites; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sites (id, tenant_id, name, address, latitude, longitude, allowed_radius, active, created_at, updated_at, is_default) FROM stdin;
14	12	cleanbowl - Main Office		0	0	100	t	2025-11-03 18:02:41.261604	2025-11-03 18:02:41.26161	f
15	13	Ayush Agrawal - Main Office		0	0	100	t	2025-11-03 19:57:19.950972	2025-11-03 19:57:19.950979	f
13	11	Godown		22.6111	77.77	150	t	2025-11-02 18:05:46.909513	2025-11-08 12:26:19.172064	f
18	16	Anand motor - Main Office		0	0	100	t	2025-11-20 05:50:55.531763	2025-11-20 05:50:55.531768	f
19	17	Saumya steels - Main Office		0	0	100	t	2025-11-20 06:03:50.245429	2025-11-20 06:03:50.245434	f
20	13	DLS		0	0	100	t	2025-11-28 19:08:20.596761	2025-11-28 19:08:20.596767	f
21	13	HeadOffice		0	0	100	t	2025-11-28 19:08:22.537282	2025-11-28 19:08:22.537289	f
22	18	tally professinal - Main Office		0	0	100	t	2025-12-01 10:57:17.545664	2025-12-01 10:57:17.54567	f
23	19	tally professinal - Main Office		0	0	100	t	2025-12-01 11:07:27.649706	2025-12-01 11:07:27.649713	f
24	16	delivery		0	0	100	t	2025-12-03 19:51:03.046446	2025-12-03 19:51:03.04645	f
12	11	Mahaveer Electricals		23.210064	77.441191	100	t	2025-11-02 10:46:07.938018	2025-11-21 05:15:49.501462	t
25	20	SW Test Projecf - Main Office		0	0	100	t	2025-12-10 07:05:54.392399	2025-12-10 07:05:54.392404	t
26	21	Anand Vastralaya - Main Office		0	0	100	t	2025-12-10 11:09:03.306201	2025-12-10 11:09:03.306206	t
29	21	godown	1st Lane	0	0	100	t	2025-12-10 13:17:55.134934	2025-12-10 13:17:55.134938	f
\.


--
-- Data for Name: stock_movements; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stock_movements (id, tenant_id, material_id, site_id, type, quantity, reason, reference, "timestamp", user_id, transfer_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: stocks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stocks (id, tenant_id, material_id, site_id, quantity, min_stock_alert, last_updated, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: subscription_deliveries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.subscription_deliveries (id, tenant_id, subscription_id, delivery_date, quantity, rate, amount, status, is_modified, modification_reason, notes, created_at, updated_at, delivered_by, delivered_at, bottles_delivered, bottles_collected, assigned_to) FROM stdin;
1	11	7	2025-11-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.715979	2025-11-22 19:50:04.715985	\N	\N	0	0	\N
2	11	7	2025-11-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.715987	2025-11-22 19:50:04.715989	\N	\N	0	0	\N
6	11	7	2025-11-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716002	2025-11-26 19:46:37.907042	21	2025-11-26 19:46:37.906393	1	2	21
93	16	13	2025-12-02	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652361	2025-12-02 15:49:51.652366	\N	\N	0	0	\N
94	16	13	2025-12-03	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652369	2025-12-02 15:49:51.652371	\N	\N	0	0	\N
1126	16	46	2025-12-28	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624197	2025-12-03 19:59:05.138213	\N	\N	0	0	28
1127	16	46	2025-12-29	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624201	2025-12-03 19:59:05.138215	\N	\N	0	0	28
1128	16	46	2025-12-30	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624205	2025-12-03 19:59:05.138217	\N	\N	0	0	28
1129	16	46	2025-12-31	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624209	2025-12-03 19:59:05.13822	\N	\N	0	0	28
1133	16	47	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759586	2025-12-03 19:59:10.91321	\N	\N	0	0	28
1134	16	47	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.75959	2025-12-03 19:59:10.913217	\N	\N	0	0	28
1135	16	47	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759594	2025-12-03 19:59:10.913219	\N	\N	0	0	28
1136	16	47	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759598	2025-12-03 19:59:10.913221	\N	\N	0	0	28
1137	16	47	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759601	2025-12-03 19:59:10.913223	\N	\N	0	0	28
1138	16	47	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759605	2025-12-03 19:59:10.913225	\N	\N	0	0	28
1139	16	47	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759609	2025-12-03 19:59:10.913227	\N	\N	0	0	28
1140	16	47	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759613	2025-12-03 19:59:10.913229	\N	\N	0	0	28
1141	16	47	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759617	2025-12-03 19:59:10.913231	\N	\N	0	0	28
1142	16	47	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759621	2025-12-03 19:59:10.913233	\N	\N	0	0	28
1143	16	47	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759625	2025-12-03 19:59:10.913235	\N	\N	0	0	28
1144	16	47	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759629	2025-12-03 19:59:10.913237	\N	\N	0	0	28
1145	16	47	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759633	2025-12-03 19:59:10.913239	\N	\N	0	0	28
1146	16	47	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759638	2025-12-03 19:59:10.913241	\N	\N	0	0	28
1147	16	47	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759642	2025-12-03 19:59:10.913243	\N	\N	0	0	28
1148	16	47	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759646	2025-12-03 19:59:10.913245	\N	\N	0	0	28
1149	16	47	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.75965	2025-12-03 19:59:10.913247	\N	\N	0	0	28
1150	16	47	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759654	2025-12-03 19:59:10.913249	\N	\N	0	0	28
1151	16	47	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759658	2025-12-03 19:59:10.913251	\N	\N	0	0	28
1152	16	47	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759662	2025-12-03 19:59:10.913253	\N	\N	0	0	28
1153	16	47	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759666	2025-12-03 19:59:10.913255	\N	\N	0	0	28
1154	16	47	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.75967	2025-12-03 19:59:10.913257	\N	\N	0	0	28
1155	16	47	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759674	2025-12-03 19:59:10.913259	\N	\N	0	0	28
154	16	15	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056187	2025-12-02 15:57:17.056192	\N	\N	0	0	\N
70	11	10	2025-11-23	1.50	80.00	120.00	delivered	f	\N	\N	2025-11-23 04:17:30.37132	2025-11-23 04:17:30.371326	\N	\N	0	0	\N
71	11	10	2025-11-24	1.50	80.00	120.00	delivered	f	\N	\N	2025-11-23 04:17:30.371329	2025-11-23 04:17:30.371331	\N	\N	0	0	\N
3	11	7	2025-11-24	3.00	80.00	240.00	delivered	t	party	\N	2025-11-22 19:50:04.715991	2025-11-22 20:00:38.772093	\N	\N	0	0	\N
8	11	7	2025-11-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.71601	2025-11-26 19:43:23.332781	\N	\N	0	0	21
61	11	9	2025-11-22	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.513997	2025-11-22 20:34:02.514002	\N	\N	0	0	\N
62	11	9	2025-11-23	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514004	2025-11-22 20:34:02.514006	\N	\N	0	0	\N
63	11	9	2025-11-24	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514008	2025-11-22 20:34:02.514009	\N	\N	0	0	\N
64	11	9	2025-11-25	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514011	2025-11-22 20:34:02.514013	\N	\N	0	0	\N
65	11	9	2025-11-26	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514015	2025-11-22 20:34:02.514017	\N	\N	0	0	\N
66	11	9	2025-11-27	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514018	2025-11-22 20:34:02.51402	\N	\N	0	0	\N
67	11	9	2025-11-28	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514022	2025-11-22 20:34:02.514023	\N	\N	0	0	\N
68	11	9	2025-11-29	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514025	2025-11-22 20:34:02.514027	\N	\N	0	0	\N
69	11	9	2025-11-30	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-22 20:34:02.514029	2025-11-22 20:34:02.51403	\N	\N	0	0	\N
73	11	10	2025-11-26	1.50	80.00	120.00	delivered	f	\N	\N	2025-11-23 04:17:30.371337	2025-11-23 04:17:30.371338	\N	\N	0	0	\N
76	11	10	2025-11-29	1.50	80.00	120.00	delivered	f	\N	\N	2025-11-23 04:17:30.371348	2025-11-23 04:17:30.37135	\N	\N	0	0	\N
77	11	10	2025-11-30	1.50	80.00	120.00	delivered	f	\N	\N	2025-11-23 04:17:30.371352	2025-11-23 04:17:30.371353	\N	\N	0	0	\N
72	11	10	2025-11-25	3.00	80.00	240.00	delivered	t	Party	\N	2025-11-23 04:17:30.371333	2025-11-23 04:18:22.323897	\N	\N	0	0	\N
9	11	7	2025-11-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716013	2025-11-26 19:43:23.332783	\N	\N	0	0	21
75	11	10	2025-11-28	0.00	80.00	0.00	paused	t	Vacation	\N	2025-11-23 04:17:30.371344	2025-11-23 04:18:47.890581	\N	\N	0	0	\N
78	11	11	2025-11-23	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-23 10:53:46.45184	2025-11-23 10:53:46.451845	\N	\N	0	0	\N
79	11	11	2025-11-24	0.00	80.00	0.00	paused	t	Paused by customer	\N	2025-11-23 10:53:46.451848	2025-11-23 11:07:49.349665	\N	\N	0	0	\N
10	11	7	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716017	2025-11-26 19:43:23.332785	\N	\N	0	0	21
86	11	12	2025-11-24	3.00	80.00	240.00	delivered	f	\N	\N	2025-11-24 18:13:35.309752	2025-11-24 18:13:35.309759	\N	\N	0	0	\N
80	11	11	2025-11-25	3.00	80.00	240.00	delivered	t	Quantity changed to 3.0 by customer	\N	2025-11-23 10:53:46.451851	2025-11-25 04:32:37.596105	13	2025-11-24 20:50:37.991504	3	1	18
87	11	12	2025-11-25	3.00	80.00	240.00	delivered	f	\N	\N	2025-11-24 18:13:35.309761	2025-11-25 04:32:53.120549	\N	\N	0	0	18
88	11	12	2025-11-26	3.00	80.00	240.00	delivered	f	\N	\N	2025-11-24 18:13:35.309765	2025-11-26 11:59:43.480904	16	2025-11-26 11:59:43.480277	3	2	16
4	11	7	2025-11-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.715995	2025-11-24 20:51:14.109799	13	2025-11-24 20:51:14.107191	1	1	\N
74	11	10	2025-11-27	1.50	80.00	120.00	delivered	f	\N	\N	2025-11-23 04:17:30.37134	2025-11-26 19:35:10.845768	\N	\N	0	0	\N
5	11	7	2025-11-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.715999	2025-11-26 11:57:03.093004	16	2025-11-26 11:57:03.091388	1	4	16
81	11	11	2025-11-26	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-23 10:53:46.451855	2025-11-26 11:58:53.852336	16	2025-11-26 11:58:53.851676	2	2	16
7	11	7	2025-11-28	0.00	80.00	0.00	paused	t	out of town	\N	2025-11-22 19:50:04.716006	2025-11-26 19:43:23.332779	\N	\N	0	0	21
11	11	7	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716021	2025-11-26 19:43:23.332787	\N	\N	0	0	21
12	11	7	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716025	2025-11-26 19:43:23.332789	\N	\N	0	0	21
14	11	7	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716032	2025-11-26 19:43:23.332793	\N	\N	0	0	21
15	11	7	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716036	2025-11-26 19:43:23.332795	\N	\N	0	0	21
16	11	7	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716039	2025-11-26 19:43:23.332797	\N	\N	0	0	21
17	11	7	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716043	2025-11-26 19:43:23.332799	\N	\N	0	0	21
18	11	7	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716047	2025-11-26 19:43:23.332801	\N	\N	0	0	21
19	11	7	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716051	2025-11-26 19:43:23.332803	\N	\N	0	0	21
20	11	7	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716054	2025-11-26 19:43:23.332805	\N	\N	0	0	21
21	11	7	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716058	2025-11-26 19:43:23.332806	\N	\N	0	0	21
22	11	7	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716062	2025-11-26 19:43:23.332808	\N	\N	0	0	21
23	11	7	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716065	2025-11-26 19:43:23.33281	\N	\N	0	0	21
24	11	7	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716069	2025-11-26 19:43:23.332812	\N	\N	0	0	21
25	11	7	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716073	2025-11-26 19:43:23.332814	\N	\N	0	0	21
26	11	7	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716077	2025-11-26 19:43:23.332816	\N	\N	0	0	21
27	11	7	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.71608	2025-11-26 19:43:23.332818	\N	\N	0	0	21
28	11	7	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716084	2025-11-26 19:43:23.33282	\N	\N	0	0	21
29	11	7	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716088	2025-11-26 19:43:23.332822	\N	\N	0	0	21
30	11	7	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-11-22 19:50:04.716091	2025-11-26 19:43:23.332823	\N	\N	0	0	21
90	11	12	2025-11-28	2.00	80.00	160.00	delivered	t	less member	\N	2025-11-24 18:13:35.309773	2025-11-26 19:43:28.580092	\N	\N	0	0	21
91	11	12	2025-11-29	3.00	80.00	240.00	delivered	f	\N	\N	2025-11-24 18:13:35.309777	2025-11-26 19:43:28.580094	\N	\N	0	0	21
92	11	12	2025-11-30	3.00	80.00	240.00	delivered	f	\N	\N	2025-11-24 18:13:35.30978	2025-11-26 19:43:28.580096	\N	\N	0	0	21
83	11	11	2025-11-28	0.00	80.00	0.00	paused	t	Paused by customer	\N	2025-11-23 10:53:46.451863	2025-11-26 19:43:29.890061	\N	\N	0	0	21
84	11	11	2025-11-29	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-23 10:53:46.451867	2025-11-26 19:43:29.890063	\N	\N	0	0	21
85	11	11	2025-11-30	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-23 10:53:46.451871	2025-11-26 19:43:29.890065	\N	\N	0	0	21
82	11	11	2025-11-27	2.00	80.00	160.00	delivered	f	\N	\N	2025-11-23 10:53:46.451859	2025-11-26 19:46:25.265169	21	2025-11-26 19:46:25.263709	2	1	21
89	11	12	2025-11-27	3.00	80.00	240.00	delivered	f	\N	\N	2025-11-24 18:13:35.309769	2025-11-26 19:46:49.807968	21	2025-11-26 19:46:49.807314	3	2	21
123	16	14	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365305	2025-12-02 15:55:36.365311	\N	\N	0	0	\N
124	16	14	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365314	2025-12-02 15:55:36.365316	\N	\N	0	0	\N
125	16	14	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365318	2025-12-02 15:55:36.36532	\N	\N	0	0	\N
126	16	14	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365322	2025-12-02 15:55:36.365324	\N	\N	0	0	\N
127	16	14	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365327	2025-12-02 15:55:36.365328	\N	\N	0	0	\N
128	16	14	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365331	2025-12-02 15:55:36.365333	\N	\N	0	0	\N
129	16	14	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365335	2025-12-02 15:55:36.365337	\N	\N	0	0	\N
130	16	14	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365339	2025-12-02 15:55:36.365341	\N	\N	0	0	\N
131	16	14	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365343	2025-12-02 15:55:36.365345	\N	\N	0	0	\N
132	16	14	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365347	2025-12-02 15:55:36.365349	\N	\N	0	0	\N
133	16	14	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365352	2025-12-02 15:55:36.365353	\N	\N	0	0	\N
134	16	14	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365356	2025-12-02 15:55:36.365357	\N	\N	0	0	\N
135	16	14	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.36536	2025-12-02 15:55:36.365362	\N	\N	0	0	\N
136	16	14	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365364	2025-12-02 15:55:36.365366	\N	\N	0	0	\N
137	16	14	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365368	2025-12-02 15:55:36.36537	\N	\N	0	0	\N
138	16	14	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365372	2025-12-02 15:55:36.365374	\N	\N	0	0	\N
139	16	14	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365376	2025-12-02 15:55:36.365378	\N	\N	0	0	\N
140	16	14	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.36538	2025-12-02 15:55:36.365382	\N	\N	0	0	\N
141	16	14	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365385	2025-12-02 15:55:36.365386	\N	\N	0	0	\N
142	16	14	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365389	2025-12-02 15:55:36.36539	\N	\N	0	0	\N
143	16	14	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365393	2025-12-02 15:55:36.365395	\N	\N	0	0	\N
144	16	14	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365397	2025-12-02 15:55:36.365399	\N	\N	0	0	\N
145	16	14	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365401	2025-12-02 15:55:36.365403	\N	\N	0	0	\N
146	16	14	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365405	2025-12-02 15:55:36.365407	\N	\N	0	0	\N
147	16	14	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.36541	2025-12-02 15:55:36.365411	\N	\N	0	0	\N
148	16	14	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365414	2025-12-02 15:55:36.365415	\N	\N	0	0	\N
149	16	14	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365418	2025-12-02 15:55:36.36542	\N	\N	0	0	\N
150	16	14	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365422	2025-12-02 15:55:36.365424	\N	\N	0	0	\N
151	16	14	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365426	2025-12-02 15:55:36.365428	\N	\N	0	0	\N
152	16	14	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.36543	2025-12-02 15:55:36.365432	\N	\N	0	0	\N
153	16	14	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 15:55:36.365434	2025-12-02 15:55:36.365436	\N	\N	0	0	\N
155	16	15	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056195	2025-12-02 15:57:17.056197	\N	\N	0	0	\N
156	16	15	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056199	2025-12-02 15:57:17.056201	\N	\N	0	0	\N
1156	16	47	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759678	2025-12-03 19:59:10.913261	\N	\N	0	0	28
1157	16	47	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759682	2025-12-03 19:59:10.913263	\N	\N	0	0	28
1158	16	47	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759686	2025-12-03 19:59:10.913265	\N	\N	0	0	28
1159	16	47	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.75969	2025-12-03 19:59:10.913267	\N	\N	0	0	28
1160	16	47	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759694	2025-12-03 19:59:10.913269	\N	\N	0	0	28
1164	16	48	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.8972	2025-12-03 19:59:16.689724	\N	\N	0	0	28
1165	16	48	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897204	2025-12-03 19:59:16.689738	\N	\N	0	0	28
1166	16	48	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897208	2025-12-03 19:59:16.689743	\N	\N	0	0	28
1167	16	48	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897212	2025-12-03 19:59:16.689745	\N	\N	0	0	28
1168	16	48	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897216	2025-12-03 19:59:16.689747	\N	\N	0	0	28
1169	16	48	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.89722	2025-12-03 19:59:16.689749	\N	\N	0	0	28
1170	16	48	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897224	2025-12-03 19:59:16.689751	\N	\N	0	0	28
1171	16	48	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897228	2025-12-03 19:59:16.689753	\N	\N	0	0	28
1172	16	48	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897232	2025-12-03 19:59:16.689755	\N	\N	0	0	28
1173	16	48	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897236	2025-12-03 19:59:16.689758	\N	\N	0	0	28
1174	16	48	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.89724	2025-12-03 19:59:16.68976	\N	\N	0	0	28
1175	16	48	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897243	2025-12-03 19:59:16.689762	\N	\N	0	0	28
1176	16	48	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897247	2025-12-03 19:59:16.689764	\N	\N	0	0	28
1177	16	48	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897251	2025-12-03 19:59:16.689766	\N	\N	0	0	28
1178	16	48	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897255	2025-12-03 19:59:16.689768	\N	\N	0	0	28
1179	16	48	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897259	2025-12-03 19:59:16.68977	\N	\N	0	0	28
1180	16	48	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897263	2025-12-03 19:59:16.689771	\N	\N	0	0	28
1181	16	48	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897267	2025-12-03 19:59:16.689773	\N	\N	0	0	28
1182	16	48	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897271	2025-12-03 19:59:16.689775	\N	\N	0	0	28
1183	16	48	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897275	2025-12-03 19:59:16.689777	\N	\N	0	0	28
1184	16	48	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897279	2025-12-03 19:59:16.689779	\N	\N	0	0	28
1185	16	48	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897283	2025-12-03 19:59:16.689781	\N	\N	0	0	28
1186	16	48	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897287	2025-12-03 19:59:16.689783	\N	\N	0	0	28
1187	16	48	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897291	2025-12-03 19:59:16.689785	\N	\N	0	0	28
185	16	16	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.26697	2025-12-02 15:58:30.266976	\N	\N	0	0	\N
186	16	16	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.266979	2025-12-02 15:58:30.266981	\N	\N	0	0	\N
187	16	16	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.266983	2025-12-02 15:58:30.266985	\N	\N	0	0	\N
1188	16	48	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897295	2025-12-03 19:59:16.689787	\N	\N	0	0	28
1189	16	48	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897299	2025-12-03 19:59:16.689789	\N	\N	0	0	28
1190	16	48	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897302	2025-12-03 19:59:16.689791	\N	\N	0	0	28
1191	16	48	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897306	2025-12-03 19:59:16.689793	\N	\N	0	0	28
1195	16	49	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046658	2025-12-03 19:59:22.465315	\N	\N	0	0	28
1196	16	49	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046662	2025-12-03 19:59:22.46532	\N	\N	0	0	28
1197	16	49	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046666	2025-12-03 19:59:22.465322	\N	\N	0	0	28
1198	16	49	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046671	2025-12-03 19:59:22.465324	\N	\N	0	0	28
1199	16	49	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046675	2025-12-03 19:59:22.465326	\N	\N	0	0	28
1200	16	49	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046679	2025-12-03 19:59:22.465328	\N	\N	0	0	28
1201	16	49	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046683	2025-12-03 19:59:22.46533	\N	\N	0	0	28
1202	16	49	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046687	2025-12-03 19:59:22.465332	\N	\N	0	0	28
1203	16	49	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046691	2025-12-03 19:59:22.465334	\N	\N	0	0	28
1204	16	49	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046695	2025-12-03 19:59:22.465336	\N	\N	0	0	28
1205	16	49	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046699	2025-12-03 19:59:22.465338	\N	\N	0	0	28
1206	16	49	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046703	2025-12-03 19:59:22.46534	\N	\N	0	0	28
1207	16	49	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046708	2025-12-03 19:59:22.465342	\N	\N	0	0	28
1208	16	49	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046712	2025-12-03 19:59:22.465344	\N	\N	0	0	28
1209	16	49	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046716	2025-12-03 19:59:22.465346	\N	\N	0	0	28
1210	16	49	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.04672	2025-12-03 19:59:22.465348	\N	\N	0	0	28
1211	16	49	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046724	2025-12-03 19:59:22.46535	\N	\N	0	0	28
1212	16	49	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046728	2025-12-03 19:59:22.465352	\N	\N	0	0	28
1213	16	49	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046732	2025-12-03 19:59:22.465354	\N	\N	0	0	28
1214	16	49	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046736	2025-12-03 19:59:22.465356	\N	\N	0	0	28
1215	16	49	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.04674	2025-12-03 19:59:22.465358	\N	\N	0	0	28
1216	16	49	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046744	2025-12-03 19:59:22.465361	\N	\N	0	0	28
1217	16	49	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046748	2025-12-03 19:59:22.465363	\N	\N	0	0	28
1218	16	49	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046752	2025-12-03 19:59:22.465365	\N	\N	0	0	28
216	16	17	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356685	2025-12-02 17:45:36.356691	\N	\N	0	0	\N
217	16	17	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356694	2025-12-02 17:45:36.356696	\N	\N	0	0	\N
218	16	17	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356698	2025-12-02 17:45:36.3567	\N	\N	0	0	\N
1219	16	49	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046756	2025-12-03 19:59:22.465367	\N	\N	0	0	28
1220	16	49	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046759	2025-12-03 19:59:22.465369	\N	\N	0	0	28
1221	16	49	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046763	2025-12-03 19:59:22.465371	\N	\N	0	0	28
1222	16	49	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046767	2025-12-03 19:59:22.465373	\N	\N	0	0	28
2614	16	91	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744129	2025-12-03 19:59:38.15657	\N	\N	0	0	28
2615	16	91	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744133	2025-12-03 19:59:38.156572	\N	\N	0	0	28
2616	16	91	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744137	2025-12-03 19:59:38.156574	\N	\N	0	0	28
2617	16	91	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744141	2025-12-03 19:59:38.156576	\N	\N	0	0	28
2618	16	91	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744145	2025-12-03 19:59:38.156578	\N	\N	0	0	28
2619	16	91	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744149	2025-12-03 19:59:38.15658	\N	\N	0	0	28
2620	16	91	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744154	2025-12-03 19:59:38.156582	\N	\N	0	0	28
2621	16	91	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744158	2025-12-03 19:59:38.156584	\N	\N	0	0	28
2622	16	91	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744162	2025-12-03 19:59:38.156586	\N	\N	0	0	28
2623	16	91	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744166	2025-12-03 19:59:38.156588	\N	\N	0	0	28
2624	16	91	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.74417	2025-12-03 19:59:38.15659	\N	\N	0	0	28
2625	16	91	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744174	2025-12-03 19:59:38.156592	\N	\N	0	0	28
2626	16	91	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744179	2025-12-03 19:59:38.156594	\N	\N	0	0	28
2627	16	91	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744183	2025-12-03 19:59:38.156596	\N	\N	0	0	28
2628	16	91	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744187	2025-12-03 19:59:38.156598	\N	\N	0	0	28
2629	16	91	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744191	2025-12-03 19:59:38.1566	\N	\N	0	0	28
2630	16	91	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744195	2025-12-03 19:59:38.156602	\N	\N	0	0	28
174	16	15	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056272	2025-12-03 19:55:13.384514	\N	\N	0	0	28
175	16	15	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056276	2025-12-03 19:55:13.384516	\N	\N	0	0	28
2669	11	12	2025-12-03	2.00	80.00	160.00	delivered	t		\N	2025-12-04 05:27:40.314257	2025-12-04 05:27:40.314264	\N	\N	0	0	\N
277	16	19	2025-12-01	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.37859	2025-12-02 18:55:03.378595	\N	\N	0	0	\N
278	16	19	2025-12-03	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378598	2025-12-02 18:55:03.3786	\N	\N	0	0	\N
293	16	20	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994555	2025-12-02 19:10:08.994561	\N	\N	0	0	\N
294	16	20	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994564	2025-12-02 19:10:08.994566	\N	\N	0	0	\N
295	16	20	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994569	2025-12-02 19:10:08.99457	\N	\N	0	0	\N
279	16	19	2025-12-05	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378602	2025-12-03 19:55:30.7223	\N	\N	0	0	28
280	16	19	2025-12-07	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378606	2025-12-03 19:55:30.722306	\N	\N	0	0	28
281	16	19	2025-12-09	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378611	2025-12-03 19:55:30.722308	\N	\N	0	0	28
282	16	19	2025-12-11	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378615	2025-12-03 19:55:30.72231	\N	\N	0	0	28
283	16	19	2025-12-13	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378619	2025-12-03 19:55:30.722312	\N	\N	0	0	28
284	16	19	2025-12-15	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378623	2025-12-03 19:55:30.722314	\N	\N	0	0	28
285	16	19	2025-12-17	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378627	2025-12-03 19:55:30.722316	\N	\N	0	0	28
286	16	19	2025-12-19	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378631	2025-12-03 19:55:30.722318	\N	\N	0	0	28
287	16	19	2025-12-21	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378635	2025-12-03 19:55:30.72232	\N	\N	0	0	28
288	16	19	2025-12-23	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378639	2025-12-03 19:55:30.722322	\N	\N	0	0	28
289	16	19	2025-12-25	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378644	2025-12-03 19:55:30.722323	\N	\N	0	0	28
290	16	19	2025-12-27	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378648	2025-12-03 19:55:30.722325	\N	\N	0	0	28
291	16	19	2025-12-29	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378652	2025-12-03 19:55:30.722327	\N	\N	0	0	28
292	16	19	2025-12-31	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 18:55:03.378656	2025-12-03 19:55:30.722329	\N	\N	0	0	28
296	16	20	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994573	2025-12-03 19:55:30.722331	\N	\N	0	0	28
297	16	20	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994578	2025-12-03 19:55:30.722333	\N	\N	0	0	28
298	16	20	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994582	2025-12-03 19:55:30.722335	\N	\N	0	0	28
299	16	20	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994586	2025-12-03 19:55:30.722337	\N	\N	0	0	28
300	16	20	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.99459	2025-12-03 19:55:30.722339	\N	\N	0	0	28
301	16	20	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994594	2025-12-03 19:55:30.722341	\N	\N	0	0	28
302	16	20	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994598	2025-12-03 19:55:30.722343	\N	\N	0	0	28
303	16	20	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994603	2025-12-03 19:55:30.722345	\N	\N	0	0	28
304	16	20	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994607	2025-12-03 19:55:30.722347	\N	\N	0	0	28
305	16	20	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994611	2025-12-03 19:55:30.722349	\N	\N	0	0	28
306	16	20	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994615	2025-12-03 19:55:30.722351	\N	\N	0	0	28
324	16	21	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286356	2025-12-02 19:26:35.286362	\N	\N	0	0	\N
325	16	21	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286365	2025-12-02 19:26:35.286367	\N	\N	0	0	\N
326	16	21	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286369	2025-12-02 19:26:35.286371	\N	\N	0	0	\N
355	16	22	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380696	2025-12-02 19:33:59.380701	\N	\N	0	0	\N
356	16	22	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380704	2025-12-02 19:33:59.380706	\N	\N	0	0	\N
357	16	22	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380708	2025-12-02 19:33:59.38071	\N	\N	0	0	\N
386	16	23	2025-12-01	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499442	2025-12-02 19:35:09.499448	\N	\N	0	0	\N
387	16	23	2025-12-02	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499451	2025-12-02 19:35:09.499453	\N	\N	0	0	\N
388	16	23	2025-12-03	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499455	2025-12-02 19:35:09.499457	\N	\N	0	0	\N
417	16	24	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163051	2025-12-02 19:35:46.163056	\N	\N	0	0	\N
418	16	24	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163059	2025-12-02 19:35:46.163061	\N	\N	0	0	\N
419	16	24	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163063	2025-12-02 19:35:46.163065	\N	\N	0	0	\N
448	16	25	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573327	2025-12-02 19:37:40.573333	\N	\N	0	0	\N
449	16	25	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573335	2025-12-02 19:37:40.573337	\N	\N	0	0	\N
450	16	25	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.57334	2025-12-02 19:37:40.573341	\N	\N	0	0	\N
479	16	26	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718585	2025-12-02 19:38:13.71859	\N	\N	0	0	\N
480	16	26	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718593	2025-12-02 19:38:13.718595	\N	\N	0	0	\N
481	16	26	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718598	2025-12-02 19:38:13.718599	\N	\N	0	0	\N
1008	16	43	2025-12-03	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213733	2025-12-03 19:02:22.345495	\N	\N	0	0	\N
474	16	25	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.57344	2025-12-03 19:56:02.190319	\N	\N	0	0	28
475	16	25	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573445	2025-12-03 19:56:02.190321	\N	\N	0	0	28
541	16	28	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:39:05.616059	2025-12-02 19:39:05.616065	\N	\N	0	0	\N
542	16	28	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:39:05.616068	2025-12-02 19:39:05.61607	\N	\N	0	0	\N
543	16	28	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:39:05.616072	2025-12-02 19:39:05.616074	\N	\N	0	0	\N
476	16	25	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573449	2025-12-03 19:56:02.190323	\N	\N	0	0	28
477	16	25	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573453	2025-12-03 19:56:02.190325	\N	\N	0	0	28
1737	16	67	2025-12-04	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180206	2025-12-03 19:03:07.129818	\N	\N	0	0	\N
1738	16	67	2025-12-05	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.18021	2025-12-03 19:03:07.510046	\N	\N	0	0	\N
1739	16	67	2025-12-06	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180214	2025-12-03 19:03:07.885587	\N	\N	0	0	\N
1740	16	67	2025-12-07	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180218	2025-12-03 19:03:08.261297	\N	\N	0	0	\N
1741	16	67	2025-12-08	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180222	2025-12-03 19:03:08.638932	\N	\N	0	0	\N
1742	16	67	2025-12-09	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180226	2025-12-03 19:03:09.014984	\N	\N	0	0	\N
1743	16	67	2025-12-10	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.18023	2025-12-03 19:03:09.391406	\N	\N	0	0	\N
1744	16	67	2025-12-11	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180235	2025-12-03 19:03:09.767734	\N	\N	0	0	\N
1745	16	67	2025-12-12	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180239	2025-12-03 19:03:10.144554	\N	\N	0	0	\N
1746	16	67	2025-12-13	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180243	2025-12-03 19:03:10.520476	\N	\N	0	0	\N
1747	16	67	2025-12-14	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180247	2025-12-03 19:03:10.897226	\N	\N	0	0	\N
1748	16	67	2025-12-15	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180251	2025-12-03 19:03:11.273476	\N	\N	0	0	\N
1749	16	67	2025-12-16	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180255	2025-12-03 19:03:11.650538	\N	\N	0	0	\N
1750	16	67	2025-12-17	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180259	2025-12-03 19:03:12.026228	\N	\N	0	0	\N
1751	16	67	2025-12-18	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180263	2025-12-03 19:03:12.402014	\N	\N	0	0	\N
1752	16	67	2025-12-19	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180267	2025-12-03 19:03:12.777447	\N	\N	0	0	\N
1753	16	67	2025-12-20	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.18027	2025-12-03 19:03:13.153378	\N	\N	0	0	\N
1754	16	67	2025-12-21	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180274	2025-12-03 19:03:13.52922	\N	\N	0	0	\N
1755	16	67	2025-12-22	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180278	2025-12-03 19:03:13.905587	\N	\N	0	0	\N
1756	16	67	2025-12-23	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180282	2025-12-03 19:03:14.281383	\N	\N	0	0	\N
1757	16	67	2025-12-24	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180286	2025-12-03 19:03:14.657592	\N	\N	0	0	\N
1758	16	67	2025-12-25	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.18029	2025-12-03 19:03:15.033282	\N	\N	0	0	\N
1759	16	67	2025-12-26	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180294	2025-12-03 19:03:15.408716	\N	\N	0	0	\N
1760	16	67	2025-12-27	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180298	2025-12-03 19:03:15.785197	\N	\N	0	0	\N
1761	16	67	2025-12-28	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180302	2025-12-03 19:03:16.162233	\N	\N	0	0	\N
1762	16	67	2025-12-29	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180306	2025-12-03 19:03:16.537783	\N	\N	0	0	\N
1763	16	67	2025-12-30	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180309	2025-12-03 19:03:16.913299	\N	\N	0	0	\N
1764	16	67	2025-12-31	0.00	80.00	0.00	paused	t	opted out	\N	2025-12-03 18:58:05.180313	2025-12-03 19:03:17.288717	\N	\N	0	0	\N
1036	16	43	2025-12-31	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213845	2025-12-03 19:56:56.20305	\N	\N	0	0	28
2457	16	34	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337058	2025-12-03 19:57:56.546759	\N	\N	0	0	28
2458	16	34	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337067	2025-12-03 19:57:56.546765	\N	\N	0	0	28
2459	16	34	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337072	2025-12-03 19:57:56.546768	\N	\N	0	0	28
2460	16	34	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337076	2025-12-03 19:57:56.54677	\N	\N	0	0	28
2461	16	34	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.33708	2025-12-03 19:57:56.546772	\N	\N	0	0	28
2462	16	34	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337084	2025-12-03 19:57:56.546774	\N	\N	0	0	28
2463	16	34	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337089	2025-12-03 19:57:56.546776	\N	\N	0	0	28
2464	16	34	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337093	2025-12-03 19:57:56.546778	\N	\N	0	0	28
2465	16	34	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337097	2025-12-03 19:57:56.54678	\N	\N	0	0	28
2466	16	34	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337101	2025-12-03 19:57:56.546782	\N	\N	0	0	28
2467	16	34	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337105	2025-12-03 19:57:56.546784	\N	\N	0	0	28
2468	16	34	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.33711	2025-12-03 19:57:56.546786	\N	\N	0	0	28
2469	16	34	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337114	2025-12-03 19:57:56.546788	\N	\N	0	0	28
2470	16	34	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337118	2025-12-03 19:57:56.54679	\N	\N	0	0	28
2471	16	34	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337122	2025-12-03 19:57:56.546792	\N	\N	0	0	28
2472	16	34	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337126	2025-12-03 19:57:56.546794	\N	\N	0	0	28
2473	16	34	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.33713	2025-12-03 19:57:56.546796	\N	\N	0	0	28
2474	16	34	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337134	2025-12-03 19:57:56.546798	\N	\N	0	0	28
2475	16	34	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337138	2025-12-03 19:57:56.5468	\N	\N	0	0	28
2476	16	34	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337143	2025-12-03 19:57:56.546802	\N	\N	0	0	28
13	11	7	2025-12-04	0.00	80.00	0.00	paused	t	out	\N	2025-11-22 19:50:04.716028	2025-12-02 19:40:39.614795	\N	\N	0	0	21
665	16	32	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832169	2025-12-03 18:57:25.832174	\N	\N	0	0	\N
666	16	32	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832177	2025-12-03 18:57:25.832179	\N	\N	0	0	\N
667	16	32	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832182	2025-12-03 18:57:25.832184	\N	\N	0	0	\N
696	16	33	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:27.008727	2025-12-03 18:57:27.008732	\N	\N	0	0	\N
697	16	33	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:27.008735	2025-12-03 18:57:27.008736	\N	\N	0	0	\N
698	16	33	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:27.008739	2025-12-03 18:57:27.008741	\N	\N	0	0	\N
727	16	34	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:28.150403	2025-12-03 18:57:28.150409	\N	\N	0	0	\N
728	16	34	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:28.150412	2025-12-03 18:57:28.150414	\N	\N	0	0	\N
729	16	34	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:28.150416	2025-12-03 18:57:28.150418	\N	\N	0	0	\N
758	16	35	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288358	2025-12-03 18:57:29.288364	\N	\N	0	0	\N
759	16	35	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288367	2025-12-03 18:57:29.288369	\N	\N	0	0	\N
760	16	35	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288372	2025-12-03 18:57:29.288373	\N	\N	0	0	\N
761	16	35	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288376	2025-12-03 19:56:22.119169	\N	\N	0	0	28
762	16	35	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.28838	2025-12-03 19:56:22.119175	\N	\N	0	0	28
763	16	35	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288384	2025-12-03 19:56:22.119177	\N	\N	0	0	28
764	16	35	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288388	2025-12-03 19:56:22.119179	\N	\N	0	0	28
765	16	35	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288393	2025-12-03 19:56:22.119181	\N	\N	0	0	28
766	16	35	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288397	2025-12-03 19:56:22.119184	\N	\N	0	0	28
767	16	35	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288401	2025-12-03 19:56:22.119186	\N	\N	0	0	28
768	16	35	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288405	2025-12-03 19:56:22.119188	\N	\N	0	0	28
769	16	35	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.28841	2025-12-03 19:56:22.11919	\N	\N	0	0	28
770	16	35	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288414	2025-12-03 19:56:22.119192	\N	\N	0	0	28
771	16	35	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288418	2025-12-03 19:56:22.119194	\N	\N	0	0	28
772	16	35	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288422	2025-12-03 19:56:22.119196	\N	\N	0	0	28
789	16	36	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:30.426336	2025-12-03 18:57:30.426341	\N	\N	0	0	\N
790	16	36	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:30.426344	2025-12-03 18:57:30.426346	\N	\N	0	0	\N
791	16	36	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:30.426349	2025-12-03 18:57:30.426351	\N	\N	0	0	\N
820	16	37	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:31.565325	2025-12-03 18:57:31.56533	\N	\N	0	0	\N
821	16	37	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:31.565333	2025-12-03 18:57:31.565335	\N	\N	0	0	\N
822	16	37	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:31.565338	2025-12-03 18:57:31.56534	\N	\N	0	0	\N
773	16	35	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288426	2025-12-03 19:56:22.119198	\N	\N	0	0	28
774	16	35	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.28843	2025-12-03 19:56:22.1192	\N	\N	0	0	28
775	16	35	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288434	2025-12-03 19:56:22.119202	\N	\N	0	0	28
776	16	35	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288438	2025-12-03 19:56:22.119204	\N	\N	0	0	28
777	16	35	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288442	2025-12-03 19:56:22.119206	\N	\N	0	0	28
778	16	35	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288447	2025-12-03 19:56:22.119208	\N	\N	0	0	28
779	16	35	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288451	2025-12-03 19:56:22.11921	\N	\N	0	0	28
780	16	35	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288455	2025-12-03 19:56:22.119212	\N	\N	0	0	28
781	16	35	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288459	2025-12-03 19:56:22.119214	\N	\N	0	0	28
782	16	35	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288463	2025-12-03 19:56:22.119216	\N	\N	0	0	28
783	16	35	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288467	2025-12-03 19:56:22.119218	\N	\N	0	0	28
784	16	35	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288471	2025-12-03 19:56:22.11922	\N	\N	0	0	28
785	16	35	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288476	2025-12-03 19:56:22.119222	\N	\N	0	0	28
786	16	35	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.28848	2025-12-03 19:56:22.119224	\N	\N	0	0	28
787	16	35	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288484	2025-12-03 19:56:22.119226	\N	\N	0	0	28
788	16	35	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:29.288488	2025-12-03 19:56:22.119228	\N	\N	0	0	28
851	16	38	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516652	2025-12-03 18:57:32.516657	\N	\N	0	0	\N
852	16	38	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.51666	2025-12-03 18:57:32.516662	\N	\N	0	0	\N
853	16	38	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516664	2025-12-03 18:57:32.516666	\N	\N	0	0	\N
882	16	39	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654723	2025-12-03 18:57:33.654729	\N	\N	0	0	\N
883	16	39	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654732	2025-12-03 18:57:33.654734	\N	\N	0	0	\N
884	16	39	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654736	2025-12-03 18:57:33.654738	\N	\N	0	0	\N
913	16	40	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795111	2025-12-03 18:57:34.795117	\N	\N	0	0	\N
914	16	40	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.79512	2025-12-03 18:57:34.795122	\N	\N	0	0	\N
915	16	40	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795124	2025-12-03 18:57:34.795126	\N	\N	0	0	\N
854	16	38	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516668	2025-12-03 19:56:27.894871	\N	\N	0	0	28
855	16	38	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516672	2025-12-03 19:56:27.894877	\N	\N	0	0	28
856	16	38	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516676	2025-12-03 19:56:27.894879	\N	\N	0	0	28
944	16	41	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:35.934326	2025-12-03 18:57:35.934331	\N	\N	0	0	\N
945	16	41	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:35.934334	2025-12-03 18:57:35.934336	\N	\N	0	0	\N
946	16	41	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:35.934338	2025-12-03 18:57:35.93434	\N	\N	0	0	\N
975	16	42	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073143	2025-12-03 18:57:37.073148	\N	\N	0	0	\N
976	16	42	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073151	2025-12-03 18:57:37.073153	\N	\N	0	0	\N
977	16	42	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073155	2025-12-03 18:57:37.073157	\N	\N	0	0	\N
923	16	40	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795156	2025-12-03 19:56:44.653295	\N	\N	0	0	28
924	16	40	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795159	2025-12-03 19:56:44.653297	\N	\N	0	0	28
925	16	40	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795163	2025-12-03 19:56:44.653299	\N	\N	0	0	28
926	16	40	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795167	2025-12-03 19:56:44.653301	\N	\N	0	0	28
927	16	40	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795171	2025-12-03 19:56:44.653303	\N	\N	0	0	28
928	16	40	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795175	2025-12-03 19:56:44.653305	\N	\N	0	0	28
929	16	40	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795179	2025-12-03 19:56:44.653307	\N	\N	0	0	28
930	16	40	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795183	2025-12-03 19:56:44.653309	\N	\N	0	0	28
931	16	40	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795187	2025-12-03 19:56:44.653311	\N	\N	0	0	28
932	16	40	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795191	2025-12-03 19:56:44.653313	\N	\N	0	0	28
933	16	40	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795195	2025-12-03 19:56:44.653315	\N	\N	0	0	28
934	16	40	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795199	2025-12-03 19:56:44.653317	\N	\N	0	0	28
935	16	40	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795203	2025-12-03 19:56:44.653319	\N	\N	0	0	28
936	16	40	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795207	2025-12-03 19:56:44.653321	\N	\N	0	0	28
937	16	40	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795211	2025-12-03 19:56:44.653323	\N	\N	0	0	28
938	16	40	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795215	2025-12-03 19:56:44.653325	\N	\N	0	0	28
939	16	40	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795218	2025-12-03 19:56:44.653327	\N	\N	0	0	28
940	16	40	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795222	2025-12-03 19:56:44.653329	\N	\N	0	0	28
941	16	40	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795226	2025-12-03 19:56:44.653331	\N	\N	0	0	28
942	16	40	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.79523	2025-12-03 19:56:44.653333	\N	\N	0	0	28
943	16	40	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795234	2025-12-03 19:56:44.653334	\N	\N	0	0	28
978	16	42	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073159	2025-12-03 19:56:50.431041	\N	\N	0	0	28
979	16	42	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073163	2025-12-03 19:56:50.431046	\N	\N	0	0	28
980	16	42	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073167	2025-12-03 19:56:50.431048	\N	\N	0	0	28
981	16	42	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073171	2025-12-03 19:56:50.43105	\N	\N	0	0	28
1006	16	43	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:38.213721	2025-12-03 18:57:38.213726	\N	\N	0	0	\N
1007	16	43	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:38.213729	2025-12-03 18:57:38.213731	\N	\N	0	0	\N
1037	16	44	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350887	2025-12-03 18:57:39.350892	\N	\N	0	0	\N
1038	16	44	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350895	2025-12-03 18:57:39.350896	\N	\N	0	0	\N
1039	16	44	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350899	2025-12-03 18:57:39.3509	\N	\N	0	0	\N
1068	16	45	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.48683	2025-12-03 18:57:40.486835	\N	\N	0	0	\N
1069	16	45	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486838	2025-12-03 18:57:40.48684	\N	\N	0	0	\N
1070	16	45	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486842	2025-12-03 18:57:40.486844	\N	\N	0	0	\N
998	16	42	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073241	2025-12-03 19:56:50.431082	\N	\N	0	0	28
999	16	42	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073245	2025-12-03 19:56:50.431084	\N	\N	0	0	28
1000	16	42	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073249	2025-12-03 19:56:50.431086	\N	\N	0	0	28
1001	16	42	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073253	2025-12-03 19:56:50.431088	\N	\N	0	0	28
1002	16	42	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073257	2025-12-03 19:56:50.43109	\N	\N	0	0	28
1003	16	42	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073261	2025-12-03 19:56:50.431092	\N	\N	0	0	28
1004	16	42	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073266	2025-12-03 19:56:50.431094	\N	\N	0	0	28
1005	16	42	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.07327	2025-12-03 19:56:50.431096	\N	\N	0	0	28
1040	16	44	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350903	2025-12-03 19:57:01.983269	\N	\N	0	0	28
1041	16	44	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350907	2025-12-03 19:57:01.983274	\N	\N	0	0	28
1042	16	44	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350911	2025-12-03 19:57:01.983276	\N	\N	0	0	28
1043	16	44	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350915	2025-12-03 19:57:01.983278	\N	\N	0	0	28
1044	16	44	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350919	2025-12-03 19:57:01.98328	\N	\N	0	0	28
1045	16	44	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350923	2025-12-03 19:57:01.983282	\N	\N	0	0	28
1046	16	44	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350927	2025-12-03 19:57:01.983284	\N	\N	0	0	28
1047	16	44	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350931	2025-12-03 19:57:01.983286	\N	\N	0	0	28
1048	16	44	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350934	2025-12-03 19:57:01.983288	\N	\N	0	0	28
1049	16	44	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350938	2025-12-03 19:57:01.98329	\N	\N	0	0	28
1050	16	44	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350942	2025-12-03 19:57:01.983292	\N	\N	0	0	28
1051	16	44	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350946	2025-12-03 19:57:01.983294	\N	\N	0	0	28
1052	16	44	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.35095	2025-12-03 19:57:01.983296	\N	\N	0	0	28
1053	16	44	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350954	2025-12-03 19:57:01.983298	\N	\N	0	0	28
1054	16	44	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350958	2025-12-03 19:57:01.9833	\N	\N	0	0	28
1055	16	44	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350962	2025-12-03 19:57:01.983302	\N	\N	0	0	28
1056	16	44	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350965	2025-12-03 19:57:01.983304	\N	\N	0	0	28
1057	16	44	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350969	2025-12-03 19:57:01.983306	\N	\N	0	0	28
1102	16	46	2025-12-04	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624103	2025-12-03 19:59:05.138161	\N	\N	0	0	28
1103	16	46	2025-12-05	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624107	2025-12-03 19:59:05.138168	\N	\N	0	0	28
1104	16	46	2025-12-06	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624111	2025-12-03 19:59:05.13817	\N	\N	0	0	28
1105	16	46	2025-12-07	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624115	2025-12-03 19:59:05.138172	\N	\N	0	0	28
1106	16	46	2025-12-08	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624119	2025-12-03 19:59:05.138174	\N	\N	0	0	28
1107	16	46	2025-12-09	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624123	2025-12-03 19:59:05.138175	\N	\N	0	0	28
1108	16	46	2025-12-10	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624127	2025-12-03 19:59:05.138177	\N	\N	0	0	28
1109	16	46	2025-12-11	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624131	2025-12-03 19:59:05.138179	\N	\N	0	0	28
1110	16	46	2025-12-12	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624135	2025-12-03 19:59:05.138181	\N	\N	0	0	28
1111	16	46	2025-12-13	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624138	2025-12-03 19:59:05.138183	\N	\N	0	0	28
1112	16	46	2025-12-14	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624142	2025-12-03 19:59:05.138185	\N	\N	0	0	28
1113	16	46	2025-12-15	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624146	2025-12-03 19:59:05.138187	\N	\N	0	0	28
1114	16	46	2025-12-16	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.62415	2025-12-03 19:59:05.138189	\N	\N	0	0	28
1115	16	46	2025-12-17	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624154	2025-12-03 19:59:05.138191	\N	\N	0	0	28
1116	16	46	2025-12-18	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624158	2025-12-03 19:59:05.138194	\N	\N	0	0	28
1117	16	46	2025-12-19	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624162	2025-12-03 19:59:05.138196	\N	\N	0	0	28
1118	16	46	2025-12-20	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624166	2025-12-03 19:59:05.138198	\N	\N	0	0	28
1119	16	46	2025-12-21	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.62417	2025-12-03 19:59:05.1382	\N	\N	0	0	28
1120	16	46	2025-12-22	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624173	2025-12-03 19:59:05.138202	\N	\N	0	0	28
1121	16	46	2025-12-23	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624177	2025-12-03 19:59:05.138204	\N	\N	0	0	28
1122	16	46	2025-12-24	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624181	2025-12-03 19:59:05.138205	\N	\N	0	0	28
1123	16	46	2025-12-25	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624185	2025-12-03 19:59:05.138207	\N	\N	0	0	28
1124	16	46	2025-12-26	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624189	2025-12-03 19:59:05.138209	\N	\N	0	0	28
1125	16	46	2025-12-27	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624193	2025-12-03 19:59:05.138211	\N	\N	0	0	28
1099	16	46	2025-12-01	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624088	2025-12-03 18:57:41.624093	\N	\N	0	0	\N
1100	16	46	2025-12-02	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624095	2025-12-03 18:57:41.624097	\N	\N	0	0	\N
1101	16	46	2025-12-03	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:57:41.624099	2025-12-03 18:57:41.624101	\N	\N	0	0	\N
1130	16	47	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.75957	2025-12-03 18:57:42.759575	\N	\N	0	0	\N
1131	16	47	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759578	2025-12-03 18:57:42.75958	\N	\N	0	0	\N
1132	16	47	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:42.759582	2025-12-03 18:57:42.759584	\N	\N	0	0	\N
1161	16	48	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897184	2025-12-03 18:57:43.897189	\N	\N	0	0	\N
1162	16	48	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897192	2025-12-03 18:57:43.897194	\N	\N	0	0	\N
1163	16	48	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:43.897196	2025-12-03 18:57:43.897198	\N	\N	0	0	\N
1192	16	49	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046642	2025-12-03 18:57:45.046647	\N	\N	0	0	\N
1193	16	49	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.04665	2025-12-03 18:57:45.046652	\N	\N	0	0	\N
1194	16	49	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:45.046654	2025-12-03 18:57:45.046656	\N	\N	0	0	\N
1257	16	51	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332967	2025-12-03 19:59:28.237458	\N	\N	0	0	28
1258	16	51	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332971	2025-12-03 19:59:28.237464	\N	\N	0	0	28
1259	16	51	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332975	2025-12-03 19:59:28.237467	\N	\N	0	0	28
1260	16	51	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332979	2025-12-03 19:59:28.237469	\N	\N	0	0	28
1261	16	51	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332983	2025-12-03 19:59:28.237471	\N	\N	0	0	28
1262	16	51	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332987	2025-12-03 19:59:28.237473	\N	\N	0	0	28
1263	16	51	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332991	2025-12-03 19:59:28.237475	\N	\N	0	0	28
1264	16	51	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332995	2025-12-03 19:59:28.237477	\N	\N	0	0	28
1265	16	51	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332999	2025-12-03 19:59:28.237479	\N	\N	0	0	28
1266	16	51	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333003	2025-12-03 19:59:28.237481	\N	\N	0	0	28
1267	16	51	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333007	2025-12-03 19:59:28.237483	\N	\N	0	0	28
1268	16	51	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333011	2025-12-03 19:59:28.237485	\N	\N	0	0	28
1269	16	51	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333014	2025-12-03 19:59:28.237487	\N	\N	0	0	28
1270	16	51	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333018	2025-12-03 19:59:28.237489	\N	\N	0	0	28
1271	16	51	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333022	2025-12-03 19:59:28.237491	\N	\N	0	0	28
1272	16	51	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333026	2025-12-03 19:59:28.237493	\N	\N	0	0	28
1273	16	51	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333031	2025-12-03 19:59:28.237495	\N	\N	0	0	28
1274	16	51	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333035	2025-12-03 19:59:28.237497	\N	\N	0	0	28
1275	16	51	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333039	2025-12-03 19:59:28.237499	\N	\N	0	0	28
1276	16	51	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333043	2025-12-03 19:59:28.237501	\N	\N	0	0	28
1277	16	51	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333047	2025-12-03 19:59:28.237503	\N	\N	0	0	28
1278	16	51	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333051	2025-12-03 19:59:28.237505	\N	\N	0	0	28
1279	16	51	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333055	2025-12-03 19:59:28.237507	\N	\N	0	0	28
1280	16	51	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333059	2025-12-03 19:59:28.237509	\N	\N	0	0	28
1281	16	51	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333063	2025-12-03 19:59:28.237511	\N	\N	0	0	28
1282	16	51	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333067	2025-12-03 19:59:28.237513	\N	\N	0	0	28
1283	16	51	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333071	2025-12-03 19:59:28.237515	\N	\N	0	0	28
1284	16	51	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.333075	2025-12-03 19:59:28.237517	\N	\N	0	0	28
1254	16	51	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332952	2025-12-03 18:57:47.332957	\N	\N	0	0	\N
1255	16	51	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332959	2025-12-03 18:57:47.332961	\N	\N	0	0	\N
1256	16	51	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:47.332964	2025-12-03 18:57:47.332965	\N	\N	0	0	\N
1285	16	52	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468756	2025-12-03 18:57:48.468762	\N	\N	0	0	\N
1286	16	52	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468764	2025-12-03 18:57:48.468766	\N	\N	0	0	\N
1287	16	52	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468769	2025-12-03 18:57:48.46877	\N	\N	0	0	\N
1288	16	52	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468773	2025-12-03 18:57:48.468774	\N	\N	0	0	\N
1289	16	52	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468777	2025-12-03 18:57:48.468778	\N	\N	0	0	\N
1290	16	52	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468781	2025-12-03 18:57:48.468782	\N	\N	0	0	\N
1291	16	52	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468785	2025-12-03 18:57:48.468786	\N	\N	0	0	\N
1292	16	52	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468789	2025-12-03 18:57:48.46879	\N	\N	0	0	\N
1293	16	52	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468793	2025-12-03 18:57:48.468794	\N	\N	0	0	\N
1294	16	52	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468797	2025-12-03 18:57:48.468798	\N	\N	0	0	\N
1295	16	52	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468801	2025-12-03 18:57:48.468803	\N	\N	0	0	\N
1296	16	52	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468805	2025-12-03 18:57:48.468807	\N	\N	0	0	\N
1297	16	52	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468809	2025-12-03 18:57:48.468811	\N	\N	0	0	\N
1298	16	52	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468814	2025-12-03 18:57:48.468816	\N	\N	0	0	\N
1299	16	52	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:48.468818	2025-12-03 18:57:48.46882	\N	\N	0	0	\N
1300	16	53	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417797	2025-12-03 18:57:49.417802	\N	\N	0	0	\N
1301	16	53	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417805	2025-12-03 18:57:49.417807	\N	\N	0	0	\N
1302	16	53	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417809	2025-12-03 18:57:49.417811	\N	\N	0	0	\N
1303	16	53	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417813	2025-12-03 18:57:49.417815	\N	\N	0	0	\N
1304	16	53	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417817	2025-12-03 18:57:49.417819	\N	\N	0	0	\N
1305	16	53	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417821	2025-12-03 18:57:49.417823	\N	\N	0	0	\N
1306	16	53	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417825	2025-12-03 18:57:49.417827	\N	\N	0	0	\N
1307	16	53	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417829	2025-12-03 18:57:49.417831	\N	\N	0	0	\N
1308	16	53	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417833	2025-12-03 18:57:49.417835	\N	\N	0	0	\N
1309	16	53	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417837	2025-12-03 18:57:49.417839	\N	\N	0	0	\N
1310	16	53	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417841	2025-12-03 18:57:49.417842	\N	\N	0	0	\N
1311	16	53	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417845	2025-12-03 18:57:49.417846	\N	\N	0	0	\N
1312	16	53	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417848	2025-12-03 18:57:49.41785	\N	\N	0	0	\N
1313	16	53	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417852	2025-12-03 18:57:49.417854	\N	\N	0	0	\N
1314	16	53	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417857	2025-12-03 18:57:49.417859	\N	\N	0	0	\N
1315	16	53	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417861	2025-12-03 18:57:49.417863	\N	\N	0	0	\N
1316	16	53	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417865	2025-12-03 18:57:49.417867	\N	\N	0	0	\N
1317	16	53	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417869	2025-12-03 18:57:49.417871	\N	\N	0	0	\N
1318	16	53	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417873	2025-12-03 18:57:49.417874	\N	\N	0	0	\N
1319	16	53	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417877	2025-12-03 18:57:49.417879	\N	\N	0	0	\N
1320	16	53	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417881	2025-12-03 18:57:49.417883	\N	\N	0	0	\N
1321	16	53	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417885	2025-12-03 18:57:49.417887	\N	\N	0	0	\N
1322	16	53	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417889	2025-12-03 18:57:49.417891	\N	\N	0	0	\N
1323	16	53	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417893	2025-12-03 18:57:49.417895	\N	\N	0	0	\N
1324	16	53	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417897	2025-12-03 18:57:49.417899	\N	\N	0	0	\N
1325	16	53	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417901	2025-12-03 18:57:49.417903	\N	\N	0	0	\N
1326	16	53	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417905	2025-12-03 18:57:49.417907	\N	\N	0	0	\N
1327	16	53	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417909	2025-12-03 18:57:49.417911	\N	\N	0	0	\N
1328	16	53	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417913	2025-12-03 18:57:49.417915	\N	\N	0	0	\N
1329	16	53	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.417917	2025-12-03 18:57:49.417919	\N	\N	0	0	\N
1330	16	53	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:49.41794	2025-12-03 18:57:49.417942	\N	\N	0	0	\N
1331	16	54	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557014	2025-12-03 18:57:50.557019	\N	\N	0	0	\N
1332	16	54	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557022	2025-12-03 18:57:50.557024	\N	\N	0	0	\N
1333	16	54	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557026	2025-12-03 18:57:50.557028	\N	\N	0	0	\N
1334	16	54	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.55703	2025-12-03 18:57:50.557032	\N	\N	0	0	\N
1335	16	54	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557034	2025-12-03 18:57:50.557036	\N	\N	0	0	\N
1336	16	54	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557038	2025-12-03 18:57:50.557039	\N	\N	0	0	\N
1337	16	54	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557042	2025-12-03 18:57:50.557043	\N	\N	0	0	\N
1338	16	54	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557046	2025-12-03 18:57:50.557047	\N	\N	0	0	\N
1339	16	54	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557049	2025-12-03 18:57:50.557051	\N	\N	0	0	\N
1340	16	54	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557053	2025-12-03 18:57:50.557055	\N	\N	0	0	\N
1341	16	54	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557057	2025-12-03 18:57:50.557059	\N	\N	0	0	\N
1342	16	54	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557061	2025-12-03 18:57:50.557063	\N	\N	0	0	\N
1343	16	54	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557065	2025-12-03 18:57:50.557067	\N	\N	0	0	\N
1344	16	54	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557069	2025-12-03 18:57:50.557071	\N	\N	0	0	\N
1345	16	54	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557073	2025-12-03 18:57:50.557074	\N	\N	0	0	\N
1346	16	54	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557077	2025-12-03 18:57:50.557079	\N	\N	0	0	\N
1347	16	54	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557081	2025-12-03 18:57:50.557083	\N	\N	0	0	\N
1348	16	54	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557085	2025-12-03 18:57:50.557087	\N	\N	0	0	\N
1349	16	54	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557089	2025-12-03 18:57:50.55709	\N	\N	0	0	\N
1350	16	54	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557093	2025-12-03 18:57:50.557094	\N	\N	0	0	\N
1351	16	54	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557097	2025-12-03 18:57:50.557098	\N	\N	0	0	\N
1352	16	54	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.5571	2025-12-03 18:57:50.557102	\N	\N	0	0	\N
1353	16	54	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557104	2025-12-03 18:57:50.557106	\N	\N	0	0	\N
1354	16	54	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557108	2025-12-03 18:57:50.55711	\N	\N	0	0	\N
1355	16	54	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557112	2025-12-03 18:57:50.557114	\N	\N	0	0	\N
1356	16	54	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557116	2025-12-03 18:57:50.557118	\N	\N	0	0	\N
1357	16	54	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.55712	2025-12-03 18:57:50.557122	\N	\N	0	0	\N
1358	16	54	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557124	2025-12-03 18:57:50.557126	\N	\N	0	0	\N
1359	16	54	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557128	2025-12-03 18:57:50.55713	\N	\N	0	0	\N
1360	16	54	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557132	2025-12-03 18:57:50.557133	\N	\N	0	0	\N
1361	16	54	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:50.557136	2025-12-03 18:57:50.557137	\N	\N	0	0	\N
1362	16	55	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698348	2025-12-03 18:57:51.698353	\N	\N	0	0	\N
1363	16	55	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698356	2025-12-03 18:57:51.698357	\N	\N	0	0	\N
1364	16	55	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.69836	2025-12-03 18:57:51.698361	\N	\N	0	0	\N
1365	16	55	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698364	2025-12-03 18:57:51.698365	\N	\N	0	0	\N
1366	16	55	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698368	2025-12-03 18:57:51.698369	\N	\N	0	0	\N
1367	16	55	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698372	2025-12-03 18:57:51.698374	\N	\N	0	0	\N
1368	16	55	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698376	2025-12-03 18:57:51.698378	\N	\N	0	0	\N
1369	16	55	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.69838	2025-12-03 18:57:51.698382	\N	\N	0	0	\N
1370	16	55	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698384	2025-12-03 18:57:51.698386	\N	\N	0	0	\N
1371	16	55	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698388	2025-12-03 18:57:51.69839	\N	\N	0	0	\N
1372	16	55	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698392	2025-12-03 18:57:51.698394	\N	\N	0	0	\N
1373	16	55	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698396	2025-12-03 18:57:51.698398	\N	\N	0	0	\N
1374	16	55	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.6984	2025-12-03 18:57:51.698402	\N	\N	0	0	\N
1375	16	55	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698404	2025-12-03 18:57:51.698406	\N	\N	0	0	\N
1376	16	55	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698408	2025-12-03 18:57:51.69841	\N	\N	0	0	\N
1377	16	55	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698412	2025-12-03 18:57:51.698414	\N	\N	0	0	\N
1378	16	55	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698416	2025-12-03 18:57:51.698417	\N	\N	0	0	\N
1379	16	55	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.69842	2025-12-03 18:57:51.698421	\N	\N	0	0	\N
1380	16	55	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698424	2025-12-03 18:57:51.698425	\N	\N	0	0	\N
1381	16	55	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698428	2025-12-03 18:57:51.69843	\N	\N	0	0	\N
1382	16	55	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698432	2025-12-03 18:57:51.698434	\N	\N	0	0	\N
1383	16	55	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698436	2025-12-03 18:57:51.698438	\N	\N	0	0	\N
1384	16	55	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.69844	2025-12-03 18:57:51.698442	\N	\N	0	0	\N
1385	16	55	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698444	2025-12-03 18:57:51.698446	\N	\N	0	0	\N
1386	16	55	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698448	2025-12-03 18:57:51.69845	\N	\N	0	0	\N
1387	16	55	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698452	2025-12-03 18:57:51.698454	\N	\N	0	0	\N
1388	16	55	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698456	2025-12-03 18:57:51.698458	\N	\N	0	0	\N
1389	16	55	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.69846	2025-12-03 18:57:51.698462	\N	\N	0	0	\N
1390	16	55	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698464	2025-12-03 18:57:51.698466	\N	\N	0	0	\N
1391	16	55	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698468	2025-12-03 18:57:51.69847	\N	\N	0	0	\N
1392	16	55	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:51.698472	2025-12-03 18:57:51.698474	\N	\N	0	0	\N
1393	16	56	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838713	2025-12-03 18:57:52.838719	\N	\N	0	0	\N
1394	16	56	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838721	2025-12-03 18:57:52.838723	\N	\N	0	0	\N
1395	16	56	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838725	2025-12-03 18:57:52.838727	\N	\N	0	0	\N
1396	16	56	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838729	2025-12-03 18:57:52.838731	\N	\N	0	0	\N
1397	16	56	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838733	2025-12-03 18:57:52.838735	\N	\N	0	0	\N
1398	16	56	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838737	2025-12-03 18:57:52.838739	\N	\N	0	0	\N
1399	16	56	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838741	2025-12-03 18:57:52.838743	\N	\N	0	0	\N
1400	16	56	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838745	2025-12-03 18:57:52.838747	\N	\N	0	0	\N
1401	16	56	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838749	2025-12-03 18:57:52.838751	\N	\N	0	0	\N
1402	16	56	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838753	2025-12-03 18:57:52.838755	\N	\N	0	0	\N
1403	16	56	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838757	2025-12-03 18:57:52.838759	\N	\N	0	0	\N
1404	16	56	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838761	2025-12-03 18:57:52.838763	\N	\N	0	0	\N
1405	16	56	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838765	2025-12-03 18:57:52.838767	\N	\N	0	0	\N
1406	16	56	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838769	2025-12-03 18:57:52.838771	\N	\N	0	0	\N
1407	16	56	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838773	2025-12-03 18:57:52.838775	\N	\N	0	0	\N
1408	16	56	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838777	2025-12-03 18:57:52.838779	\N	\N	0	0	\N
1409	16	56	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838781	2025-12-03 18:57:52.838783	\N	\N	0	0	\N
1410	16	56	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838785	2025-12-03 18:57:52.838787	\N	\N	0	0	\N
1411	16	56	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838789	2025-12-03 18:57:52.838791	\N	\N	0	0	\N
1412	16	56	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838793	2025-12-03 18:57:52.838795	\N	\N	0	0	\N
1413	16	56	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838797	2025-12-03 18:57:52.838799	\N	\N	0	0	\N
1414	16	56	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838801	2025-12-03 18:57:52.838803	\N	\N	0	0	\N
1415	16	56	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838805	2025-12-03 18:57:52.838807	\N	\N	0	0	\N
1416	16	56	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838809	2025-12-03 18:57:52.83881	\N	\N	0	0	\N
1417	16	56	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838813	2025-12-03 18:57:52.838814	\N	\N	0	0	\N
1418	16	56	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838816	2025-12-03 18:57:52.838818	\N	\N	0	0	\N
1419	16	56	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.83882	2025-12-03 18:57:52.838822	\N	\N	0	0	\N
1420	16	56	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838824	2025-12-03 18:57:52.838826	\N	\N	0	0	\N
1421	16	56	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838828	2025-12-03 18:57:52.83883	\N	\N	0	0	\N
1422	16	56	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838832	2025-12-03 18:57:52.838833	\N	\N	0	0	\N
1423	16	56	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:52.838836	2025-12-03 18:57:52.838837	\N	\N	0	0	\N
1424	16	57	2025-12-01	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976218	2025-12-03 18:57:53.976224	\N	\N	0	0	\N
1425	16	57	2025-12-02	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976227	2025-12-03 18:57:53.976229	\N	\N	0	0	\N
1426	16	57	2025-12-03	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976231	2025-12-03 18:57:53.976233	\N	\N	0	0	\N
1427	16	57	2025-12-04	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976235	2025-12-03 18:57:53.976237	\N	\N	0	0	\N
1428	16	57	2025-12-05	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976239	2025-12-03 18:57:53.976241	\N	\N	0	0	\N
1429	16	57	2025-12-06	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976243	2025-12-03 18:57:53.976244	\N	\N	0	0	\N
1430	16	57	2025-12-07	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976247	2025-12-03 18:57:53.976248	\N	\N	0	0	\N
1431	16	57	2025-12-08	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976251	2025-12-03 18:57:53.976252	\N	\N	0	0	\N
1432	16	57	2025-12-09	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976254	2025-12-03 18:57:53.976256	\N	\N	0	0	\N
1433	16	57	2025-12-10	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976258	2025-12-03 18:57:53.97626	\N	\N	0	0	\N
1434	16	57	2025-12-11	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976262	2025-12-03 18:57:53.976264	\N	\N	0	0	\N
1435	16	57	2025-12-12	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976266	2025-12-03 18:57:53.976268	\N	\N	0	0	\N
1436	16	57	2025-12-13	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.97627	2025-12-03 18:57:53.976272	\N	\N	0	0	\N
1437	16	57	2025-12-14	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976274	2025-12-03 18:57:53.976276	\N	\N	0	0	\N
1438	16	57	2025-12-15	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976278	2025-12-03 18:57:53.97628	\N	\N	0	0	\N
1439	16	57	2025-12-16	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976282	2025-12-03 18:57:53.976283	\N	\N	0	0	\N
1440	16	57	2025-12-17	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976286	2025-12-03 18:57:53.976287	\N	\N	0	0	\N
1441	16	57	2025-12-18	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.97629	2025-12-03 18:57:53.976291	\N	\N	0	0	\N
1442	16	57	2025-12-19	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976294	2025-12-03 18:57:53.976295	\N	\N	0	0	\N
1443	16	57	2025-12-20	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976297	2025-12-03 18:57:53.976299	\N	\N	0	0	\N
1444	16	57	2025-12-21	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976301	2025-12-03 18:57:53.976303	\N	\N	0	0	\N
1445	16	57	2025-12-22	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976305	2025-12-03 18:57:53.976307	\N	\N	0	0	\N
1446	16	57	2025-12-23	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976309	2025-12-03 18:57:53.97631	\N	\N	0	0	\N
1447	16	57	2025-12-24	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976313	2025-12-03 18:57:53.976314	\N	\N	0	0	\N
1448	16	57	2025-12-25	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976316	2025-12-03 18:57:53.976318	\N	\N	0	0	\N
1449	16	57	2025-12-26	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.97632	2025-12-03 18:57:53.976322	\N	\N	0	0	\N
1450	16	57	2025-12-27	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976324	2025-12-03 18:57:53.976326	\N	\N	0	0	\N
1451	16	57	2025-12-28	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976328	2025-12-03 18:57:53.976329	\N	\N	0	0	\N
1452	16	57	2025-12-29	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976332	2025-12-03 18:57:53.976333	\N	\N	0	0	\N
1453	16	57	2025-12-30	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976335	2025-12-03 18:57:53.976337	\N	\N	0	0	\N
1454	16	57	2025-12-31	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:57:53.976339	2025-12-03 18:57:53.976341	\N	\N	0	0	\N
1455	16	58	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118257	2025-12-03 18:57:55.118262	\N	\N	0	0	\N
1456	16	58	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118265	2025-12-03 18:57:55.118267	\N	\N	0	0	\N
1457	16	58	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118269	2025-12-03 18:57:55.118271	\N	\N	0	0	\N
1458	16	58	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118273	2025-12-03 18:57:55.118274	\N	\N	0	0	\N
1459	16	58	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118277	2025-12-03 18:57:55.118278	\N	\N	0	0	\N
1460	16	58	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.11828	2025-12-03 18:57:55.118282	\N	\N	0	0	\N
1461	16	58	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118285	2025-12-03 18:57:55.118286	\N	\N	0	0	\N
1462	16	58	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118289	2025-12-03 18:57:55.11829	\N	\N	0	0	\N
1463	16	58	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118293	2025-12-03 18:57:55.118294	\N	\N	0	0	\N
1464	16	58	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118297	2025-12-03 18:57:55.118298	\N	\N	0	0	\N
1465	16	58	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118301	2025-12-03 18:57:55.118302	\N	\N	0	0	\N
1466	16	58	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118304	2025-12-03 18:57:55.118306	\N	\N	0	0	\N
1467	16	58	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118308	2025-12-03 18:57:55.11831	\N	\N	0	0	\N
1468	16	58	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118312	2025-12-03 18:57:55.118314	\N	\N	0	0	\N
1469	16	58	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118316	2025-12-03 18:57:55.118318	\N	\N	0	0	\N
1470	16	58	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.11832	2025-12-03 18:57:55.118322	\N	\N	0	0	\N
1471	16	58	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118324	2025-12-03 18:57:55.118326	\N	\N	0	0	\N
1472	16	58	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118328	2025-12-03 18:57:55.118329	\N	\N	0	0	\N
1473	16	58	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118332	2025-12-03 18:57:55.118333	\N	\N	0	0	\N
1474	16	58	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118335	2025-12-03 18:57:55.118337	\N	\N	0	0	\N
1475	16	58	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118339	2025-12-03 18:57:55.118341	\N	\N	0	0	\N
1476	16	58	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118343	2025-12-03 18:57:55.118345	\N	\N	0	0	\N
1477	16	58	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118347	2025-12-03 18:57:55.118349	\N	\N	0	0	\N
1478	16	58	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118351	2025-12-03 18:57:55.118353	\N	\N	0	0	\N
1479	16	58	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118355	2025-12-03 18:57:55.118356	\N	\N	0	0	\N
1480	16	58	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118359	2025-12-03 18:57:55.11836	\N	\N	0	0	\N
1481	16	58	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118363	2025-12-03 18:57:55.118364	\N	\N	0	0	\N
1482	16	58	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118366	2025-12-03 18:57:55.118368	\N	\N	0	0	\N
1483	16	58	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.11837	2025-12-03 18:57:55.118372	\N	\N	0	0	\N
1484	16	58	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118374	2025-12-03 18:57:55.118376	\N	\N	0	0	\N
1485	16	58	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:55.118378	2025-12-03 18:57:55.11838	\N	\N	0	0	\N
1486	16	59	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255414	2025-12-03 18:57:56.255419	\N	\N	0	0	\N
1487	16	59	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255422	2025-12-03 18:57:56.255424	\N	\N	0	0	\N
1488	16	59	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255426	2025-12-03 18:57:56.255428	\N	\N	0	0	\N
1489	16	59	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.25543	2025-12-03 18:57:56.255432	\N	\N	0	0	\N
1490	16	59	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255434	2025-12-03 18:57:56.255436	\N	\N	0	0	\N
1491	16	59	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255438	2025-12-03 18:57:56.25544	\N	\N	0	0	\N
1492	16	59	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255443	2025-12-03 18:57:56.255444	\N	\N	0	0	\N
1493	16	59	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255447	2025-12-03 18:57:56.255448	\N	\N	0	0	\N
1494	16	59	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255451	2025-12-03 18:57:56.255452	\N	\N	0	0	\N
1495	16	59	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255454	2025-12-03 18:57:56.255456	\N	\N	0	0	\N
1496	16	59	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255458	2025-12-03 18:57:56.25546	\N	\N	0	0	\N
1497	16	59	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255462	2025-12-03 18:57:56.255464	\N	\N	0	0	\N
1498	16	59	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255466	2025-12-03 18:57:56.255468	\N	\N	0	0	\N
1499	16	59	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.25547	2025-12-03 18:57:56.255472	\N	\N	0	0	\N
1500	16	59	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255474	2025-12-03 18:57:56.255476	\N	\N	0	0	\N
1501	16	59	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255478	2025-12-03 18:57:56.25548	\N	\N	0	0	\N
1502	16	59	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255482	2025-12-03 18:57:56.255484	\N	\N	0	0	\N
1503	16	59	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255486	2025-12-03 18:57:56.255488	\N	\N	0	0	\N
1504	16	59	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.25549	2025-12-03 18:57:56.255492	\N	\N	0	0	\N
1505	16	59	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255494	2025-12-03 18:57:56.255495	\N	\N	0	0	\N
1506	16	59	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255498	2025-12-03 18:57:56.255499	\N	\N	0	0	\N
1507	16	59	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255502	2025-12-03 18:57:56.255503	\N	\N	0	0	\N
1508	16	59	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255505	2025-12-03 18:57:56.255507	\N	\N	0	0	\N
1509	16	59	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255509	2025-12-03 18:57:56.255511	\N	\N	0	0	\N
1510	16	59	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255513	2025-12-03 18:57:56.255515	\N	\N	0	0	\N
1511	16	59	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255517	2025-12-03 18:57:56.255519	\N	\N	0	0	\N
1512	16	59	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255521	2025-12-03 18:57:56.255523	\N	\N	0	0	\N
1513	16	59	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255525	2025-12-03 18:57:56.255527	\N	\N	0	0	\N
1514	16	59	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255529	2025-12-03 18:57:56.25553	\N	\N	0	0	\N
1515	16	59	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255533	2025-12-03 18:57:56.255534	\N	\N	0	0	\N
1516	16	59	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:56.255536	2025-12-03 18:57:56.255538	\N	\N	0	0	\N
1548	16	61	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.53807	2025-12-03 18:57:58.538076	\N	\N	0	0	\N
1549	16	61	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538078	2025-12-03 18:57:58.53808	\N	\N	0	0	\N
1550	16	61	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538082	2025-12-03 18:57:58.538084	\N	\N	0	0	\N
1551	16	61	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538086	2025-12-03 18:57:58.538088	\N	\N	0	0	\N
1552	16	61	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538091	2025-12-03 18:57:58.538092	\N	\N	0	0	\N
1553	16	61	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538094	2025-12-03 18:57:58.538096	\N	\N	0	0	\N
1554	16	61	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538099	2025-12-03 18:57:58.538101	\N	\N	0	0	\N
1555	16	61	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538103	2025-12-03 18:57:58.538105	\N	\N	0	0	\N
1556	16	61	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538107	2025-12-03 18:57:58.538109	\N	\N	0	0	\N
1557	16	61	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538111	2025-12-03 18:57:58.538113	\N	\N	0	0	\N
1558	16	61	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538115	2025-12-03 18:57:58.538117	\N	\N	0	0	\N
1559	16	61	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538119	2025-12-03 18:57:58.538121	\N	\N	0	0	\N
1560	16	61	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538124	2025-12-03 18:57:58.538126	\N	\N	0	0	\N
1561	16	61	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538128	2025-12-03 18:57:58.53813	\N	\N	0	0	\N
1562	16	61	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538132	2025-12-03 18:57:58.538134	\N	\N	0	0	\N
1563	16	61	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538136	2025-12-03 18:57:58.538138	\N	\N	0	0	\N
1564	16	61	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.53814	2025-12-03 18:57:58.538142	\N	\N	0	0	\N
1565	16	61	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538144	2025-12-03 18:57:58.538146	\N	\N	0	0	\N
1566	16	61	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538148	2025-12-03 18:57:58.53815	\N	\N	0	0	\N
1567	16	61	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538152	2025-12-03 18:57:58.538154	\N	\N	0	0	\N
1568	16	61	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538156	2025-12-03 18:57:58.538158	\N	\N	0	0	\N
1569	16	61	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.53816	2025-12-03 18:57:58.538162	\N	\N	0	0	\N
1570	16	61	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538164	2025-12-03 18:57:58.538166	\N	\N	0	0	\N
1571	16	61	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538168	2025-12-03 18:57:58.53817	\N	\N	0	0	\N
1572	16	61	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538172	2025-12-03 18:57:58.538174	\N	\N	0	0	\N
1573	16	61	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538176	2025-12-03 18:57:58.538178	\N	\N	0	0	\N
1574	16	61	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.53818	2025-12-03 18:57:58.538182	\N	\N	0	0	\N
1575	16	61	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538185	2025-12-03 18:57:58.538186	\N	\N	0	0	\N
1576	16	61	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538189	2025-12-03 18:57:58.53819	\N	\N	0	0	\N
1577	16	61	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538192	2025-12-03 18:57:58.538194	\N	\N	0	0	\N
1578	16	61	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:58.538197	2025-12-03 18:57:58.538198	\N	\N	0	0	\N
1579	16	62	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676572	2025-12-03 18:57:59.676577	\N	\N	0	0	\N
1580	16	62	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.67658	2025-12-03 18:57:59.676582	\N	\N	0	0	\N
1581	16	62	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676584	2025-12-03 18:57:59.676586	\N	\N	0	0	\N
1582	16	62	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676588	2025-12-03 18:57:59.67659	\N	\N	0	0	\N
1583	16	62	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676592	2025-12-03 18:57:59.676594	\N	\N	0	0	\N
1584	16	62	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676596	2025-12-03 18:57:59.676598	\N	\N	0	0	\N
1585	16	62	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.6766	2025-12-03 18:57:59.676602	\N	\N	0	0	\N
1586	16	62	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676604	2025-12-03 18:57:59.676606	\N	\N	0	0	\N
1587	16	62	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676608	2025-12-03 18:57:59.67661	\N	\N	0	0	\N
1588	16	62	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676612	2025-12-03 18:57:59.676614	\N	\N	0	0	\N
1589	16	62	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676616	2025-12-03 18:57:59.676618	\N	\N	0	0	\N
1590	16	62	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.67662	2025-12-03 18:57:59.676621	\N	\N	0	0	\N
1591	16	62	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676624	2025-12-03 18:57:59.676625	\N	\N	0	0	\N
1592	16	62	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676628	2025-12-03 18:57:59.676629	\N	\N	0	0	\N
1593	16	62	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676632	2025-12-03 18:57:59.676633	\N	\N	0	0	\N
1594	16	62	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676636	2025-12-03 18:57:59.676637	\N	\N	0	0	\N
1595	16	62	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.67664	2025-12-03 18:57:59.676641	\N	\N	0	0	\N
1596	16	62	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676643	2025-12-03 18:57:59.676645	\N	\N	0	0	\N
1597	16	62	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676647	2025-12-03 18:57:59.676649	\N	\N	0	0	\N
1598	16	62	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676651	2025-12-03 18:57:59.676653	\N	\N	0	0	\N
1599	16	62	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676655	2025-12-03 18:57:59.676657	\N	\N	0	0	\N
1600	16	62	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676659	2025-12-03 18:57:59.676661	\N	\N	0	0	\N
1601	16	62	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676663	2025-12-03 18:57:59.676665	\N	\N	0	0	\N
1602	16	62	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676667	2025-12-03 18:57:59.676669	\N	\N	0	0	\N
1603	16	62	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676671	2025-12-03 18:57:59.676673	\N	\N	0	0	\N
1604	16	62	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676675	2025-12-03 18:57:59.676676	\N	\N	0	0	\N
1605	16	62	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676679	2025-12-03 18:57:59.67668	\N	\N	0	0	\N
1606	16	62	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676683	2025-12-03 18:57:59.676684	\N	\N	0	0	\N
1607	16	62	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676687	2025-12-03 18:57:59.676688	\N	\N	0	0	\N
1608	16	62	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.67669	2025-12-03 18:57:59.676692	\N	\N	0	0	\N
1609	16	62	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:59.676694	2025-12-03 18:57:59.676696	\N	\N	0	0	\N
1610	16	63	2025-12-01	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628139	2025-12-03 18:58:00.628144	\N	\N	0	0	\N
1611	16	63	2025-12-02	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628147	2025-12-03 18:58:00.628149	\N	\N	0	0	\N
1612	16	63	2025-12-03	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628151	2025-12-03 18:58:00.628153	\N	\N	0	0	\N
1613	16	63	2025-12-04	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628155	2025-12-03 18:58:00.628157	\N	\N	0	0	\N
1614	16	63	2025-12-05	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628159	2025-12-03 18:58:00.628161	\N	\N	0	0	\N
1615	16	63	2025-12-06	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628163	2025-12-03 18:58:00.628165	\N	\N	0	0	\N
1616	16	63	2025-12-07	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628168	2025-12-03 18:58:00.62817	\N	\N	0	0	\N
1617	16	63	2025-12-08	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628172	2025-12-03 18:58:00.628174	\N	\N	0	0	\N
1618	16	63	2025-12-09	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628176	2025-12-03 18:58:00.628178	\N	\N	0	0	\N
1619	16	63	2025-12-10	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.62818	2025-12-03 18:58:00.628182	\N	\N	0	0	\N
1620	16	63	2025-12-11	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628184	2025-12-03 18:58:00.628186	\N	\N	0	0	\N
1621	16	63	2025-12-12	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628188	2025-12-03 18:58:00.62819	\N	\N	0	0	\N
1622	16	63	2025-12-13	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628192	2025-12-03 18:58:00.628194	\N	\N	0	0	\N
1623	16	63	2025-12-14	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628196	2025-12-03 18:58:00.628198	\N	\N	0	0	\N
1624	16	63	2025-12-15	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.6282	2025-12-03 18:58:00.628202	\N	\N	0	0	\N
1625	16	63	2025-12-16	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628204	2025-12-03 18:58:00.628206	\N	\N	0	0	\N
1626	16	63	2025-12-17	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628208	2025-12-03 18:58:00.62821	\N	\N	0	0	\N
1627	16	63	2025-12-18	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628212	2025-12-03 18:58:00.628214	\N	\N	0	0	\N
1628	16	63	2025-12-19	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628216	2025-12-03 18:58:00.628218	\N	\N	0	0	\N
1629	16	63	2025-12-20	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.62822	2025-12-03 18:58:00.628222	\N	\N	0	0	\N
1630	16	63	2025-12-21	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628224	2025-12-03 18:58:00.628226	\N	\N	0	0	\N
1631	16	63	2025-12-22	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628228	2025-12-03 18:58:00.62823	\N	\N	0	0	\N
1632	16	63	2025-12-23	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628232	2025-12-03 18:58:00.628234	\N	\N	0	0	\N
1633	16	63	2025-12-24	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628236	2025-12-03 18:58:00.628238	\N	\N	0	0	\N
1634	16	63	2025-12-25	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.62824	2025-12-03 18:58:00.628242	\N	\N	0	0	\N
1635	16	63	2025-12-26	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628244	2025-12-03 18:58:00.628246	\N	\N	0	0	\N
1636	16	63	2025-12-27	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628248	2025-12-03 18:58:00.62825	\N	\N	0	0	\N
1637	16	63	2025-12-28	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628252	2025-12-03 18:58:00.628254	\N	\N	0	0	\N
1638	16	63	2025-12-29	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628256	2025-12-03 18:58:00.628257	\N	\N	0	0	\N
1639	16	63	2025-12-30	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.62826	2025-12-03 18:58:00.628261	\N	\N	0	0	\N
1640	16	63	2025-12-31	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:00.628264	2025-12-03 18:58:00.628265	\N	\N	0	0	\N
1641	16	64	2025-12-01	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765516	2025-12-03 18:58:01.765521	\N	\N	0	0	\N
1642	16	64	2025-12-02	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765524	2025-12-03 18:58:01.765526	\N	\N	0	0	\N
1643	16	64	2025-12-03	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765528	2025-12-03 18:58:01.76553	\N	\N	0	0	\N
1644	16	64	2025-12-04	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765532	2025-12-03 18:58:01.765534	\N	\N	0	0	\N
1645	16	64	2025-12-05	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765536	2025-12-03 18:58:01.765538	\N	\N	0	0	\N
1646	16	64	2025-12-06	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.76554	2025-12-03 18:58:01.765542	\N	\N	0	0	\N
1647	16	64	2025-12-07	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765544	2025-12-03 18:58:01.765546	\N	\N	0	0	\N
1648	16	64	2025-12-08	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765548	2025-12-03 18:58:01.76555	\N	\N	0	0	\N
1649	16	64	2025-12-09	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765552	2025-12-03 18:58:01.765554	\N	\N	0	0	\N
1650	16	64	2025-12-10	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765557	2025-12-03 18:58:01.765559	\N	\N	0	0	\N
1651	16	64	2025-12-11	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765561	2025-12-03 18:58:01.765563	\N	\N	0	0	\N
1652	16	64	2025-12-12	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765565	2025-12-03 18:58:01.765567	\N	\N	0	0	\N
1653	16	64	2025-12-13	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765569	2025-12-03 18:58:01.765571	\N	\N	0	0	\N
1654	16	64	2025-12-14	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765573	2025-12-03 18:58:01.765575	\N	\N	0	0	\N
1655	16	64	2025-12-15	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765577	2025-12-03 18:58:01.765579	\N	\N	0	0	\N
1656	16	64	2025-12-16	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765581	2025-12-03 18:58:01.765582	\N	\N	0	0	\N
1657	16	64	2025-12-17	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765585	2025-12-03 18:58:01.765586	\N	\N	0	0	\N
1658	16	64	2025-12-18	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765589	2025-12-03 18:58:01.76559	\N	\N	0	0	\N
1659	16	64	2025-12-19	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765593	2025-12-03 18:58:01.765594	\N	\N	0	0	\N
1660	16	64	2025-12-20	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765597	2025-12-03 18:58:01.765598	\N	\N	0	0	\N
1661	16	64	2025-12-21	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765601	2025-12-03 18:58:01.765602	\N	\N	0	0	\N
1662	16	64	2025-12-22	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765604	2025-12-03 18:58:01.765606	\N	\N	0	0	\N
1663	16	64	2025-12-23	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765608	2025-12-03 18:58:01.76561	\N	\N	0	0	\N
1664	16	64	2025-12-24	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765612	2025-12-03 18:58:01.765614	\N	\N	0	0	\N
1665	16	64	2025-12-25	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765616	2025-12-03 18:58:01.765618	\N	\N	0	0	\N
1666	16	64	2025-12-26	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.76562	2025-12-03 18:58:01.765622	\N	\N	0	0	\N
1667	16	64	2025-12-27	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765624	2025-12-03 18:58:01.765626	\N	\N	0	0	\N
1668	16	64	2025-12-28	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765628	2025-12-03 18:58:01.765629	\N	\N	0	0	\N
1669	16	64	2025-12-29	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765632	2025-12-03 18:58:01.765633	\N	\N	0	0	\N
1670	16	64	2025-12-30	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.765636	2025-12-03 18:58:01.765637	\N	\N	0	0	\N
1671	16	64	2025-12-31	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:01.76564	2025-12-03 18:58:01.765641	\N	\N	0	0	\N
1672	16	65	2025-12-01	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903924	2025-12-03 18:58:02.903929	\N	\N	0	0	\N
1673	16	65	2025-12-02	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903932	2025-12-03 18:58:02.903934	\N	\N	0	0	\N
1674	16	65	2025-12-03	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903936	2025-12-03 18:58:02.903937	\N	\N	0	0	\N
1675	16	65	2025-12-04	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.90394	2025-12-03 18:58:02.903941	\N	\N	0	0	\N
1676	16	65	2025-12-05	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903944	2025-12-03 18:58:02.903945	\N	\N	0	0	\N
1677	16	65	2025-12-06	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903947	2025-12-03 18:58:02.903949	\N	\N	0	0	\N
1678	16	65	2025-12-07	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903951	2025-12-03 18:58:02.903953	\N	\N	0	0	\N
1679	16	65	2025-12-08	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903955	2025-12-03 18:58:02.903957	\N	\N	0	0	\N
1680	16	65	2025-12-09	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903959	2025-12-03 18:58:02.903961	\N	\N	0	0	\N
1681	16	65	2025-12-10	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903963	2025-12-03 18:58:02.903965	\N	\N	0	0	\N
1682	16	65	2025-12-11	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903967	2025-12-03 18:58:02.903968	\N	\N	0	0	\N
1683	16	65	2025-12-12	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903971	2025-12-03 18:58:02.903972	\N	\N	0	0	\N
1684	16	65	2025-12-13	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903974	2025-12-03 18:58:02.903976	\N	\N	0	0	\N
1685	16	65	2025-12-14	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903978	2025-12-03 18:58:02.90398	\N	\N	0	0	\N
1686	16	65	2025-12-15	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903982	2025-12-03 18:58:02.903984	\N	\N	0	0	\N
1687	16	65	2025-12-16	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903986	2025-12-03 18:58:02.903988	\N	\N	0	0	\N
1688	16	65	2025-12-17	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.90399	2025-12-03 18:58:02.903992	\N	\N	0	0	\N
1689	16	65	2025-12-18	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903994	2025-12-03 18:58:02.903996	\N	\N	0	0	\N
1690	16	65	2025-12-19	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.903998	2025-12-03 18:58:02.903999	\N	\N	0	0	\N
1691	16	65	2025-12-20	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904002	2025-12-03 18:58:02.904004	\N	\N	0	0	\N
1692	16	65	2025-12-21	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904006	2025-12-03 18:58:02.904008	\N	\N	0	0	\N
1693	16	65	2025-12-22	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.90401	2025-12-03 18:58:02.904012	\N	\N	0	0	\N
1694	16	65	2025-12-23	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904014	2025-12-03 18:58:02.904016	\N	\N	0	0	\N
1695	16	65	2025-12-24	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904018	2025-12-03 18:58:02.904019	\N	\N	0	0	\N
1696	16	65	2025-12-25	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904022	2025-12-03 18:58:02.904023	\N	\N	0	0	\N
1697	16	65	2025-12-26	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904025	2025-12-03 18:58:02.904027	\N	\N	0	0	\N
1698	16	65	2025-12-27	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904029	2025-12-03 18:58:02.904031	\N	\N	0	0	\N
1699	16	65	2025-12-28	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904033	2025-12-03 18:58:02.904035	\N	\N	0	0	\N
1700	16	65	2025-12-29	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904037	2025-12-03 18:58:02.904039	\N	\N	0	0	\N
1701	16	65	2025-12-30	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904041	2025-12-03 18:58:02.904043	\N	\N	0	0	\N
1702	16	65	2025-12-31	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:02.904045	2025-12-03 18:58:02.904047	\N	\N	0	0	\N
1703	16	66	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043037	2025-12-03 18:58:04.043042	\N	\N	0	0	\N
1704	16	66	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043045	2025-12-03 18:58:04.043047	\N	\N	0	0	\N
1705	16	66	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043049	2025-12-03 18:58:04.043051	\N	\N	0	0	\N
1706	16	66	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043053	2025-12-03 18:58:04.043055	\N	\N	0	0	\N
1707	16	66	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043057	2025-12-03 18:58:04.043059	\N	\N	0	0	\N
1708	16	66	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043061	2025-12-03 18:58:04.043063	\N	\N	0	0	\N
1709	16	66	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043065	2025-12-03 18:58:04.043067	\N	\N	0	0	\N
1710	16	66	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043069	2025-12-03 18:58:04.043071	\N	\N	0	0	\N
1711	16	66	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043073	2025-12-03 18:58:04.043075	\N	\N	0	0	\N
1712	16	66	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043077	2025-12-03 18:58:04.043079	\N	\N	0	0	\N
1713	16	66	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043081	2025-12-03 18:58:04.043083	\N	\N	0	0	\N
1714	16	66	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043085	2025-12-03 18:58:04.043087	\N	\N	0	0	\N
1715	16	66	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043089	2025-12-03 18:58:04.043091	\N	\N	0	0	\N
1716	16	66	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043093	2025-12-03 18:58:04.043095	\N	\N	0	0	\N
1717	16	66	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043097	2025-12-03 18:58:04.043099	\N	\N	0	0	\N
1718	16	66	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043102	2025-12-03 18:58:04.043104	\N	\N	0	0	\N
1719	16	66	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043106	2025-12-03 18:58:04.043108	\N	\N	0	0	\N
1720	16	66	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.04311	2025-12-03 18:58:04.043112	\N	\N	0	0	\N
1721	16	66	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043114	2025-12-03 18:58:04.043116	\N	\N	0	0	\N
1722	16	66	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043118	2025-12-03 18:58:04.04312	\N	\N	0	0	\N
1723	16	66	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043123	2025-12-03 18:58:04.043124	\N	\N	0	0	\N
1724	16	66	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043127	2025-12-03 18:58:04.043128	\N	\N	0	0	\N
1725	16	66	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043131	2025-12-03 18:58:04.043132	\N	\N	0	0	\N
1726	16	66	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043135	2025-12-03 18:58:04.043136	\N	\N	0	0	\N
1727	16	66	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043139	2025-12-03 18:58:04.043141	\N	\N	0	0	\N
1728	16	66	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043143	2025-12-03 18:58:04.043145	\N	\N	0	0	\N
1729	16	66	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043147	2025-12-03 18:58:04.043149	\N	\N	0	0	\N
1730	16	66	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043151	2025-12-03 18:58:04.043153	\N	\N	0	0	\N
1731	16	66	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043155	2025-12-03 18:58:04.043157	\N	\N	0	0	\N
1732	16	66	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043159	2025-12-03 18:58:04.043161	\N	\N	0	0	\N
1733	16	66	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:04.043163	2025-12-03 18:58:04.043165	\N	\N	0	0	\N
1734	16	67	2025-12-01	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:58:05.180189	2025-12-03 18:58:05.180195	\N	\N	0	0	\N
1735	16	67	2025-12-02	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:58:05.180198	2025-12-03 18:58:05.1802	\N	\N	0	0	\N
1736	16	67	2025-12-03	1.50	80.00	120.00	delivered	f	\N	\N	2025-12-03 18:58:05.180202	2025-12-03 18:58:05.180204	\N	\N	0	0	\N
1765	16	68	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316884	2025-12-03 18:58:06.316889	\N	\N	0	0	\N
1766	16	68	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316892	2025-12-03 18:58:06.316894	\N	\N	0	0	\N
1767	16	68	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316896	2025-12-03 18:58:06.316898	\N	\N	0	0	\N
1768	16	68	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.3169	2025-12-03 18:58:06.316902	\N	\N	0	0	\N
1769	16	68	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316904	2025-12-03 18:58:06.316906	\N	\N	0	0	\N
1770	16	68	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316909	2025-12-03 18:58:06.31691	\N	\N	0	0	\N
1771	16	68	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316913	2025-12-03 18:58:06.316915	\N	\N	0	0	\N
1772	16	68	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316917	2025-12-03 18:58:06.316919	\N	\N	0	0	\N
1773	16	68	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316921	2025-12-03 18:58:06.316923	\N	\N	0	0	\N
1774	16	68	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316925	2025-12-03 18:58:06.316927	\N	\N	0	0	\N
1775	16	68	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316929	2025-12-03 18:58:06.316931	\N	\N	0	0	\N
1776	16	68	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316933	2025-12-03 18:58:06.316935	\N	\N	0	0	\N
1777	16	68	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316937	2025-12-03 18:58:06.316939	\N	\N	0	0	\N
1778	16	68	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316941	2025-12-03 18:58:06.316943	\N	\N	0	0	\N
1779	16	68	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316945	2025-12-03 18:58:06.316947	\N	\N	0	0	\N
1780	16	68	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316949	2025-12-03 18:58:06.316951	\N	\N	0	0	\N
1781	16	68	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316953	2025-12-03 18:58:06.316955	\N	\N	0	0	\N
1782	16	68	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316957	2025-12-03 18:58:06.316959	\N	\N	0	0	\N
1783	16	68	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316961	2025-12-03 18:58:06.316962	\N	\N	0	0	\N
1784	16	68	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316965	2025-12-03 18:58:06.316967	\N	\N	0	0	\N
1785	16	68	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316969	2025-12-03 18:58:06.316971	\N	\N	0	0	\N
1786	16	68	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316973	2025-12-03 18:58:06.316975	\N	\N	0	0	\N
1787	16	68	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316977	2025-12-03 18:58:06.316978	\N	\N	0	0	\N
1788	16	68	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316981	2025-12-03 18:58:06.316982	\N	\N	0	0	\N
1789	16	68	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316985	2025-12-03 18:58:06.316986	\N	\N	0	0	\N
1790	16	68	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316989	2025-12-03 18:58:06.31699	\N	\N	0	0	\N
1791	16	68	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316993	2025-12-03 18:58:06.316994	\N	\N	0	0	\N
1792	16	68	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.316997	2025-12-03 18:58:06.316998	\N	\N	0	0	\N
1793	16	68	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.317001	2025-12-03 18:58:06.317002	\N	\N	0	0	\N
1794	16	68	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.317004	2025-12-03 18:58:06.317006	\N	\N	0	0	\N
1795	16	68	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:06.317008	2025-12-03 18:58:06.31701	\N	\N	0	0	\N
1796	16	69	2025-12-01	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454579	2025-12-03 18:58:07.454585	\N	\N	0	0	\N
1797	16	69	2025-12-02	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454587	2025-12-03 18:58:07.454589	\N	\N	0	0	\N
1798	16	69	2025-12-03	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454591	2025-12-03 18:58:07.454593	\N	\N	0	0	\N
1799	16	69	2025-12-04	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454595	2025-12-03 18:58:07.454597	\N	\N	0	0	\N
1800	16	69	2025-12-05	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454599	2025-12-03 18:58:07.454601	\N	\N	0	0	\N
1801	16	69	2025-12-06	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454603	2025-12-03 18:58:07.454605	\N	\N	0	0	\N
1802	16	69	2025-12-07	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454607	2025-12-03 18:58:07.454609	\N	\N	0	0	\N
1803	16	69	2025-12-08	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454611	2025-12-03 18:58:07.454613	\N	\N	0	0	\N
1804	16	69	2025-12-09	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454615	2025-12-03 18:58:07.454617	\N	\N	0	0	\N
1805	16	69	2025-12-10	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454619	2025-12-03 18:58:07.454621	\N	\N	0	0	\N
1806	16	69	2025-12-11	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454623	2025-12-03 18:58:07.454624	\N	\N	0	0	\N
1807	16	69	2025-12-12	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454627	2025-12-03 18:58:07.454628	\N	\N	0	0	\N
1808	16	69	2025-12-13	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454631	2025-12-03 18:58:07.454632	\N	\N	0	0	\N
1809	16	69	2025-12-14	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454634	2025-12-03 18:58:07.454636	\N	\N	0	0	\N
1810	16	69	2025-12-15	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454638	2025-12-03 18:58:07.45464	\N	\N	0	0	\N
1811	16	69	2025-12-16	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454642	2025-12-03 18:58:07.454644	\N	\N	0	0	\N
1812	16	69	2025-12-17	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454646	2025-12-03 18:58:07.454648	\N	\N	0	0	\N
1813	16	69	2025-12-18	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.45465	2025-12-03 18:58:07.454652	\N	\N	0	0	\N
1814	16	69	2025-12-19	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454654	2025-12-03 18:58:07.454656	\N	\N	0	0	\N
1815	16	69	2025-12-20	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454658	2025-12-03 18:58:07.45466	\N	\N	0	0	\N
1816	16	69	2025-12-21	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454662	2025-12-03 18:58:07.454664	\N	\N	0	0	\N
1817	16	69	2025-12-22	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454667	2025-12-03 18:58:07.454668	\N	\N	0	0	\N
1818	16	69	2025-12-23	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454671	2025-12-03 18:58:07.454672	\N	\N	0	0	\N
1819	16	69	2025-12-24	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454675	2025-12-03 18:58:07.454676	\N	\N	0	0	\N
1820	16	69	2025-12-25	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454679	2025-12-03 18:58:07.45468	\N	\N	0	0	\N
1821	16	69	2025-12-26	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454682	2025-12-03 18:58:07.454684	\N	\N	0	0	\N
1822	16	69	2025-12-27	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454686	2025-12-03 18:58:07.454688	\N	\N	0	0	\N
1823	16	69	2025-12-28	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.45469	2025-12-03 18:58:07.454692	\N	\N	0	0	\N
1824	16	69	2025-12-29	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454694	2025-12-03 18:58:07.454696	\N	\N	0	0	\N
1825	16	69	2025-12-30	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454698	2025-12-03 18:58:07.4547	\N	\N	0	0	\N
1826	16	69	2025-12-31	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 18:58:07.454702	2025-12-03 18:58:07.454704	\N	\N	0	0	\N
1827	16	70	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592877	2025-12-03 18:58:08.592881	\N	\N	0	0	\N
1828	16	70	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592884	2025-12-03 18:58:08.592886	\N	\N	0	0	\N
1829	16	70	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592888	2025-12-03 18:58:08.59289	\N	\N	0	0	\N
1830	16	70	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592893	2025-12-03 18:58:08.592894	\N	\N	0	0	\N
1831	16	70	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592897	2025-12-03 18:58:08.592898	\N	\N	0	0	\N
1832	16	70	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592901	2025-12-03 18:58:08.592902	\N	\N	0	0	\N
1833	16	70	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592905	2025-12-03 18:58:08.592907	\N	\N	0	0	\N
1834	16	70	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592909	2025-12-03 18:58:08.592911	\N	\N	0	0	\N
1835	16	70	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592913	2025-12-03 18:58:08.592915	\N	\N	0	0	\N
1836	16	70	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592917	2025-12-03 18:58:08.592919	\N	\N	0	0	\N
1837	16	70	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592921	2025-12-03 18:58:08.592923	\N	\N	0	0	\N
1838	16	70	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592925	2025-12-03 18:58:08.592927	\N	\N	0	0	\N
1839	16	70	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592929	2025-12-03 18:58:08.592931	\N	\N	0	0	\N
1840	16	70	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592933	2025-12-03 18:58:08.592935	\N	\N	0	0	\N
1841	16	70	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592937	2025-12-03 18:58:08.592939	\N	\N	0	0	\N
1842	16	70	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592941	2025-12-03 18:58:08.592943	\N	\N	0	0	\N
1843	16	70	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592945	2025-12-03 18:58:08.592947	\N	\N	0	0	\N
1844	16	70	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592949	2025-12-03 18:58:08.592951	\N	\N	0	0	\N
1845	16	70	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592953	2025-12-03 18:58:08.592955	\N	\N	0	0	\N
1846	16	70	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592958	2025-12-03 18:58:08.592959	\N	\N	0	0	\N
1847	16	70	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592961	2025-12-03 18:58:08.592963	\N	\N	0	0	\N
1848	16	70	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592966	2025-12-03 18:58:08.592967	\N	\N	0	0	\N
1849	16	70	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592969	2025-12-03 18:58:08.592971	\N	\N	0	0	\N
1850	16	70	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592973	2025-12-03 18:58:08.592975	\N	\N	0	0	\N
1851	16	70	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592977	2025-12-03 18:58:08.592979	\N	\N	0	0	\N
1852	16	70	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592981	2025-12-03 18:58:08.592983	\N	\N	0	0	\N
1853	16	70	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592985	2025-12-03 18:58:08.592987	\N	\N	0	0	\N
1854	16	70	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592989	2025-12-03 18:58:08.592991	\N	\N	0	0	\N
1855	16	70	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592993	2025-12-03 18:58:08.592995	\N	\N	0	0	\N
1856	16	70	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.592998	2025-12-03 18:58:08.592999	\N	\N	0	0	\N
1857	16	70	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:08.593002	2025-12-03 18:58:08.593003	\N	\N	0	0	\N
1858	16	71	2025-12-01	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728709	2025-12-03 18:58:09.728714	\N	\N	0	0	\N
1859	16	71	2025-12-02	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728717	2025-12-03 18:58:09.728718	\N	\N	0	0	\N
1860	16	71	2025-12-03	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728721	2025-12-03 18:58:09.728722	\N	\N	0	0	\N
1861	16	71	2025-12-04	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728725	2025-12-03 18:58:09.728726	\N	\N	0	0	\N
1862	16	71	2025-12-05	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728729	2025-12-03 18:58:09.72873	\N	\N	0	0	\N
1863	16	71	2025-12-06	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728733	2025-12-03 18:58:09.728734	\N	\N	0	0	\N
1864	16	71	2025-12-07	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728736	2025-12-03 18:58:09.728738	\N	\N	0	0	\N
1865	16	71	2025-12-08	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.72874	2025-12-03 18:58:09.728742	\N	\N	0	0	\N
1866	16	71	2025-12-09	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728744	2025-12-03 18:58:09.728746	\N	\N	0	0	\N
1867	16	71	2025-12-10	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728748	2025-12-03 18:58:09.72875	\N	\N	0	0	\N
1868	16	71	2025-12-11	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728752	2025-12-03 18:58:09.728754	\N	\N	0	0	\N
1869	16	71	2025-12-12	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728756	2025-12-03 18:58:09.728758	\N	\N	0	0	\N
1870	16	71	2025-12-13	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.72876	2025-12-03 18:58:09.728762	\N	\N	0	0	\N
1871	16	71	2025-12-14	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728764	2025-12-03 18:58:09.728766	\N	\N	0	0	\N
1872	16	71	2025-12-15	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728768	2025-12-03 18:58:09.728769	\N	\N	0	0	\N
1873	16	71	2025-12-16	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728772	2025-12-03 18:58:09.728773	\N	\N	0	0	\N
1874	16	71	2025-12-17	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728776	2025-12-03 18:58:09.728777	\N	\N	0	0	\N
1875	16	71	2025-12-18	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728779	2025-12-03 18:58:09.728781	\N	\N	0	0	\N
1876	16	71	2025-12-19	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728783	2025-12-03 18:58:09.728785	\N	\N	0	0	\N
1877	16	71	2025-12-20	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728787	2025-12-03 18:58:09.728789	\N	\N	0	0	\N
1878	16	71	2025-12-21	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728791	2025-12-03 18:58:09.728793	\N	\N	0	0	\N
1879	16	71	2025-12-22	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728795	2025-12-03 18:58:09.728797	\N	\N	0	0	\N
1880	16	71	2025-12-23	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728799	2025-12-03 18:58:09.728801	\N	\N	0	0	\N
1881	16	71	2025-12-24	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728804	2025-12-03 18:58:09.728805	\N	\N	0	0	\N
1882	16	71	2025-12-25	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728808	2025-12-03 18:58:09.728809	\N	\N	0	0	\N
1883	16	71	2025-12-26	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728812	2025-12-03 18:58:09.728814	\N	\N	0	0	\N
1884	16	71	2025-12-27	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728816	2025-12-03 18:58:09.728818	\N	\N	0	0	\N
1885	16	71	2025-12-28	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.72882	2025-12-03 18:58:09.728822	\N	\N	0	0	\N
1886	16	71	2025-12-29	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728824	2025-12-03 18:58:09.728826	\N	\N	0	0	\N
1887	16	71	2025-12-30	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728828	2025-12-03 18:58:09.72883	\N	\N	0	0	\N
1888	16	71	2025-12-31	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:09.728832	2025-12-03 18:58:09.728834	\N	\N	0	0	\N
1889	16	72	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865635	2025-12-03 18:58:10.865641	\N	\N	0	0	\N
1890	16	72	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865643	2025-12-03 18:58:10.865645	\N	\N	0	0	\N
1891	16	72	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865647	2025-12-03 18:58:10.865649	\N	\N	0	0	\N
1892	16	72	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865651	2025-12-03 18:58:10.865653	\N	\N	0	0	\N
1893	16	72	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865655	2025-12-03 18:58:10.865657	\N	\N	0	0	\N
1894	16	72	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865659	2025-12-03 18:58:10.86566	\N	\N	0	0	\N
1895	16	72	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865663	2025-12-03 18:58:10.865664	\N	\N	0	0	\N
1896	16	72	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865666	2025-12-03 18:58:10.865668	\N	\N	0	0	\N
1897	16	72	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.86567	2025-12-03 18:58:10.865672	\N	\N	0	0	\N
1898	16	72	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865675	2025-12-03 18:58:10.865676	\N	\N	0	0	\N
1899	16	72	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865679	2025-12-03 18:58:10.86568	\N	\N	0	0	\N
1900	16	72	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865683	2025-12-03 18:58:10.865684	\N	\N	0	0	\N
1901	16	72	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865687	2025-12-03 18:58:10.865688	\N	\N	0	0	\N
1902	16	72	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865691	2025-12-03 18:58:10.865692	\N	\N	0	0	\N
1903	16	72	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865695	2025-12-03 18:58:10.865696	\N	\N	0	0	\N
1904	16	72	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865699	2025-12-03 18:58:10.8657	\N	\N	0	0	\N
1905	16	72	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865703	2025-12-03 18:58:10.865704	\N	\N	0	0	\N
1906	16	72	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865706	2025-12-03 18:58:10.865708	\N	\N	0	0	\N
1907	16	72	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.86571	2025-12-03 18:58:10.865712	\N	\N	0	0	\N
1908	16	72	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865714	2025-12-03 18:58:10.865716	\N	\N	0	0	\N
1909	16	72	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865718	2025-12-03 18:58:10.86572	\N	\N	0	0	\N
1910	16	72	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865722	2025-12-03 18:58:10.865724	\N	\N	0	0	\N
1911	16	72	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865726	2025-12-03 18:58:10.865728	\N	\N	0	0	\N
1912	16	72	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.86573	2025-12-03 18:58:10.865732	\N	\N	0	0	\N
1913	16	72	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865734	2025-12-03 18:58:10.865736	\N	\N	0	0	\N
1914	16	72	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865738	2025-12-03 18:58:10.86574	\N	\N	0	0	\N
1915	16	72	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865742	2025-12-03 18:58:10.865744	\N	\N	0	0	\N
1916	16	72	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865746	2025-12-03 18:58:10.865748	\N	\N	0	0	\N
1917	16	72	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.86575	2025-12-03 18:58:10.865752	\N	\N	0	0	\N
1918	16	72	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865754	2025-12-03 18:58:10.865756	\N	\N	0	0	\N
1919	16	72	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:10.865758	2025-12-03 18:58:10.86576	\N	\N	0	0	\N
1920	16	73	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005429	2025-12-03 18:58:12.005434	\N	\N	0	0	\N
1921	16	73	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005437	2025-12-03 18:58:12.005439	\N	\N	0	0	\N
1922	16	73	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005441	2025-12-03 18:58:12.005443	\N	\N	0	0	\N
1923	16	73	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005445	2025-12-03 18:58:12.005447	\N	\N	0	0	\N
1924	16	73	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005449	2025-12-03 18:58:12.005451	\N	\N	0	0	\N
1925	16	73	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005453	2025-12-03 18:58:12.005455	\N	\N	0	0	\N
1926	16	73	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005457	2025-12-03 18:58:12.005458	\N	\N	0	0	\N
1927	16	73	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005461	2025-12-03 18:58:12.005462	\N	\N	0	0	\N
1928	16	73	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005465	2025-12-03 18:58:12.005466	\N	\N	0	0	\N
1929	16	73	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005468	2025-12-03 18:58:12.00547	\N	\N	0	0	\N
1930	16	73	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005472	2025-12-03 18:58:12.005474	\N	\N	0	0	\N
1931	16	73	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005476	2025-12-03 18:58:12.005478	\N	\N	0	0	\N
1932	16	73	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.00548	2025-12-03 18:58:12.005482	\N	\N	0	0	\N
1933	16	73	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005484	2025-12-03 18:58:12.005486	\N	\N	0	0	\N
1934	16	73	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005488	2025-12-03 18:58:12.005489	\N	\N	0	0	\N
1935	16	73	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005492	2025-12-03 18:58:12.005493	\N	\N	0	0	\N
1936	16	73	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005496	2025-12-03 18:58:12.005497	\N	\N	0	0	\N
1937	16	73	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005499	2025-12-03 18:58:12.005501	\N	\N	0	0	\N
1938	16	73	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005503	2025-12-03 18:58:12.005505	\N	\N	0	0	\N
1939	16	73	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005507	2025-12-03 18:58:12.005509	\N	\N	0	0	\N
1940	16	73	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005511	2025-12-03 18:58:12.005513	\N	\N	0	0	\N
1941	16	73	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005515	2025-12-03 18:58:12.005516	\N	\N	0	0	\N
1942	16	73	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005519	2025-12-03 18:58:12.00552	\N	\N	0	0	\N
1943	16	73	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005523	2025-12-03 18:58:12.005524	\N	\N	0	0	\N
1944	16	73	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005526	2025-12-03 18:58:12.005528	\N	\N	0	0	\N
1945	16	73	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.00553	2025-12-03 18:58:12.005532	\N	\N	0	0	\N
1946	16	73	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005534	2025-12-03 18:58:12.005536	\N	\N	0	0	\N
1947	16	73	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005538	2025-12-03 18:58:12.00554	\N	\N	0	0	\N
1948	16	73	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005542	2025-12-03 18:58:12.005544	\N	\N	0	0	\N
1949	16	73	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.005546	2025-12-03 18:58:12.005548	\N	\N	0	0	\N
1950	16	73	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:12.00555	2025-12-03 18:58:12.005552	\N	\N	0	0	\N
1951	16	74	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143306	2025-12-03 18:58:13.143312	\N	\N	0	0	\N
1952	16	74	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143314	2025-12-03 18:58:13.143316	\N	\N	0	0	\N
1953	16	74	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143318	2025-12-03 18:58:13.14332	\N	\N	0	0	\N
1954	16	74	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143322	2025-12-03 18:58:13.143324	\N	\N	0	0	\N
1955	16	74	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143326	2025-12-03 18:58:13.143328	\N	\N	0	0	\N
1956	16	74	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.14333	2025-12-03 18:58:13.143332	\N	\N	0	0	\N
1957	16	74	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143334	2025-12-03 18:58:13.143336	\N	\N	0	0	\N
1958	16	74	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143339	2025-12-03 18:58:13.14334	\N	\N	0	0	\N
1959	16	74	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143343	2025-12-03 18:58:13.143344	\N	\N	0	0	\N
1960	16	74	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143347	2025-12-03 18:58:13.143348	\N	\N	0	0	\N
1961	16	74	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143351	2025-12-03 18:58:13.143352	\N	\N	0	0	\N
1962	16	74	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143355	2025-12-03 18:58:13.143357	\N	\N	0	0	\N
1963	16	74	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143359	2025-12-03 18:58:13.143361	\N	\N	0	0	\N
1964	16	74	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143363	2025-12-03 18:58:13.143365	\N	\N	0	0	\N
1965	16	74	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143367	2025-12-03 18:58:13.143369	\N	\N	0	0	\N
1966	16	74	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143371	2025-12-03 18:58:13.143373	\N	\N	0	0	\N
1967	16	74	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143375	2025-12-03 18:58:13.143377	\N	\N	0	0	\N
1968	16	74	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143379	2025-12-03 18:58:13.14338	\N	\N	0	0	\N
1969	16	74	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143383	2025-12-03 18:58:13.143384	\N	\N	0	0	\N
1970	16	74	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143387	2025-12-03 18:58:13.143388	\N	\N	0	0	\N
1971	16	74	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.14339	2025-12-03 18:58:13.143392	\N	\N	0	0	\N
1972	16	74	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143394	2025-12-03 18:58:13.143396	\N	\N	0	0	\N
1973	16	74	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143399	2025-12-03 18:58:13.1434	\N	\N	0	0	\N
1974	16	74	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143402	2025-12-03 18:58:13.143404	\N	\N	0	0	\N
1975	16	74	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143406	2025-12-03 18:58:13.143408	\N	\N	0	0	\N
1976	16	74	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.14341	2025-12-03 18:58:13.143412	\N	\N	0	0	\N
1977	16	74	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143414	2025-12-03 18:58:13.143416	\N	\N	0	0	\N
1978	16	74	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143418	2025-12-03 18:58:13.14342	\N	\N	0	0	\N
1979	16	74	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143423	2025-12-03 18:58:13.143424	\N	\N	0	0	\N
1980	16	74	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143427	2025-12-03 18:58:13.143429	\N	\N	0	0	\N
1981	16	74	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:13.143431	2025-12-03 18:58:13.143433	\N	\N	0	0	\N
1982	16	75	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.28139	2025-12-03 18:58:14.281396	\N	\N	0	0	\N
1983	16	75	2025-12-02	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281398	2025-12-03 18:58:14.2814	\N	\N	0	0	\N
1984	16	75	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281402	2025-12-03 18:58:14.281404	\N	\N	0	0	\N
1985	16	75	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281406	2025-12-03 18:58:14.281408	\N	\N	0	0	\N
1986	16	75	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.28141	2025-12-03 18:58:14.281412	\N	\N	0	0	\N
1987	16	75	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281414	2025-12-03 18:58:14.281416	\N	\N	0	0	\N
1988	16	75	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281418	2025-12-03 18:58:14.28142	\N	\N	0	0	\N
1989	16	75	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281423	2025-12-03 18:58:14.281424	\N	\N	0	0	\N
1990	16	75	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281427	2025-12-03 18:58:14.281428	\N	\N	0	0	\N
1991	16	75	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281431	2025-12-03 18:58:14.281433	\N	\N	0	0	\N
1992	16	75	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281435	2025-12-03 18:58:14.281437	\N	\N	0	0	\N
1993	16	75	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281439	2025-12-03 18:58:14.28144	\N	\N	0	0	\N
1994	16	75	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281443	2025-12-03 18:58:14.281444	\N	\N	0	0	\N
1995	16	75	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281447	2025-12-03 18:58:14.281448	\N	\N	0	0	\N
1996	16	75	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281451	2025-12-03 18:58:14.281452	\N	\N	0	0	\N
1997	16	75	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281454	2025-12-03 18:58:14.281456	\N	\N	0	0	\N
1998	16	75	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281458	2025-12-03 18:58:14.28146	\N	\N	0	0	\N
1999	16	75	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281462	2025-12-03 18:58:14.281464	\N	\N	0	0	\N
2000	16	75	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281466	2025-12-03 18:58:14.281468	\N	\N	0	0	\N
2001	16	75	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.28147	2025-12-03 18:58:14.281472	\N	\N	0	0	\N
2002	16	75	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281474	2025-12-03 18:58:14.281476	\N	\N	0	0	\N
2003	16	75	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281478	2025-12-03 18:58:14.28148	\N	\N	0	0	\N
2004	16	75	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281482	2025-12-03 18:58:14.281484	\N	\N	0	0	\N
2005	16	75	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281486	2025-12-03 18:58:14.281488	\N	\N	0	0	\N
2006	16	75	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.28149	2025-12-03 18:58:14.281492	\N	\N	0	0	\N
2007	16	75	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281494	2025-12-03 18:58:14.281496	\N	\N	0	0	\N
2008	16	75	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281498	2025-12-03 18:58:14.2815	\N	\N	0	0	\N
2009	16	75	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281502	2025-12-03 18:58:14.281504	\N	\N	0	0	\N
2010	16	75	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281506	2025-12-03 18:58:14.281508	\N	\N	0	0	\N
2011	16	75	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.28151	2025-12-03 18:58:14.281512	\N	\N	0	0	\N
2012	16	75	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:14.281514	2025-12-03 18:58:14.281516	\N	\N	0	0	\N
2013	16	76	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418441	2025-12-03 18:58:15.418447	\N	\N	0	0	\N
2014	16	76	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418449	2025-12-03 18:58:15.418451	\N	\N	0	0	\N
2015	16	76	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418453	2025-12-03 18:58:15.418455	\N	\N	0	0	\N
2016	16	76	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418457	2025-12-03 18:58:15.418459	\N	\N	0	0	\N
2017	16	76	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418461	2025-12-03 18:58:15.418463	\N	\N	0	0	\N
2018	16	76	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418465	2025-12-03 18:58:15.418467	\N	\N	0	0	\N
2019	16	76	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418469	2025-12-03 18:58:15.418471	\N	\N	0	0	\N
2020	16	76	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418473	2025-12-03 18:58:15.418475	\N	\N	0	0	\N
2021	16	76	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418477	2025-12-03 18:58:15.418479	\N	\N	0	0	\N
2022	16	76	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418481	2025-12-03 18:58:15.418482	\N	\N	0	0	\N
2023	16	76	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418485	2025-12-03 18:58:15.418487	\N	\N	0	0	\N
2024	16	76	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418489	2025-12-03 18:58:15.418491	\N	\N	0	0	\N
2025	16	76	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418493	2025-12-03 18:58:15.418495	\N	\N	0	0	\N
2026	16	76	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418498	2025-12-03 18:58:15.4185	\N	\N	0	0	\N
2027	16	76	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418502	2025-12-03 18:58:15.418504	\N	\N	0	0	\N
2028	16	76	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418506	2025-12-03 18:58:15.418508	\N	\N	0	0	\N
2029	16	76	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.41851	2025-12-03 18:58:15.418512	\N	\N	0	0	\N
2030	16	76	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418514	2025-12-03 18:58:15.418516	\N	\N	0	0	\N
2031	16	76	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418518	2025-12-03 18:58:15.41852	\N	\N	0	0	\N
2032	16	76	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418522	2025-12-03 18:58:15.418524	\N	\N	0	0	\N
2033	16	76	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418526	2025-12-03 18:58:15.418528	\N	\N	0	0	\N
2034	16	76	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.41853	2025-12-03 18:58:15.418532	\N	\N	0	0	\N
2035	16	76	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418534	2025-12-03 18:58:15.418536	\N	\N	0	0	\N
2036	16	76	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418538	2025-12-03 18:58:15.41854	\N	\N	0	0	\N
2037	16	76	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418542	2025-12-03 18:58:15.418544	\N	\N	0	0	\N
2038	16	76	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418546	2025-12-03 18:58:15.418548	\N	\N	0	0	\N
2039	16	76	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.41855	2025-12-03 18:58:15.418552	\N	\N	0	0	\N
2040	16	76	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418554	2025-12-03 18:58:15.418556	\N	\N	0	0	\N
2041	16	76	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418558	2025-12-03 18:58:15.41856	\N	\N	0	0	\N
2042	16	76	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418562	2025-12-03 18:58:15.418564	\N	\N	0	0	\N
2043	16	76	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:15.418566	2025-12-03 18:58:15.418568	\N	\N	0	0	\N
2044	16	77	2025-12-01	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556474	2025-12-03 18:58:16.55648	\N	\N	0	0	\N
2045	16	77	2025-12-02	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556482	2025-12-03 18:58:16.556484	\N	\N	0	0	\N
2046	16	77	2025-12-03	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556486	2025-12-03 18:58:16.556488	\N	\N	0	0	\N
2047	16	77	2025-12-04	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.55649	2025-12-03 18:58:16.556492	\N	\N	0	0	\N
2048	16	77	2025-12-05	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556494	2025-12-03 18:58:16.556496	\N	\N	0	0	\N
2049	16	77	2025-12-06	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556498	2025-12-03 18:58:16.5565	\N	\N	0	0	\N
2050	16	77	2025-12-07	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556502	2025-12-03 18:58:16.556504	\N	\N	0	0	\N
2051	16	77	2025-12-08	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556506	2025-12-03 18:58:16.556508	\N	\N	0	0	\N
2052	16	77	2025-12-09	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.55651	2025-12-03 18:58:16.556511	\N	\N	0	0	\N
2053	16	77	2025-12-10	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556514	2025-12-03 18:58:16.556516	\N	\N	0	0	\N
2054	16	77	2025-12-11	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556518	2025-12-03 18:58:16.556519	\N	\N	0	0	\N
2055	16	77	2025-12-12	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556522	2025-12-03 18:58:16.556523	\N	\N	0	0	\N
2056	16	77	2025-12-13	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556525	2025-12-03 18:58:16.556527	\N	\N	0	0	\N
2057	16	77	2025-12-14	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556529	2025-12-03 18:58:16.556531	\N	\N	0	0	\N
2058	16	77	2025-12-15	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556533	2025-12-03 18:58:16.556535	\N	\N	0	0	\N
2059	16	77	2025-12-16	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556537	2025-12-03 18:58:16.556539	\N	\N	0	0	\N
2060	16	77	2025-12-17	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556541	2025-12-03 18:58:16.556543	\N	\N	0	0	\N
2061	16	77	2025-12-18	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556545	2025-12-03 18:58:16.556547	\N	\N	0	0	\N
2062	16	77	2025-12-19	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556549	2025-12-03 18:58:16.556551	\N	\N	0	0	\N
2063	16	77	2025-12-20	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556553	2025-12-03 18:58:16.556555	\N	\N	0	0	\N
2064	16	77	2025-12-21	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556557	2025-12-03 18:58:16.556559	\N	\N	0	0	\N
2065	16	77	2025-12-22	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556561	2025-12-03 18:58:16.556563	\N	\N	0	0	\N
2066	16	77	2025-12-23	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556565	2025-12-03 18:58:16.556567	\N	\N	0	0	\N
2067	16	77	2025-12-24	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556569	2025-12-03 18:58:16.556571	\N	\N	0	0	\N
2068	16	77	2025-12-25	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556573	2025-12-03 18:58:16.556575	\N	\N	0	0	\N
2069	16	77	2025-12-26	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556577	2025-12-03 18:58:16.556579	\N	\N	0	0	\N
2070	16	77	2025-12-27	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556581	2025-12-03 18:58:16.556583	\N	\N	0	0	\N
2071	16	77	2025-12-28	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556585	2025-12-03 18:58:16.556587	\N	\N	0	0	\N
2072	16	77	2025-12-29	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556589	2025-12-03 18:58:16.556591	\N	\N	0	0	\N
2073	16	77	2025-12-30	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556593	2025-12-03 18:58:16.556594	\N	\N	0	0	\N
2074	16	77	2025-12-31	2.50	80.00	200.00	delivered	f	\N	\N	2025-12-03 18:58:16.556597	2025-12-03 18:58:16.556598	\N	\N	0	0	\N
2075	16	78	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.696977	2025-12-03 18:58:17.696982	\N	\N	0	0	\N
2076	16	78	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.696986	2025-12-03 18:58:17.696987	\N	\N	0	0	\N
2077	16	78	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.69699	2025-12-03 18:58:17.696992	\N	\N	0	0	\N
2106	16	79	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839039	2025-12-03 18:58:18.839044	\N	\N	0	0	\N
2107	16	79	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839047	2025-12-03 18:58:18.839048	\N	\N	0	0	\N
2108	16	79	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839051	2025-12-03 18:58:18.839053	\N	\N	0	0	\N
2137	16	80	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979173	2025-12-03 18:58:19.979178	\N	\N	0	0	\N
2138	16	80	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979181	2025-12-03 18:58:19.979183	\N	\N	0	0	\N
2139	16	80	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979185	2025-12-03 18:58:19.979187	\N	\N	0	0	\N
2168	16	81	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118139	2025-12-03 18:58:21.118144	\N	\N	0	0	\N
2169	16	81	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118147	2025-12-03 18:58:21.118149	\N	\N	0	0	\N
2170	16	81	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118151	2025-12-03 18:58:21.118153	\N	\N	0	0	\N
2199	16	82	2025-12-01	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253609	2025-12-03 18:58:22.253614	\N	\N	0	0	\N
2200	16	82	2025-12-03	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253617	2025-12-03 18:58:22.253619	\N	\N	0	0	\N
2215	16	83	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389241	2025-12-03 18:58:23.389247	\N	\N	0	0	\N
2216	16	83	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389249	2025-12-03 18:58:23.389251	\N	\N	0	0	\N
2217	16	83	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389254	2025-12-03 18:58:23.389255	\N	\N	0	0	\N
2246	16	84	2025-12-01	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339234	2025-12-03 18:58:24.33924	\N	\N	0	0	\N
2247	16	84	2025-12-02	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339243	2025-12-03 18:58:24.339244	\N	\N	0	0	\N
2248	16	84	2025-12-03	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339247	2025-12-03 18:58:24.339249	\N	\N	0	0	\N
2198	16	81	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118263	2025-12-03 19:57:30.85431	\N	\N	0	0	28
2201	16	82	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253621	2025-12-03 19:57:36.624861	\N	\N	0	0	28
2202	16	82	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253625	2025-12-03 19:57:36.624867	\N	\N	0	0	28
2277	16	85	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480682	2025-12-03 18:58:25.480687	\N	\N	0	0	\N
2278	16	85	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.48069	2025-12-03 18:58:25.480692	\N	\N	0	0	\N
2279	16	85	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480694	2025-12-03 18:58:25.480696	\N	\N	0	0	\N
2308	16	86	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616602	2025-12-03 18:58:26.616609	\N	\N	0	0	\N
2309	16	86	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616612	2025-12-03 18:58:26.616613	\N	\N	0	0	\N
2310	16	86	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616616	2025-12-03 18:58:26.616617	\N	\N	0	0	\N
2311	16	86	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.61662	2025-12-03 18:58:26.616621	\N	\N	0	0	\N
2312	16	86	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616624	2025-12-03 18:58:26.616626	\N	\N	0	0	\N
2313	16	86	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616628	2025-12-03 18:58:26.61663	\N	\N	0	0	\N
2314	16	86	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616632	2025-12-03 18:58:26.616634	\N	\N	0	0	\N
2315	16	86	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616636	2025-12-03 18:58:26.616638	\N	\N	0	0	\N
2316	16	86	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.61664	2025-12-03 18:58:26.616642	\N	\N	0	0	\N
2317	16	86	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616644	2025-12-03 18:58:26.616646	\N	\N	0	0	\N
2318	16	86	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616648	2025-12-03 18:58:26.61665	\N	\N	0	0	\N
2319	16	86	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616652	2025-12-03 18:58:26.616654	\N	\N	0	0	\N
2320	16	86	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616656	2025-12-03 18:58:26.616658	\N	\N	0	0	\N
2321	16	86	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.61666	2025-12-03 18:58:26.616662	\N	\N	0	0	\N
2322	16	86	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:26.616664	2025-12-03 18:58:26.616666	\N	\N	0	0	\N
2323	16	87	2025-12-01	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751384	2025-12-03 18:58:27.751389	\N	\N	0	0	\N
2324	16	87	2025-12-02	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751392	2025-12-03 18:58:27.751394	\N	\N	0	0	\N
2325	16	87	2025-12-03	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751396	2025-12-03 18:58:27.751398	\N	\N	0	0	\N
2326	16	87	2025-12-04	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751401	2025-12-03 18:58:27.751402	\N	\N	0	0	\N
2327	16	87	2025-12-05	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751405	2025-12-03 18:58:27.751406	\N	\N	0	0	\N
2328	16	87	2025-12-06	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751409	2025-12-03 18:58:27.75141	\N	\N	0	0	\N
2329	16	87	2025-12-07	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751413	2025-12-03 18:58:27.751414	\N	\N	0	0	\N
2330	16	87	2025-12-08	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751417	2025-12-03 18:58:27.751418	\N	\N	0	0	\N
2331	16	87	2025-12-09	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751421	2025-12-03 18:58:27.751422	\N	\N	0	0	\N
2332	16	87	2025-12-10	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751425	2025-12-03 18:58:27.751426	\N	\N	0	0	\N
2333	16	87	2025-12-11	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751429	2025-12-03 18:58:27.751431	\N	\N	0	0	\N
2334	16	87	2025-12-12	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751433	2025-12-03 18:58:27.751435	\N	\N	0	0	\N
2335	16	87	2025-12-13	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751437	2025-12-03 18:58:27.751439	\N	\N	0	0	\N
2336	16	87	2025-12-14	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751441	2025-12-03 18:58:27.751442	\N	\N	0	0	\N
2337	16	87	2025-12-15	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751445	2025-12-03 18:58:27.751446	\N	\N	0	0	\N
2338	16	87	2025-12-16	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751448	2025-12-03 18:58:27.75145	\N	\N	0	0	\N
2339	16	87	2025-12-17	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751452	2025-12-03 18:58:27.751454	\N	\N	0	0	\N
2340	16	87	2025-12-18	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751456	2025-12-03 18:58:27.751458	\N	\N	0	0	\N
2341	16	87	2025-12-19	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.75146	2025-12-03 18:58:27.751462	\N	\N	0	0	\N
2342	16	87	2025-12-20	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751464	2025-12-03 18:58:27.751465	\N	\N	0	0	\N
2343	16	87	2025-12-21	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751468	2025-12-03 18:58:27.751469	\N	\N	0	0	\N
2344	16	87	2025-12-22	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751471	2025-12-03 18:58:27.751473	\N	\N	0	0	\N
2345	16	87	2025-12-23	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751475	2025-12-03 18:58:27.751477	\N	\N	0	0	\N
2346	16	87	2025-12-24	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751479	2025-12-03 18:58:27.751481	\N	\N	0	0	\N
2347	16	87	2025-12-25	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751483	2025-12-03 18:58:27.751485	\N	\N	0	0	\N
2348	16	87	2025-12-26	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751487	2025-12-03 18:58:27.751489	\N	\N	0	0	\N
2349	16	87	2025-12-27	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751491	2025-12-03 18:58:27.751493	\N	\N	0	0	\N
2350	16	87	2025-12-28	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751495	2025-12-03 18:58:27.751497	\N	\N	0	0	\N
2351	16	87	2025-12-29	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751499	2025-12-03 18:58:27.751501	\N	\N	0	0	\N
2352	16	87	2025-12-30	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751503	2025-12-03 18:58:27.751504	\N	\N	0	0	\N
2353	16	87	2025-12-31	2.00	80.00	160.00	delivered	f	\N	\N	2025-12-03 18:58:27.751507	2025-12-03 18:58:27.751508	\N	\N	0	0	\N
2354	16	88	2025-12-01	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889702	2025-12-03 18:58:28.889707	\N	\N	0	0	\N
2355	16	88	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889709	2025-12-03 18:58:28.889711	\N	\N	0	0	\N
2356	16	88	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889714	2025-12-03 18:58:28.889715	\N	\N	0	0	\N
2357	16	88	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889718	2025-12-03 18:58:28.889719	\N	\N	0	0	\N
2358	16	88	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889722	2025-12-03 18:58:28.889723	\N	\N	0	0	\N
2359	16	88	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889726	2025-12-03 18:58:28.889727	\N	\N	0	0	\N
2360	16	88	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.88973	2025-12-03 18:58:28.889732	\N	\N	0	0	\N
2361	16	88	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889734	2025-12-03 18:58:28.889736	\N	\N	0	0	\N
2362	16	88	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889738	2025-12-03 18:58:28.88974	\N	\N	0	0	\N
2363	16	88	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889742	2025-12-03 18:58:28.889744	\N	\N	0	0	\N
2364	16	88	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889746	2025-12-03 18:58:28.889748	\N	\N	0	0	\N
2365	16	88	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.88975	2025-12-03 18:58:28.889752	\N	\N	0	0	\N
2366	16	88	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889754	2025-12-03 18:58:28.889756	\N	\N	0	0	\N
2367	16	88	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889758	2025-12-03 18:58:28.88976	\N	\N	0	0	\N
2368	16	88	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889762	2025-12-03 18:58:28.889764	\N	\N	0	0	\N
2369	16	88	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889766	2025-12-03 18:58:28.889768	\N	\N	0	0	\N
2370	16	88	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.88977	2025-12-03 18:58:28.889772	\N	\N	0	0	\N
2371	16	88	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889774	2025-12-03 18:58:28.889776	\N	\N	0	0	\N
2372	16	88	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889778	2025-12-03 18:58:28.88978	\N	\N	0	0	\N
2373	16	88	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889782	2025-12-03 18:58:28.889784	\N	\N	0	0	\N
2374	16	88	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889786	2025-12-03 18:58:28.889788	\N	\N	0	0	\N
2375	16	88	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.88979	2025-12-03 18:58:28.889792	\N	\N	0	0	\N
2376	16	88	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889794	2025-12-03 18:58:28.889796	\N	\N	0	0	\N
2377	16	88	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889799	2025-12-03 18:58:28.8898	\N	\N	0	0	\N
2378	16	88	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889803	2025-12-03 18:58:28.889804	\N	\N	0	0	\N
2379	16	88	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889807	2025-12-03 18:58:28.889808	\N	\N	0	0	\N
2380	16	88	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.88981	2025-12-03 18:58:28.889812	\N	\N	0	0	\N
2381	16	88	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889815	2025-12-03 18:58:28.889816	\N	\N	0	0	\N
2382	16	88	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889819	2025-12-03 18:58:28.88982	\N	\N	0	0	\N
2383	16	88	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889833	2025-12-03 18:58:28.889834	\N	\N	0	0	\N
2384	16	88	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:28.889837	2025-12-03 18:58:28.889838	\N	\N	0	0	\N
2385	16	89	2025-12-02	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034095	2025-12-03 18:58:30.0341	\N	\N	0	0	\N
2386	16	89	2025-12-03	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034103	2025-12-03 18:58:30.034105	\N	\N	0	0	\N
2387	16	89	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034107	2025-12-03 18:58:30.034109	\N	\N	0	0	\N
2388	16	89	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034111	2025-12-03 18:58:30.034113	\N	\N	0	0	\N
2389	16	89	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034115	2025-12-03 18:58:30.034117	\N	\N	0	0	\N
2390	16	89	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034119	2025-12-03 18:58:30.034121	\N	\N	0	0	\N
2391	16	89	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034123	2025-12-03 18:58:30.034124	\N	\N	0	0	\N
2392	16	89	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034126	2025-12-03 18:58:30.034128	\N	\N	0	0	\N
2393	16	89	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.03413	2025-12-03 18:58:30.034132	\N	\N	0	0	\N
2394	16	89	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034134	2025-12-03 18:58:30.034136	\N	\N	0	0	\N
2395	16	89	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034138	2025-12-03 18:58:30.03414	\N	\N	0	0	\N
2396	16	89	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034142	2025-12-03 18:58:30.034144	\N	\N	0	0	\N
2397	16	89	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034146	2025-12-03 18:58:30.034148	\N	\N	0	0	\N
2398	16	89	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.03415	2025-12-03 18:58:30.034152	\N	\N	0	0	\N
2399	16	89	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034154	2025-12-03 18:58:30.034156	\N	\N	0	0	\N
2400	16	89	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034158	2025-12-03 18:58:30.03416	\N	\N	0	0	\N
2401	16	89	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034162	2025-12-03 18:58:30.034164	\N	\N	0	0	\N
2402	16	89	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034166	2025-12-03 18:58:30.034168	\N	\N	0	0	\N
2403	16	89	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.03417	2025-12-03 18:58:30.034172	\N	\N	0	0	\N
2404	16	89	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034174	2025-12-03 18:58:30.034175	\N	\N	0	0	\N
2405	16	89	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034177	2025-12-03 18:58:30.034179	\N	\N	0	0	\N
2406	16	89	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034181	2025-12-03 18:58:30.034183	\N	\N	0	0	\N
2407	16	89	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034185	2025-12-03 18:58:30.034187	\N	\N	0	0	\N
2408	16	89	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.03419	2025-12-03 18:58:30.034191	\N	\N	0	0	\N
2409	16	89	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034193	2025-12-03 18:58:30.034195	\N	\N	0	0	\N
2410	16	89	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034197	2025-12-03 18:58:30.034199	\N	\N	0	0	\N
2411	16	89	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034201	2025-12-03 18:58:30.034203	\N	\N	0	0	\N
2412	16	89	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034205	2025-12-03 18:58:30.034207	\N	\N	0	0	\N
2413	16	89	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034209	2025-12-03 18:58:30.034211	\N	\N	0	0	\N
2414	16	89	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:30.034213	2025-12-03 18:58:30.034215	\N	\N	0	0	\N
2603	16	91	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744083	2025-12-03 19:59:38.156544	\N	\N	0	0	28
2604	16	91	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744087	2025-12-03 19:59:38.15655	\N	\N	0	0	28
2605	16	91	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744091	2025-12-03 19:59:38.156552	\N	\N	0	0	28
2606	16	91	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744096	2025-12-03 19:59:38.156554	\N	\N	0	0	28
2607	16	91	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.7441	2025-12-03 19:59:38.156556	\N	\N	0	0	28
2608	16	91	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744104	2025-12-03 19:59:38.156558	\N	\N	0	0	28
2609	16	91	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744108	2025-12-03 19:59:38.15656	\N	\N	0	0	28
2610	16	91	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744112	2025-12-03 19:59:38.156562	\N	\N	0	0	28
2611	16	91	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744116	2025-12-03 19:59:38.156564	\N	\N	0	0	28
2612	16	91	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.74412	2025-12-03 19:59:38.156566	\N	\N	0	0	28
2613	16	91	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744125	2025-12-03 19:59:38.156568	\N	\N	0	0	28
2600	16	91	2025-12-01	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744066	2025-12-03 19:28:51.744072	\N	\N	0	0	\N
2601	16	91	2025-12-02	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744075	2025-12-03 19:28:51.744076	\N	\N	0	0	\N
2602	16	91	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:28:51.744079	2025-12-03 19:28:51.744081	\N	\N	0	0	\N
2631	16	92	2025-12-03	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904058	2025-12-03 19:32:02.904064	\N	\N	0	0	\N
1517	16	60	2025-12-01	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394915	2025-12-03 19:32:57.197655	\N	\N	0	0	\N
1518	16	60	2025-12-02	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394923	2025-12-03 19:32:57.583272	\N	\N	0	0	\N
1519	16	60	2025-12-03	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394927	2025-12-03 19:32:57.957151	\N	\N	0	0	\N
1520	16	60	2025-12-04	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394931	2025-12-03 19:32:58.33075	\N	\N	0	0	\N
1521	16	60	2025-12-05	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394935	2025-12-03 19:32:58.704598	\N	\N	0	0	\N
1522	16	60	2025-12-06	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394938	2025-12-03 19:32:59.082474	\N	\N	0	0	\N
1523	16	60	2025-12-07	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394942	2025-12-03 19:32:59.456744	\N	\N	0	0	\N
1524	16	60	2025-12-08	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394946	2025-12-03 19:32:59.831589	\N	\N	0	0	\N
1525	16	60	2025-12-09	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.39495	2025-12-03 19:33:00.205866	\N	\N	0	0	\N
1526	16	60	2025-12-10	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394954	2025-12-03 19:33:00.57947	\N	\N	0	0	\N
1527	16	60	2025-12-11	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394958	2025-12-03 19:33:00.953706	\N	\N	0	0	\N
1528	16	60	2025-12-12	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394962	2025-12-03 19:33:01.327259	\N	\N	0	0	\N
1529	16	60	2025-12-13	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394966	2025-12-03 19:33:01.701035	\N	\N	0	0	\N
1530	16	60	2025-12-14	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.39497	2025-12-03 19:33:02.074734	\N	\N	0	0	\N
1531	16	60	2025-12-15	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394974	2025-12-03 19:33:02.448133	\N	\N	0	0	\N
1532	16	60	2025-12-16	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394978	2025-12-03 19:33:02.821446	\N	\N	0	0	\N
1533	16	60	2025-12-17	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394982	2025-12-03 19:33:03.195468	\N	\N	0	0	\N
1534	16	60	2025-12-18	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394986	2025-12-03 19:33:03.568912	\N	\N	0	0	\N
1535	16	60	2025-12-19	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.39499	2025-12-03 19:33:03.942282	\N	\N	0	0	\N
1536	16	60	2025-12-20	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394994	2025-12-03 19:33:04.315851	\N	\N	0	0	\N
1537	16	60	2025-12-21	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.394998	2025-12-03 19:33:04.689416	\N	\N	0	0	\N
1538	16	60	2025-12-22	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395002	2025-12-03 19:33:05.063003	\N	\N	0	0	\N
1539	16	60	2025-12-23	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395006	2025-12-03 19:33:05.436692	\N	\N	0	0	\N
1540	16	60	2025-12-24	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.39501	2025-12-03 19:33:05.810455	\N	\N	0	0	\N
1541	16	60	2025-12-25	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395014	2025-12-03 19:33:06.184346	\N	\N	0	0	\N
1542	16	60	2025-12-26	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395018	2025-12-03 19:33:06.557931	\N	\N	0	0	\N
1543	16	60	2025-12-27	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395021	2025-12-03 19:33:06.931974	\N	\N	0	0	\N
1544	16	60	2025-12-28	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395025	2025-12-03 19:33:07.305729	\N	\N	0	0	\N
1545	16	60	2025-12-29	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395029	2025-12-03 19:33:07.679844	\N	\N	0	0	\N
1546	16	60	2025-12-30	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395033	2025-12-03 19:33:08.053217	\N	\N	0	0	\N
2640	16	93	2025-12-03	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376858	2025-12-03 19:42:23.376863	\N	\N	0	0	\N
2641	16	93	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376866	2025-12-03 19:42:23.376868	\N	\N	0	0	\N
2642	16	93	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.37687	2025-12-03 19:42:23.376872	\N	\N	0	0	\N
2643	16	93	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376874	2025-12-03 19:42:23.376876	\N	\N	0	0	\N
2644	16	93	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376878	2025-12-03 19:42:23.37688	\N	\N	0	0	\N
2645	16	93	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376882	2025-12-03 19:42:23.376884	\N	\N	0	0	\N
2646	16	93	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376886	2025-12-03 19:42:23.376888	\N	\N	0	0	\N
2647	16	93	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.37689	2025-12-03 19:42:23.376892	\N	\N	0	0	\N
2648	16	93	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376895	2025-12-03 19:42:23.376896	\N	\N	0	0	\N
2649	16	93	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376899	2025-12-03 19:42:23.376901	\N	\N	0	0	\N
2650	16	93	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376903	2025-12-03 19:42:23.376905	\N	\N	0	0	\N
2651	16	93	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376907	2025-12-03 19:42:23.376909	\N	\N	0	0	\N
2652	16	93	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376911	2025-12-03 19:42:23.376913	\N	\N	0	0	\N
2653	16	93	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376915	2025-12-03 19:42:23.376917	\N	\N	0	0	\N
2654	16	93	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.37692	2025-12-03 19:42:23.376922	\N	\N	0	0	\N
2655	16	93	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376924	2025-12-03 19:42:23.376926	\N	\N	0	0	\N
2656	16	93	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376928	2025-12-03 19:42:23.37693	\N	\N	0	0	\N
2657	16	93	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376933	2025-12-03 19:42:23.376934	\N	\N	0	0	\N
2658	16	93	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376937	2025-12-03 19:42:23.376939	\N	\N	0	0	\N
2659	16	93	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376941	2025-12-03 19:42:23.376943	\N	\N	0	0	\N
2660	16	93	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376945	2025-12-03 19:42:23.376947	\N	\N	0	0	\N
2661	16	93	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376949	2025-12-03 19:42:23.376951	\N	\N	0	0	\N
2662	16	93	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376954	2025-12-03 19:42:23.376955	\N	\N	0	0	\N
2663	16	93	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376958	2025-12-03 19:42:23.376959	\N	\N	0	0	\N
2664	16	93	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376962	2025-12-03 19:42:23.376964	\N	\N	0	0	\N
2665	16	93	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376966	2025-12-03 19:42:23.376968	\N	\N	0	0	\N
2666	16	93	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.37697	2025-12-03 19:42:23.376972	\N	\N	0	0	\N
2667	16	93	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376974	2025-12-03 19:42:23.376976	\N	\N	0	0	\N
2668	16	93	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 19:42:23.376978	2025-12-03 19:42:23.37698	\N	\N	0	0	\N
2637	16	92	2025-12-24	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904088	2025-12-03 19:58:19.636455	\N	\N	0	0	28
2638	16	92	2025-12-28	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904092	2025-12-03 19:58:19.636457	\N	\N	0	0	28
2639	16	92	2025-12-31	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904097	2025-12-03 19:58:19.636459	\N	\N	0	0	28
1547	16	60	2025-12-31	0.00	70.00	0.00	paused	t	on Demand	\N	2025-12-03 18:57:57.395037	2025-12-03 19:33:08.426732	\N	\N	0	0	\N
95	16	13	2025-12-04	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652373	2025-12-03 19:55:07.604026	\N	\N	0	0	28
96	16	13	2025-12-05	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652377	2025-12-03 19:55:07.604032	\N	\N	0	0	28
97	16	13	2025-12-06	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652381	2025-12-03 19:55:07.604034	\N	\N	0	0	28
98	16	13	2025-12-07	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652385	2025-12-03 19:55:07.604036	\N	\N	0	0	28
99	16	13	2025-12-08	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652389	2025-12-03 19:55:07.604038	\N	\N	0	0	28
100	16	13	2025-12-09	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652394	2025-12-03 19:55:07.60404	\N	\N	0	0	28
101	16	13	2025-12-10	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652398	2025-12-03 19:55:07.604042	\N	\N	0	0	28
102	16	13	2025-12-11	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652402	2025-12-03 19:55:07.604045	\N	\N	0	0	28
103	16	13	2025-12-12	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652406	2025-12-03 19:55:07.604047	\N	\N	0	0	28
104	16	13	2025-12-13	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.65241	2025-12-03 19:55:07.604049	\N	\N	0	0	28
105	16	13	2025-12-14	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652414	2025-12-03 19:55:07.604051	\N	\N	0	0	28
106	16	13	2025-12-15	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652418	2025-12-03 19:55:07.604053	\N	\N	0	0	28
107	16	13	2025-12-16	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652422	2025-12-03 19:55:07.604055	\N	\N	0	0	28
108	16	13	2025-12-17	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652427	2025-12-03 19:55:07.604057	\N	\N	0	0	28
109	16	13	2025-12-18	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652431	2025-12-03 19:55:07.604059	\N	\N	0	0	28
110	16	13	2025-12-19	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652435	2025-12-03 19:55:07.604061	\N	\N	0	0	28
111	16	13	2025-12-20	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652439	2025-12-03 19:55:07.604063	\N	\N	0	0	28
112	16	13	2025-12-21	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652443	2025-12-03 19:55:07.604065	\N	\N	0	0	28
113	16	13	2025-12-22	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652447	2025-12-03 19:55:07.604067	\N	\N	0	0	28
114	16	13	2025-12-23	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652452	2025-12-03 19:55:07.604069	\N	\N	0	0	28
115	16	13	2025-12-24	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652456	2025-12-03 19:55:07.604071	\N	\N	0	0	28
116	16	13	2025-12-25	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.65246	2025-12-03 19:55:07.604073	\N	\N	0	0	28
117	16	13	2025-12-26	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652464	2025-12-03 19:55:07.604075	\N	\N	0	0	28
118	16	13	2025-12-27	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652468	2025-12-03 19:55:07.604077	\N	\N	0	0	28
119	16	13	2025-12-28	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652472	2025-12-03 19:55:07.604079	\N	\N	0	0	28
120	16	13	2025-12-29	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652476	2025-12-03 19:55:07.604081	\N	\N	0	0	28
121	16	13	2025-12-30	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652481	2025-12-03 19:55:07.604083	\N	\N	0	0	28
122	16	13	2025-12-31	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-02 15:49:51.652485	2025-12-03 19:55:07.604085	\N	\N	0	0	28
157	16	15	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056204	2025-12-03 19:55:13.384476	\N	\N	0	0	28
158	16	15	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056208	2025-12-03 19:55:13.384482	\N	\N	0	0	28
159	16	15	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056212	2025-12-03 19:55:13.384485	\N	\N	0	0	28
160	16	15	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056216	2025-12-03 19:55:13.384487	\N	\N	0	0	28
161	16	15	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.05622	2025-12-03 19:55:13.384489	\N	\N	0	0	28
162	16	15	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056224	2025-12-03 19:55:13.384491	\N	\N	0	0	28
163	16	15	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056228	2025-12-03 19:55:13.384492	\N	\N	0	0	28
164	16	15	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056232	2025-12-03 19:55:13.384494	\N	\N	0	0	28
165	16	15	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056236	2025-12-03 19:55:13.384496	\N	\N	0	0	28
166	16	15	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.05624	2025-12-03 19:55:13.384498	\N	\N	0	0	28
167	16	15	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056244	2025-12-03 19:55:13.3845	\N	\N	0	0	28
168	16	15	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056248	2025-12-03 19:55:13.384502	\N	\N	0	0	28
169	16	15	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056252	2025-12-03 19:55:13.384504	\N	\N	0	0	28
170	16	15	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056256	2025-12-03 19:55:13.384506	\N	\N	0	0	28
171	16	15	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.05626	2025-12-03 19:55:13.384508	\N	\N	0	0	28
172	16	15	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056264	2025-12-03 19:55:13.38451	\N	\N	0	0	28
173	16	15	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056268	2025-12-03 19:55:13.384512	\N	\N	0	0	28
176	16	15	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056281	2025-12-03 19:55:13.384518	\N	\N	0	0	28
177	16	15	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056285	2025-12-03 19:55:13.38452	\N	\N	0	0	28
178	16	15	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056289	2025-12-03 19:55:13.384522	\N	\N	0	0	28
179	16	15	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056293	2025-12-03 19:55:13.384523	\N	\N	0	0	28
180	16	15	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056297	2025-12-03 19:55:13.384525	\N	\N	0	0	28
181	16	15	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056301	2025-12-03 19:55:13.384527	\N	\N	0	0	28
182	16	15	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056305	2025-12-03 19:55:13.384529	\N	\N	0	0	28
183	16	15	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056318	2025-12-03 19:55:13.384531	\N	\N	0	0	28
184	16	15	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:57:17.056322	2025-12-03 19:55:13.384533	\N	\N	0	0	28
188	16	16	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.266987	2025-12-03 19:55:19.16867	\N	\N	0	0	28
189	16	16	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.266991	2025-12-03 19:55:19.168677	\N	\N	0	0	28
190	16	16	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.266995	2025-12-03 19:55:19.168679	\N	\N	0	0	28
191	16	16	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.266999	2025-12-03 19:55:19.168681	\N	\N	0	0	28
192	16	16	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267003	2025-12-03 19:55:19.168683	\N	\N	0	0	28
193	16	16	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267007	2025-12-03 19:55:19.168685	\N	\N	0	0	28
194	16	16	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267011	2025-12-03 19:55:19.168687	\N	\N	0	0	28
195	16	16	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267016	2025-12-03 19:55:19.168688	\N	\N	0	0	28
196	16	16	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.26702	2025-12-03 19:55:19.168691	\N	\N	0	0	28
197	16	16	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267024	2025-12-03 19:55:19.168693	\N	\N	0	0	28
198	16	16	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267028	2025-12-03 19:55:19.168695	\N	\N	0	0	28
199	16	16	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267032	2025-12-03 19:55:19.168697	\N	\N	0	0	28
200	16	16	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267036	2025-12-03 19:55:19.168699	\N	\N	0	0	28
201	16	16	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.26704	2025-12-03 19:55:19.168701	\N	\N	0	0	28
202	16	16	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267044	2025-12-03 19:55:19.168703	\N	\N	0	0	28
203	16	16	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267048	2025-12-03 19:55:19.168705	\N	\N	0	0	28
204	16	16	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267052	2025-12-03 19:55:19.168707	\N	\N	0	0	28
205	16	16	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267056	2025-12-03 19:55:19.168709	\N	\N	0	0	28
206	16	16	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.26706	2025-12-03 19:55:19.168711	\N	\N	0	0	28
207	16	16	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267064	2025-12-03 19:55:19.168713	\N	\N	0	0	28
208	16	16	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267068	2025-12-03 19:55:19.168715	\N	\N	0	0	28
209	16	16	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267072	2025-12-03 19:55:19.168717	\N	\N	0	0	28
210	16	16	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267077	2025-12-03 19:55:19.168719	\N	\N	0	0	28
211	16	16	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267081	2025-12-03 19:55:19.168721	\N	\N	0	0	28
212	16	16	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267085	2025-12-03 19:55:19.168723	\N	\N	0	0	28
213	16	16	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267089	2025-12-03 19:55:19.168725	\N	\N	0	0	28
214	16	16	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267093	2025-12-03 19:55:19.168727	\N	\N	0	0	28
215	16	16	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 15:58:30.267097	2025-12-03 19:55:19.168729	\N	\N	0	0	28
219	16	17	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356702	2025-12-03 19:55:24.943666	\N	\N	0	0	28
220	16	17	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356706	2025-12-03 19:55:24.943672	\N	\N	0	0	28
221	16	17	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356711	2025-12-03 19:55:24.943674	\N	\N	0	0	28
222	16	17	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356715	2025-12-03 19:55:24.943676	\N	\N	0	0	28
223	16	17	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356719	2025-12-03 19:55:24.943678	\N	\N	0	0	28
224	16	17	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356723	2025-12-03 19:55:24.94368	\N	\N	0	0	28
225	16	17	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356727	2025-12-03 19:55:24.943682	\N	\N	0	0	28
226	16	17	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356731	2025-12-03 19:55:24.943684	\N	\N	0	0	28
227	16	17	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356735	2025-12-03 19:55:24.943686	\N	\N	0	0	28
228	16	17	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356739	2025-12-03 19:55:24.943688	\N	\N	0	0	28
229	16	17	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356743	2025-12-03 19:55:24.94369	\N	\N	0	0	28
230	16	17	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356748	2025-12-03 19:55:24.943692	\N	\N	0	0	28
231	16	17	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356752	2025-12-03 19:55:24.943694	\N	\N	0	0	28
232	16	17	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356756	2025-12-03 19:55:24.943696	\N	\N	0	0	28
233	16	17	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.35676	2025-12-03 19:55:24.943698	\N	\N	0	0	28
234	16	17	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356764	2025-12-03 19:55:24.9437	\N	\N	0	0	28
235	16	17	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356768	2025-12-03 19:55:24.943702	\N	\N	0	0	28
236	16	17	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356772	2025-12-03 19:55:24.943704	\N	\N	0	0	28
237	16	17	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356776	2025-12-03 19:55:24.943706	\N	\N	0	0	28
238	16	17	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.35678	2025-12-03 19:55:24.943708	\N	\N	0	0	28
239	16	17	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356784	2025-12-03 19:55:24.94371	\N	\N	0	0	28
240	16	17	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356789	2025-12-03 19:55:24.943712	\N	\N	0	0	28
241	16	17	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356793	2025-12-03 19:55:24.943714	\N	\N	0	0	28
242	16	17	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356797	2025-12-03 19:55:24.943716	\N	\N	0	0	28
243	16	17	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356801	2025-12-03 19:55:24.943718	\N	\N	0	0	28
244	16	17	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356805	2025-12-03 19:55:24.94372	\N	\N	0	0	28
245	16	17	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356809	2025-12-03 19:55:24.943721	\N	\N	0	0	28
246	16	17	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 17:45:36.356813	2025-12-03 19:55:24.943723	\N	\N	0	0	28
307	16	20	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994619	2025-12-03 19:55:30.722353	\N	\N	0	0	28
308	16	20	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994623	2025-12-03 19:55:30.722355	\N	\N	0	0	28
309	16	20	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994627	2025-12-03 19:55:30.722357	\N	\N	0	0	28
310	16	20	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994631	2025-12-03 19:55:30.722359	\N	\N	0	0	28
311	16	20	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994635	2025-12-03 19:55:30.722361	\N	\N	0	0	28
312	16	20	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994639	2025-12-03 19:55:30.722363	\N	\N	0	0	28
313	16	20	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994644	2025-12-03 19:55:30.722365	\N	\N	0	0	28
314	16	20	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994648	2025-12-03 19:55:30.722367	\N	\N	0	0	28
315	16	20	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994652	2025-12-03 19:55:30.722369	\N	\N	0	0	28
316	16	20	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994656	2025-12-03 19:55:30.722371	\N	\N	0	0	28
317	16	20	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.99466	2025-12-03 19:55:30.722372	\N	\N	0	0	28
318	16	20	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994664	2025-12-03 19:55:30.722374	\N	\N	0	0	28
319	16	20	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994668	2025-12-03 19:55:30.722376	\N	\N	0	0	28
320	16	20	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994672	2025-12-03 19:55:30.722378	\N	\N	0	0	28
321	16	20	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994676	2025-12-03 19:55:30.72238	\N	\N	0	0	28
322	16	20	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.99468	2025-12-03 19:55:30.722382	\N	\N	0	0	28
323	16	20	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:10:08.994684	2025-12-03 19:55:30.722384	\N	\N	0	0	28
327	16	21	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286373	2025-12-03 19:55:39.097554	\N	\N	0	0	28
328	16	21	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286377	2025-12-03 19:55:39.09756	\N	\N	0	0	28
329	16	21	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286382	2025-12-03 19:55:39.097562	\N	\N	0	0	28
330	16	21	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286386	2025-12-03 19:55:39.097564	\N	\N	0	0	28
331	16	21	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.28639	2025-12-03 19:55:39.097565	\N	\N	0	0	28
332	16	21	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286394	2025-12-03 19:55:39.097567	\N	\N	0	0	28
333	16	21	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286398	2025-12-03 19:55:39.097569	\N	\N	0	0	28
334	16	21	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286402	2025-12-03 19:55:39.097571	\N	\N	0	0	28
335	16	21	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286406	2025-12-03 19:55:39.097573	\N	\N	0	0	28
336	16	21	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286411	2025-12-03 19:55:39.097575	\N	\N	0	0	28
337	16	21	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286415	2025-12-03 19:55:39.097577	\N	\N	0	0	28
338	16	21	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286419	2025-12-03 19:55:39.097579	\N	\N	0	0	28
339	16	21	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286423	2025-12-03 19:55:39.097581	\N	\N	0	0	28
340	16	21	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286427	2025-12-03 19:55:39.097583	\N	\N	0	0	28
341	16	21	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286431	2025-12-03 19:55:39.097585	\N	\N	0	0	28
342	16	21	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286435	2025-12-03 19:55:39.097587	\N	\N	0	0	28
343	16	21	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286439	2025-12-03 19:55:39.097589	\N	\N	0	0	28
344	16	21	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286444	2025-12-03 19:55:39.097591	\N	\N	0	0	28
345	16	21	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286448	2025-12-03 19:55:39.097593	\N	\N	0	0	28
346	16	21	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286452	2025-12-03 19:55:39.097595	\N	\N	0	0	28
347	16	21	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286456	2025-12-03 19:55:39.097597	\N	\N	0	0	28
348	16	21	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.28646	2025-12-03 19:55:39.097599	\N	\N	0	0	28
349	16	21	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286464	2025-12-03 19:55:39.097601	\N	\N	0	0	28
350	16	21	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286468	2025-12-03 19:55:39.097603	\N	\N	0	0	28
351	16	21	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286473	2025-12-03 19:55:39.097605	\N	\N	0	0	28
352	16	21	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286477	2025-12-03 19:55:39.097607	\N	\N	0	0	28
353	16	21	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286481	2025-12-03 19:55:39.097609	\N	\N	0	0	28
354	16	21	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:26:35.286485	2025-12-03 19:55:39.097611	\N	\N	0	0	28
358	16	22	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380712	2025-12-03 19:55:44.871536	\N	\N	0	0	28
359	16	22	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380716	2025-12-03 19:55:44.871543	\N	\N	0	0	28
360	16	22	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.38072	2025-12-03 19:55:44.871545	\N	\N	0	0	28
361	16	22	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380725	2025-12-03 19:55:44.871547	\N	\N	0	0	28
362	16	22	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380729	2025-12-03 19:55:44.871549	\N	\N	0	0	28
363	16	22	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380733	2025-12-03 19:55:44.87155	\N	\N	0	0	28
364	16	22	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380737	2025-12-03 19:55:44.871553	\N	\N	0	0	28
365	16	22	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380741	2025-12-03 19:55:44.871555	\N	\N	0	0	28
366	16	22	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380745	2025-12-03 19:55:44.871557	\N	\N	0	0	28
367	16	22	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380749	2025-12-03 19:55:44.871559	\N	\N	0	0	28
368	16	22	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380753	2025-12-03 19:55:44.87156	\N	\N	0	0	28
369	16	22	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380761	2025-12-03 19:55:44.871562	\N	\N	0	0	28
370	16	22	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380765	2025-12-03 19:55:44.871564	\N	\N	0	0	28
371	16	22	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380769	2025-12-03 19:55:44.871566	\N	\N	0	0	28
372	16	22	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380777	2025-12-03 19:55:44.871568	\N	\N	0	0	28
373	16	22	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380781	2025-12-03 19:55:44.87157	\N	\N	0	0	28
374	16	22	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380785	2025-12-03 19:55:44.871573	\N	\N	0	0	28
375	16	22	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.38079	2025-12-03 19:55:44.871575	\N	\N	0	0	28
376	16	22	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380794	2025-12-03 19:55:44.871577	\N	\N	0	0	28
377	16	22	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380798	2025-12-03 19:55:44.871579	\N	\N	0	0	28
378	16	22	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380802	2025-12-03 19:55:44.871581	\N	\N	0	0	28
379	16	22	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380806	2025-12-03 19:55:44.871583	\N	\N	0	0	28
380	16	22	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.38081	2025-12-03 19:55:44.871585	\N	\N	0	0	28
381	16	22	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380814	2025-12-03 19:55:44.871587	\N	\N	0	0	28
382	16	22	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380818	2025-12-03 19:55:44.871589	\N	\N	0	0	28
383	16	22	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380822	2025-12-03 19:55:44.871591	\N	\N	0	0	28
384	16	22	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.380826	2025-12-03 19:55:44.871593	\N	\N	0	0	28
385	16	22	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-02 19:33:59.38083	2025-12-03 19:55:44.871595	\N	\N	0	0	28
389	16	23	2025-12-04	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499459	2025-12-03 19:55:50.644176	\N	\N	0	0	28
390	16	23	2025-12-05	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499463	2025-12-03 19:55:50.644182	\N	\N	0	0	28
391	16	23	2025-12-06	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499467	2025-12-03 19:55:50.644184	\N	\N	0	0	28
392	16	23	2025-12-07	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499471	2025-12-03 19:55:50.644186	\N	\N	0	0	28
393	16	23	2025-12-08	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499475	2025-12-03 19:55:50.644188	\N	\N	0	0	28
394	16	23	2025-12-09	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499479	2025-12-03 19:55:50.64419	\N	\N	0	0	28
395	16	23	2025-12-10	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499483	2025-12-03 19:55:50.644192	\N	\N	0	0	28
396	16	23	2025-12-11	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499487	2025-12-03 19:55:50.644194	\N	\N	0	0	28
397	16	23	2025-12-12	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499491	2025-12-03 19:55:50.644196	\N	\N	0	0	28
398	16	23	2025-12-13	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499495	2025-12-03 19:55:50.644198	\N	\N	0	0	28
399	16	23	2025-12-14	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499499	2025-12-03 19:55:50.6442	\N	\N	0	0	28
400	16	23	2025-12-15	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499502	2025-12-03 19:55:50.644202	\N	\N	0	0	28
401	16	23	2025-12-16	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499506	2025-12-03 19:55:50.644204	\N	\N	0	0	28
402	16	23	2025-12-17	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.49951	2025-12-03 19:55:50.644206	\N	\N	0	0	28
403	16	23	2025-12-18	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499514	2025-12-03 19:55:50.644208	\N	\N	0	0	28
404	16	23	2025-12-19	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499518	2025-12-03 19:55:50.64421	\N	\N	0	0	28
405	16	23	2025-12-20	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499522	2025-12-03 19:55:50.644233	\N	\N	0	0	28
406	16	23	2025-12-21	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499526	2025-12-03 19:55:50.644235	\N	\N	0	0	28
407	16	23	2025-12-22	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.49953	2025-12-03 19:55:50.644238	\N	\N	0	0	28
408	16	23	2025-12-23	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499534	2025-12-03 19:55:50.64424	\N	\N	0	0	28
409	16	23	2025-12-24	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499538	2025-12-03 19:55:50.644242	\N	\N	0	0	28
410	16	23	2025-12-25	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499542	2025-12-03 19:55:50.644244	\N	\N	0	0	28
411	16	23	2025-12-26	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499546	2025-12-03 19:55:50.644246	\N	\N	0	0	28
412	16	23	2025-12-27	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.49955	2025-12-03 19:55:50.644248	\N	\N	0	0	28
413	16	23	2025-12-28	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499554	2025-12-03 19:55:50.64425	\N	\N	0	0	28
414	16	23	2025-12-29	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499558	2025-12-03 19:55:50.644252	\N	\N	0	0	28
415	16	23	2025-12-30	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499562	2025-12-03 19:55:50.644254	\N	\N	0	0	28
416	16	23	2025-12-31	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-02 19:35:09.499565	2025-12-03 19:55:50.644256	\N	\N	0	0	28
420	16	24	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163067	2025-12-03 19:55:56.41865	\N	\N	0	0	28
421	16	24	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163071	2025-12-03 19:55:56.418656	\N	\N	0	0	28
422	16	24	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163075	2025-12-03 19:55:56.418658	\N	\N	0	0	28
423	16	24	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163079	2025-12-03 19:55:56.41866	\N	\N	0	0	28
424	16	24	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163083	2025-12-03 19:55:56.418662	\N	\N	0	0	28
425	16	24	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163087	2025-12-03 19:55:56.418664	\N	\N	0	0	28
426	16	24	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163091	2025-12-03 19:55:56.418666	\N	\N	0	0	28
427	16	24	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163095	2025-12-03 19:55:56.418668	\N	\N	0	0	28
428	16	24	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163099	2025-12-03 19:55:56.41867	\N	\N	0	0	28
429	16	24	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163103	2025-12-03 19:55:56.418671	\N	\N	0	0	28
430	16	24	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163107	2025-12-03 19:55:56.418673	\N	\N	0	0	28
431	16	24	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163111	2025-12-03 19:55:56.418675	\N	\N	0	0	28
432	16	24	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163115	2025-12-03 19:55:56.418677	\N	\N	0	0	28
433	16	24	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163119	2025-12-03 19:55:56.418679	\N	\N	0	0	28
434	16	24	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163123	2025-12-03 19:55:56.418681	\N	\N	0	0	28
435	16	24	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163127	2025-12-03 19:55:56.418683	\N	\N	0	0	28
436	16	24	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163131	2025-12-03 19:55:56.418685	\N	\N	0	0	28
437	16	24	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163135	2025-12-03 19:55:56.418687	\N	\N	0	0	28
438	16	24	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163139	2025-12-03 19:55:56.418689	\N	\N	0	0	28
439	16	24	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163143	2025-12-03 19:55:56.418691	\N	\N	0	0	28
440	16	24	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163147	2025-12-03 19:55:56.418693	\N	\N	0	0	28
441	16	24	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163151	2025-12-03 19:55:56.418695	\N	\N	0	0	28
442	16	24	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163155	2025-12-03 19:55:56.418697	\N	\N	0	0	28
443	16	24	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163159	2025-12-03 19:55:56.418699	\N	\N	0	0	28
444	16	24	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163163	2025-12-03 19:55:56.418701	\N	\N	0	0	28
445	16	24	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163167	2025-12-03 19:55:56.418703	\N	\N	0	0	28
446	16	24	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163171	2025-12-03 19:55:56.418705	\N	\N	0	0	28
447	16	24	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-02 19:35:46.163175	2025-12-03 19:55:56.418707	\N	\N	0	0	28
451	16	25	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573344	2025-12-03 19:56:02.190269	\N	\N	0	0	28
452	16	25	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573348	2025-12-03 19:56:02.190275	\N	\N	0	0	28
453	16	25	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573353	2025-12-03 19:56:02.190277	\N	\N	0	0	28
454	16	25	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573357	2025-12-03 19:56:02.190279	\N	\N	0	0	28
455	16	25	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573361	2025-12-03 19:56:02.190281	\N	\N	0	0	28
456	16	25	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573365	2025-12-03 19:56:02.190283	\N	\N	0	0	28
457	16	25	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573369	2025-12-03 19:56:02.190285	\N	\N	0	0	28
458	16	25	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573373	2025-12-03 19:56:02.190287	\N	\N	0	0	28
459	16	25	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573378	2025-12-03 19:56:02.190289	\N	\N	0	0	28
460	16	25	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573382	2025-12-03 19:56:02.190291	\N	\N	0	0	28
461	16	25	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573386	2025-12-03 19:56:02.190293	\N	\N	0	0	28
462	16	25	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.57339	2025-12-03 19:56:02.190295	\N	\N	0	0	28
463	16	25	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573394	2025-12-03 19:56:02.190297	\N	\N	0	0	28
464	16	25	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573398	2025-12-03 19:56:02.190299	\N	\N	0	0	28
465	16	25	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573403	2025-12-03 19:56:02.190301	\N	\N	0	0	28
466	16	25	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573407	2025-12-03 19:56:02.190303	\N	\N	0	0	28
467	16	25	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573411	2025-12-03 19:56:02.190305	\N	\N	0	0	28
468	16	25	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573415	2025-12-03 19:56:02.190307	\N	\N	0	0	28
469	16	25	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.57342	2025-12-03 19:56:02.190309	\N	\N	0	0	28
470	16	25	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573424	2025-12-03 19:56:02.190311	\N	\N	0	0	28
471	16	25	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573428	2025-12-03 19:56:02.190313	\N	\N	0	0	28
472	16	25	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573432	2025-12-03 19:56:02.190315	\N	\N	0	0	28
473	16	25	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573436	2025-12-03 19:56:02.190317	\N	\N	0	0	28
478	16	25	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:37:40.573457	2025-12-03 19:56:02.190327	\N	\N	0	0	28
482	16	26	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718602	2025-12-03 19:56:07.969691	\N	\N	0	0	28
483	16	26	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718606	2025-12-03 19:56:07.969698	\N	\N	0	0	28
484	16	26	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.71861	2025-12-03 19:56:07.9697	\N	\N	0	0	28
485	16	26	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718614	2025-12-03 19:56:07.969702	\N	\N	0	0	28
486	16	26	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718618	2025-12-03 19:56:07.969704	\N	\N	0	0	28
487	16	26	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718622	2025-12-03 19:56:07.969706	\N	\N	0	0	28
488	16	26	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718626	2025-12-03 19:56:07.969708	\N	\N	0	0	28
489	16	26	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718631	2025-12-03 19:56:07.96971	\N	\N	0	0	28
490	16	26	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718635	2025-12-03 19:56:07.969712	\N	\N	0	0	28
491	16	26	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718639	2025-12-03 19:56:07.969715	\N	\N	0	0	28
492	16	26	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718643	2025-12-03 19:56:07.969717	\N	\N	0	0	28
493	16	26	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718647	2025-12-03 19:56:07.969719	\N	\N	0	0	28
494	16	26	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718652	2025-12-03 19:56:07.969721	\N	\N	0	0	28
495	16	26	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718656	2025-12-03 19:56:07.969723	\N	\N	0	0	28
496	16	26	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.71866	2025-12-03 19:56:07.969725	\N	\N	0	0	28
497	16	26	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718665	2025-12-03 19:56:07.969727	\N	\N	0	0	28
498	16	26	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718669	2025-12-03 19:56:07.969729	\N	\N	0	0	28
499	16	26	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718673	2025-12-03 19:56:07.96973	\N	\N	0	0	28
500	16	26	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718677	2025-12-03 19:56:07.969732	\N	\N	0	0	28
501	16	26	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718682	2025-12-03 19:56:07.969734	\N	\N	0	0	28
502	16	26	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718686	2025-12-03 19:56:07.969736	\N	\N	0	0	28
503	16	26	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718715	2025-12-03 19:56:07.969738	\N	\N	0	0	28
504	16	26	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.71872	2025-12-03 19:56:07.96974	\N	\N	0	0	28
505	16	26	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718724	2025-12-03 19:56:07.969742	\N	\N	0	0	28
506	16	26	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718728	2025-12-03 19:56:07.969744	\N	\N	0	0	28
507	16	26	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718732	2025-12-03 19:56:07.969746	\N	\N	0	0	28
508	16	26	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718737	2025-12-03 19:56:07.969748	\N	\N	0	0	28
509	16	26	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-02 19:38:13.718741	2025-12-03 19:56:07.96975	\N	\N	0	0	28
2415	16	28	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.54962	2025-12-03 19:56:07.969752	\N	\N	0	0	28
2416	16	28	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549629	2025-12-03 19:56:07.969754	\N	\N	0	0	28
2417	16	28	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549633	2025-12-03 19:56:07.969756	\N	\N	0	0	28
2418	16	28	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549638	2025-12-03 19:56:07.969758	\N	\N	0	0	28
2419	16	28	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549642	2025-12-03 19:56:07.96976	\N	\N	0	0	28
2420	16	28	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549646	2025-12-03 19:56:07.969762	\N	\N	0	0	28
2421	16	28	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.54965	2025-12-03 19:56:07.969763	\N	\N	0	0	28
2422	16	28	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549654	2025-12-03 19:56:07.969765	\N	\N	0	0	28
2423	16	28	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549658	2025-12-03 19:56:07.969767	\N	\N	0	0	28
2424	16	28	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549662	2025-12-03 19:56:07.969769	\N	\N	0	0	28
2425	16	28	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549666	2025-12-03 19:56:07.969771	\N	\N	0	0	28
2426	16	28	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.54967	2025-12-03 19:56:07.969773	\N	\N	0	0	28
2427	16	28	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549675	2025-12-03 19:56:07.969775	\N	\N	0	0	28
2428	16	28	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:12:21.549679	2025-12-03 19:56:07.969777	\N	\N	0	0	28
668	16	32	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832186	2025-12-03 19:56:16.346535	\N	\N	0	0	28
669	16	32	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.83219	2025-12-03 19:56:16.346541	\N	\N	0	0	28
670	16	32	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832194	2025-12-03 19:56:16.346543	\N	\N	0	0	28
671	16	32	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832198	2025-12-03 19:56:16.346545	\N	\N	0	0	28
672	16	32	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832202	2025-12-03 19:56:16.346547	\N	\N	0	0	28
673	16	32	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832206	2025-12-03 19:56:16.346549	\N	\N	0	0	28
674	16	32	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.83221	2025-12-03 19:56:16.346551	\N	\N	0	0	28
675	16	32	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832214	2025-12-03 19:56:16.346553	\N	\N	0	0	28
676	16	32	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832218	2025-12-03 19:56:16.346555	\N	\N	0	0	28
677	16	32	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832222	2025-12-03 19:56:16.346557	\N	\N	0	0	28
678	16	32	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832226	2025-12-03 19:56:16.346559	\N	\N	0	0	28
679	16	32	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.83223	2025-12-03 19:56:16.346562	\N	\N	0	0	28
680	16	32	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832234	2025-12-03 19:56:16.346564	\N	\N	0	0	28
681	16	32	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832238	2025-12-03 19:56:16.346566	\N	\N	0	0	28
682	16	32	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832242	2025-12-03 19:56:16.346568	\N	\N	0	0	28
683	16	32	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832246	2025-12-03 19:56:16.34657	\N	\N	0	0	28
684	16	32	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.83225	2025-12-03 19:56:16.346572	\N	\N	0	0	28
685	16	32	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832254	2025-12-03 19:56:16.346574	\N	\N	0	0	28
686	16	32	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832258	2025-12-03 19:56:16.346576	\N	\N	0	0	28
687	16	32	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832262	2025-12-03 19:56:16.346578	\N	\N	0	0	28
688	16	32	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832266	2025-12-03 19:56:16.34658	\N	\N	0	0	28
689	16	32	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.83227	2025-12-03 19:56:16.346582	\N	\N	0	0	28
690	16	32	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832274	2025-12-03 19:56:16.346584	\N	\N	0	0	28
691	16	32	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832278	2025-12-03 19:56:16.346586	\N	\N	0	0	28
692	16	32	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832283	2025-12-03 19:56:16.346588	\N	\N	0	0	28
693	16	32	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832287	2025-12-03 19:56:16.34659	\N	\N	0	0	28
694	16	32	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832291	2025-12-03 19:56:16.346592	\N	\N	0	0	28
695	16	32	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:25.832295	2025-12-03 19:56:16.346594	\N	\N	0	0	28
857	16	38	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.51668	2025-12-03 19:56:27.894881	\N	\N	0	0	28
858	16	38	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516685	2025-12-03 19:56:27.894883	\N	\N	0	0	28
859	16	38	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516689	2025-12-03 19:56:27.894885	\N	\N	0	0	28
860	16	38	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516693	2025-12-03 19:56:27.894887	\N	\N	0	0	28
861	16	38	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516697	2025-12-03 19:56:27.894889	\N	\N	0	0	28
862	16	38	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516701	2025-12-03 19:56:27.894891	\N	\N	0	0	28
863	16	38	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516705	2025-12-03 19:56:27.894893	\N	\N	0	0	28
864	16	38	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516709	2025-12-03 19:56:27.894895	\N	\N	0	0	28
865	16	38	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516713	2025-12-03 19:56:27.894897	\N	\N	0	0	28
866	16	38	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516717	2025-12-03 19:56:27.894899	\N	\N	0	0	28
867	16	38	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516721	2025-12-03 19:56:27.894901	\N	\N	0	0	28
868	16	38	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516725	2025-12-03 19:56:27.894903	\N	\N	0	0	28
869	16	38	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516729	2025-12-03 19:56:27.894905	\N	\N	0	0	28
870	16	38	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516733	2025-12-03 19:56:27.894907	\N	\N	0	0	28
871	16	38	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516737	2025-12-03 19:56:27.894908	\N	\N	0	0	28
872	16	38	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516741	2025-12-03 19:56:27.89491	\N	\N	0	0	28
873	16	38	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516745	2025-12-03 19:56:27.894912	\N	\N	0	0	28
874	16	38	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516749	2025-12-03 19:56:27.894914	\N	\N	0	0	28
875	16	38	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516754	2025-12-03 19:56:27.894916	\N	\N	0	0	28
876	16	38	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516758	2025-12-03 19:56:27.894918	\N	\N	0	0	28
877	16	38	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516762	2025-12-03 19:56:27.89492	\N	\N	0	0	28
878	16	38	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516766	2025-12-03 19:56:27.894922	\N	\N	0	0	28
879	16	38	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.51677	2025-12-03 19:56:27.894924	\N	\N	0	0	28
880	16	38	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516774	2025-12-03 19:56:27.894926	\N	\N	0	0	28
881	16	38	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:32.516778	2025-12-03 19:56:27.894928	\N	\N	0	0	28
2513	16	37	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313803	2025-12-03 19:56:27.894929	\N	\N	0	0	28
2514	16	37	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313811	2025-12-03 19:56:27.894931	\N	\N	0	0	28
2515	16	37	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313816	2025-12-03 19:56:27.894933	\N	\N	0	0	28
2516	16	37	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.31382	2025-12-03 19:56:27.894935	\N	\N	0	0	28
2517	16	37	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313824	2025-12-03 19:56:27.894937	\N	\N	0	0	28
2518	16	37	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313828	2025-12-03 19:56:27.894939	\N	\N	0	0	28
2519	16	37	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313832	2025-12-03 19:56:27.894941	\N	\N	0	0	28
2520	16	37	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313836	2025-12-03 19:56:27.894943	\N	\N	0	0	28
2521	16	37	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.31384	2025-12-03 19:56:27.894945	\N	\N	0	0	28
2522	16	37	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313845	2025-12-03 19:56:27.894947	\N	\N	0	0	28
2523	16	37	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313849	2025-12-03 19:56:27.894949	\N	\N	0	0	28
2524	16	37	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313853	2025-12-03 19:56:27.894951	\N	\N	0	0	28
2525	16	37	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313857	2025-12-03 19:56:27.894953	\N	\N	0	0	28
2526	16	37	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313861	2025-12-03 19:56:27.894955	\N	\N	0	0	28
2527	16	37	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313866	2025-12-03 19:56:27.894957	\N	\N	0	0	28
2528	16	37	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.31387	2025-12-03 19:56:27.894958	\N	\N	0	0	28
2529	16	37	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313874	2025-12-03 19:56:27.89496	\N	\N	0	0	28
2530	16	37	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313878	2025-12-03 19:56:27.894962	\N	\N	0	0	28
2531	16	37	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313882	2025-12-03 19:56:27.894964	\N	\N	0	0	28
2532	16	37	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313887	2025-12-03 19:56:27.894966	\N	\N	0	0	28
2533	16	37	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313891	2025-12-03 19:56:27.894968	\N	\N	0	0	28
2534	16	37	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313895	2025-12-03 19:56:27.89497	\N	\N	0	0	28
2535	16	37	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313899	2025-12-03 19:56:27.894972	\N	\N	0	0	28
2536	16	37	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313904	2025-12-03 19:56:27.894974	\N	\N	0	0	28
2537	16	37	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313908	2025-12-03 19:56:27.894976	\N	\N	0	0	28
2538	16	37	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313912	2025-12-03 19:56:27.894978	\N	\N	0	0	28
2539	16	37	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.313916	2025-12-03 19:56:27.89498	\N	\N	0	0	28
2540	16	37	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:48.31392	2025-12-03 19:56:27.894982	\N	\N	0	0	28
885	16	39	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654741	2025-12-03 19:56:38.879479	\N	\N	0	0	28
886	16	39	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654745	2025-12-03 19:56:38.879485	\N	\N	0	0	28
887	16	39	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654749	2025-12-03 19:56:38.879487	\N	\N	0	0	28
888	16	39	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654753	2025-12-03 19:56:38.879489	\N	\N	0	0	28
889	16	39	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654757	2025-12-03 19:56:38.879491	\N	\N	0	0	28
890	16	39	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654761	2025-12-03 19:56:38.879493	\N	\N	0	0	28
891	16	39	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654766	2025-12-03 19:56:38.879495	\N	\N	0	0	28
892	16	39	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.65477	2025-12-03 19:56:38.879497	\N	\N	0	0	28
893	16	39	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654774	2025-12-03 19:56:38.879499	\N	\N	0	0	28
894	16	39	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654778	2025-12-03 19:56:38.879501	\N	\N	0	0	28
895	16	39	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654782	2025-12-03 19:56:38.879503	\N	\N	0	0	28
896	16	39	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654786	2025-12-03 19:56:38.879505	\N	\N	0	0	28
897	16	39	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.65479	2025-12-03 19:56:38.879507	\N	\N	0	0	28
898	16	39	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654794	2025-12-03 19:56:38.879509	\N	\N	0	0	28
899	16	39	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654798	2025-12-03 19:56:38.879511	\N	\N	0	0	28
900	16	39	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654802	2025-12-03 19:56:38.879513	\N	\N	0	0	28
901	16	39	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654806	2025-12-03 19:56:38.879515	\N	\N	0	0	28
902	16	39	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.65481	2025-12-03 19:56:38.879517	\N	\N	0	0	28
903	16	39	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654815	2025-12-03 19:56:38.879519	\N	\N	0	0	28
904	16	39	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654819	2025-12-03 19:56:38.879521	\N	\N	0	0	28
905	16	39	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654823	2025-12-03 19:56:38.879523	\N	\N	0	0	28
906	16	39	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654827	2025-12-03 19:56:38.879525	\N	\N	0	0	28
907	16	39	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654831	2025-12-03 19:56:38.879527	\N	\N	0	0	28
908	16	39	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654836	2025-12-03 19:56:38.879529	\N	\N	0	0	28
909	16	39	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.65484	2025-12-03 19:56:38.879531	\N	\N	0	0	28
910	16	39	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654844	2025-12-03 19:56:38.879533	\N	\N	0	0	28
911	16	39	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654848	2025-12-03 19:56:38.879535	\N	\N	0	0	28
912	16	39	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:33.654853	2025-12-03 19:56:38.879537	\N	\N	0	0	28
916	16	40	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795128	2025-12-03 19:56:44.653277	\N	\N	0	0	28
917	16	40	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795132	2025-12-03 19:56:44.653283	\N	\N	0	0	28
918	16	40	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795136	2025-12-03 19:56:44.653285	\N	\N	0	0	28
919	16	40	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.79514	2025-12-03 19:56:44.653287	\N	\N	0	0	28
920	16	40	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795144	2025-12-03 19:56:44.653289	\N	\N	0	0	28
921	16	40	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795148	2025-12-03 19:56:44.653291	\N	\N	0	0	28
922	16	40	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:34.795152	2025-12-03 19:56:44.653293	\N	\N	0	0	28
982	16	42	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073176	2025-12-03 19:56:50.431052	\N	\N	0	0	28
983	16	42	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.07318	2025-12-03 19:56:50.431054	\N	\N	0	0	28
984	16	42	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073184	2025-12-03 19:56:50.431056	\N	\N	0	0	28
985	16	42	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073188	2025-12-03 19:56:50.431058	\N	\N	0	0	28
986	16	42	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073192	2025-12-03 19:56:50.431059	\N	\N	0	0	28
987	16	42	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073196	2025-12-03 19:56:50.431061	\N	\N	0	0	28
988	16	42	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.0732	2025-12-03 19:56:50.431063	\N	\N	0	0	28
989	16	42	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073204	2025-12-03 19:56:50.431065	\N	\N	0	0	28
990	16	42	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073208	2025-12-03 19:56:50.431067	\N	\N	0	0	28
991	16	42	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073212	2025-12-03 19:56:50.431069	\N	\N	0	0	28
992	16	42	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073216	2025-12-03 19:56:50.431071	\N	\N	0	0	28
993	16	42	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.07322	2025-12-03 19:56:50.431073	\N	\N	0	0	28
994	16	42	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073224	2025-12-03 19:56:50.431075	\N	\N	0	0	28
995	16	42	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073229	2025-12-03 19:56:50.431077	\N	\N	0	0	28
996	16	42	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073233	2025-12-03 19:56:50.431078	\N	\N	0	0	28
997	16	42	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:37.073237	2025-12-03 19:56:50.43108	\N	\N	0	0	28
1009	16	43	2025-12-04	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213737	2025-12-03 19:56:56.202991	\N	\N	0	0	28
1010	16	43	2025-12-05	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213741	2025-12-03 19:56:56.202997	\N	\N	0	0	28
1011	16	43	2025-12-06	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213745	2025-12-03 19:56:56.202999	\N	\N	0	0	28
1012	16	43	2025-12-07	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213749	2025-12-03 19:56:56.203001	\N	\N	0	0	28
1013	16	43	2025-12-08	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213753	2025-12-03 19:56:56.203004	\N	\N	0	0	28
1014	16	43	2025-12-09	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213757	2025-12-03 19:56:56.203006	\N	\N	0	0	28
1015	16	43	2025-12-10	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.21376	2025-12-03 19:56:56.203008	\N	\N	0	0	28
1016	16	43	2025-12-11	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213765	2025-12-03 19:56:56.20301	\N	\N	0	0	28
1017	16	43	2025-12-12	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213768	2025-12-03 19:56:56.203012	\N	\N	0	0	28
1018	16	43	2025-12-13	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213772	2025-12-03 19:56:56.203014	\N	\N	0	0	28
1019	16	43	2025-12-14	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213776	2025-12-03 19:56:56.203016	\N	\N	0	0	28
1020	16	43	2025-12-15	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.21378	2025-12-03 19:56:56.203018	\N	\N	0	0	28
1021	16	43	2025-12-16	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213785	2025-12-03 19:56:56.20302	\N	\N	0	0	28
1022	16	43	2025-12-17	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213789	2025-12-03 19:56:56.203022	\N	\N	0	0	28
1023	16	43	2025-12-18	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213793	2025-12-03 19:56:56.203024	\N	\N	0	0	28
1024	16	43	2025-12-19	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213797	2025-12-03 19:56:56.203026	\N	\N	0	0	28
1025	16	43	2025-12-20	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213801	2025-12-03 19:56:56.203028	\N	\N	0	0	28
1026	16	43	2025-12-21	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213805	2025-12-03 19:56:56.20303	\N	\N	0	0	28
1027	16	43	2025-12-22	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213809	2025-12-03 19:56:56.203032	\N	\N	0	0	28
1028	16	43	2025-12-23	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213813	2025-12-03 19:56:56.203034	\N	\N	0	0	28
1029	16	43	2025-12-24	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213817	2025-12-03 19:56:56.203036	\N	\N	0	0	28
1030	16	43	2025-12-25	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213821	2025-12-03 19:56:56.203038	\N	\N	0	0	28
1031	16	43	2025-12-26	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213825	2025-12-03 19:56:56.20304	\N	\N	0	0	28
1032	16	43	2025-12-27	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213829	2025-12-03 19:56:56.203042	\N	\N	0	0	28
1033	16	43	2025-12-28	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213833	2025-12-03 19:56:56.203044	\N	\N	0	0	28
1034	16	43	2025-12-29	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213837	2025-12-03 19:56:56.203046	\N	\N	0	0	28
1035	16	43	2025-12-30	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:57:38.213841	2025-12-03 19:56:56.203048	\N	\N	0	0	28
1058	16	44	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350973	2025-12-03 19:57:01.983308	\N	\N	0	0	28
1059	16	44	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350977	2025-12-03 19:57:01.98331	\N	\N	0	0	28
1060	16	44	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350981	2025-12-03 19:57:01.983312	\N	\N	0	0	28
1061	16	44	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350985	2025-12-03 19:57:01.983314	\N	\N	0	0	28
1062	16	44	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350989	2025-12-03 19:57:01.983317	\N	\N	0	0	28
1063	16	44	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350992	2025-12-03 19:57:01.983324	\N	\N	0	0	28
1064	16	44	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.350996	2025-12-03 19:57:01.983327	\N	\N	0	0	28
1065	16	44	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.351	2025-12-03 19:57:01.983329	\N	\N	0	0	28
1066	16	44	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.351004	2025-12-03 19:57:01.983331	\N	\N	0	0	28
1067	16	44	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:57:39.351008	2025-12-03 19:57:01.983333	\N	\N	0	0	28
1071	16	45	2025-12-04	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486846	2025-12-03 19:57:07.754874	\N	\N	0	0	28
1072	16	45	2025-12-05	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.48685	2025-12-03 19:57:07.754881	\N	\N	0	0	28
1073	16	45	2025-12-06	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486854	2025-12-03 19:57:07.754883	\N	\N	0	0	28
1074	16	45	2025-12-07	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486858	2025-12-03 19:57:07.754885	\N	\N	0	0	28
1075	16	45	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486862	2025-12-03 19:57:07.754887	\N	\N	0	0	28
1076	16	45	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486866	2025-12-03 19:57:07.754889	\N	\N	0	0	28
1077	16	45	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.48687	2025-12-03 19:57:07.754891	\N	\N	0	0	28
1078	16	45	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486874	2025-12-03 19:57:07.754893	\N	\N	0	0	28
1079	16	45	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486878	2025-12-03 19:57:07.754895	\N	\N	0	0	28
1080	16	45	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486882	2025-12-03 19:57:07.754897	\N	\N	0	0	28
1081	16	45	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486886	2025-12-03 19:57:07.754899	\N	\N	0	0	28
1082	16	45	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.48689	2025-12-03 19:57:07.754901	\N	\N	0	0	28
1083	16	45	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486894	2025-12-03 19:57:07.754903	\N	\N	0	0	28
1084	16	45	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486898	2025-12-03 19:57:07.754905	\N	\N	0	0	28
1085	16	45	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486901	2025-12-03 19:57:07.754907	\N	\N	0	0	28
1086	16	45	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486905	2025-12-03 19:57:07.754909	\N	\N	0	0	28
1087	16	45	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486909	2025-12-03 19:57:07.754911	\N	\N	0	0	28
1088	16	45	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486913	2025-12-03 19:57:07.754913	\N	\N	0	0	28
1089	16	45	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486917	2025-12-03 19:57:07.754915	\N	\N	0	0	28
1090	16	45	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486921	2025-12-03 19:57:07.754917	\N	\N	0	0	28
1091	16	45	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486925	2025-12-03 19:57:07.754919	\N	\N	0	0	28
1092	16	45	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486928	2025-12-03 19:57:07.754921	\N	\N	0	0	28
1093	16	45	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486932	2025-12-03 19:57:07.754923	\N	\N	0	0	28
1094	16	45	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486936	2025-12-03 19:57:07.754925	\N	\N	0	0	28
1095	16	45	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.48694	2025-12-03 19:57:07.754927	\N	\N	0	0	28
1096	16	45	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486944	2025-12-03 19:57:07.754929	\N	\N	0	0	28
1097	16	45	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486948	2025-12-03 19:57:07.754931	\N	\N	0	0	28
1098	16	45	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:57:40.486952	2025-12-03 19:57:07.754933	\N	\N	0	0	28
2078	16	78	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.696994	2025-12-03 19:57:13.530678	\N	\N	0	0	28
2079	16	78	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.696998	2025-12-03 19:57:13.530684	\N	\N	0	0	28
2080	16	78	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697002	2025-12-03 19:57:13.530686	\N	\N	0	0	28
2081	16	78	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697006	2025-12-03 19:57:13.530688	\N	\N	0	0	28
2082	16	78	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.69701	2025-12-03 19:57:13.53069	\N	\N	0	0	28
2083	16	78	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697014	2025-12-03 19:57:13.530692	\N	\N	0	0	28
2084	16	78	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697018	2025-12-03 19:57:13.530694	\N	\N	0	0	28
2085	16	78	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697022	2025-12-03 19:57:13.530697	\N	\N	0	0	28
2086	16	78	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697026	2025-12-03 19:57:13.530699	\N	\N	0	0	28
2087	16	78	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.69703	2025-12-03 19:57:13.5307	\N	\N	0	0	28
2088	16	78	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697034	2025-12-03 19:57:13.530702	\N	\N	0	0	28
2089	16	78	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697039	2025-12-03 19:57:13.530704	\N	\N	0	0	28
2090	16	78	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697043	2025-12-03 19:57:13.530706	\N	\N	0	0	28
2091	16	78	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697047	2025-12-03 19:57:13.530708	\N	\N	0	0	28
2092	16	78	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697051	2025-12-03 19:57:13.53071	\N	\N	0	0	28
2093	16	78	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697055	2025-12-03 19:57:13.530712	\N	\N	0	0	28
2094	16	78	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697059	2025-12-03 19:57:13.530714	\N	\N	0	0	28
2095	16	78	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697063	2025-12-03 19:57:13.530716	\N	\N	0	0	28
2096	16	78	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697067	2025-12-03 19:57:13.530718	\N	\N	0	0	28
2097	16	78	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697071	2025-12-03 19:57:13.53072	\N	\N	0	0	28
2098	16	78	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697075	2025-12-03 19:57:13.530722	\N	\N	0	0	28
2099	16	78	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697079	2025-12-03 19:57:13.530724	\N	\N	0	0	28
2100	16	78	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697083	2025-12-03 19:57:13.530726	\N	\N	0	0	28
2101	16	78	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697087	2025-12-03 19:57:13.530728	\N	\N	0	0	28
2102	16	78	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697092	2025-12-03 19:57:13.53073	\N	\N	0	0	28
2103	16	78	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697096	2025-12-03 19:57:13.530732	\N	\N	0	0	28
2104	16	78	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.6971	2025-12-03 19:57:13.530734	\N	\N	0	0	28
2105	16	78	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:17.697104	2025-12-03 19:57:13.530736	\N	\N	0	0	28
2109	16	79	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839055	2025-12-03 19:57:19.305119	\N	\N	0	0	28
2110	16	79	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839059	2025-12-03 19:57:19.305125	\N	\N	0	0	28
2111	16	79	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839063	2025-12-03 19:57:19.305128	\N	\N	0	0	28
2112	16	79	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839067	2025-12-03 19:57:19.30513	\N	\N	0	0	28
2113	16	79	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839071	2025-12-03 19:57:19.305132	\N	\N	0	0	28
2114	16	79	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839075	2025-12-03 19:57:19.305134	\N	\N	0	0	28
2115	16	79	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839079	2025-12-03 19:57:19.305136	\N	\N	0	0	28
2116	16	79	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839083	2025-12-03 19:57:19.305138	\N	\N	0	0	28
2117	16	79	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839087	2025-12-03 19:57:19.30514	\N	\N	0	0	28
2118	16	79	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.83909	2025-12-03 19:57:19.305142	\N	\N	0	0	28
2119	16	79	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839094	2025-12-03 19:57:19.305144	\N	\N	0	0	28
2120	16	79	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839098	2025-12-03 19:57:19.305146	\N	\N	0	0	28
2121	16	79	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839102	2025-12-03 19:57:19.305148	\N	\N	0	0	28
2122	16	79	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839106	2025-12-03 19:57:19.30515	\N	\N	0	0	28
2123	16	79	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.83911	2025-12-03 19:57:19.305152	\N	\N	0	0	28
2124	16	79	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839114	2025-12-03 19:57:19.305154	\N	\N	0	0	28
2125	16	79	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839118	2025-12-03 19:57:19.305156	\N	\N	0	0	28
2126	16	79	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839122	2025-12-03 19:57:19.305158	\N	\N	0	0	28
2127	16	79	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839126	2025-12-03 19:57:19.30516	\N	\N	0	0	28
2128	16	79	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839129	2025-12-03 19:57:19.305162	\N	\N	0	0	28
2129	16	79	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839133	2025-12-03 19:57:19.305164	\N	\N	0	0	28
2130	16	79	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839137	2025-12-03 19:57:19.305166	\N	\N	0	0	28
2131	16	79	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839141	2025-12-03 19:57:19.305168	\N	\N	0	0	28
2132	16	79	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839145	2025-12-03 19:57:19.30517	\N	\N	0	0	28
2133	16	79	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839148	2025-12-03 19:57:19.305172	\N	\N	0	0	28
2134	16	79	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839152	2025-12-03 19:57:19.305174	\N	\N	0	0	28
2135	16	79	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.839156	2025-12-03 19:57:19.305176	\N	\N	0	0	28
2136	16	79	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:18.83916	2025-12-03 19:57:19.305178	\N	\N	0	0	28
2140	16	80	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979189	2025-12-03 19:57:25.077202	\N	\N	0	0	28
2141	16	80	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979193	2025-12-03 19:57:25.077208	\N	\N	0	0	28
2142	16	80	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979197	2025-12-03 19:57:25.07721	\N	\N	0	0	28
2143	16	80	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979201	2025-12-03 19:57:25.077212	\N	\N	0	0	28
2144	16	80	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979205	2025-12-03 19:57:25.077214	\N	\N	0	0	28
2145	16	80	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979209	2025-12-03 19:57:25.077216	\N	\N	0	0	28
2146	16	80	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979213	2025-12-03 19:57:25.077217	\N	\N	0	0	28
2147	16	80	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979217	2025-12-03 19:57:25.077219	\N	\N	0	0	28
2148	16	80	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979221	2025-12-03 19:57:25.077221	\N	\N	0	0	28
2149	16	80	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979225	2025-12-03 19:57:25.077223	\N	\N	0	0	28
2150	16	80	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979229	2025-12-03 19:57:25.077225	\N	\N	0	0	28
2151	16	80	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979233	2025-12-03 19:57:25.077227	\N	\N	0	0	28
2152	16	80	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979237	2025-12-03 19:57:25.077229	\N	\N	0	0	28
2153	16	80	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979241	2025-12-03 19:57:25.077231	\N	\N	0	0	28
2154	16	80	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979245	2025-12-03 19:57:25.077233	\N	\N	0	0	28
2155	16	80	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979248	2025-12-03 19:57:25.077235	\N	\N	0	0	28
2156	16	80	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979252	2025-12-03 19:57:25.077236	\N	\N	0	0	28
2157	16	80	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979256	2025-12-03 19:57:25.077238	\N	\N	0	0	28
2158	16	80	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.97926	2025-12-03 19:57:25.07724	\N	\N	0	0	28
2159	16	80	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979264	2025-12-03 19:57:25.077242	\N	\N	0	0	28
2160	16	80	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979268	2025-12-03 19:57:25.077244	\N	\N	0	0	28
2161	16	80	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979272	2025-12-03 19:57:25.077246	\N	\N	0	0	28
2162	16	80	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979276	2025-12-03 19:57:25.077248	\N	\N	0	0	28
2163	16	80	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.97928	2025-12-03 19:57:25.07725	\N	\N	0	0	28
2164	16	80	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979284	2025-12-03 19:57:25.077252	\N	\N	0	0	28
2165	16	80	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979288	2025-12-03 19:57:25.077254	\N	\N	0	0	28
2166	16	80	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979292	2025-12-03 19:57:25.077256	\N	\N	0	0	28
2167	16	80	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:19.979296	2025-12-03 19:57:25.077258	\N	\N	0	0	28
2171	16	81	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118155	2025-12-03 19:57:30.854253	\N	\N	0	0	28
2172	16	81	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118159	2025-12-03 19:57:30.854258	\N	\N	0	0	28
2173	16	81	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118163	2025-12-03 19:57:30.85426	\N	\N	0	0	28
2174	16	81	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118167	2025-12-03 19:57:30.854262	\N	\N	0	0	28
2175	16	81	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118171	2025-12-03 19:57:30.854264	\N	\N	0	0	28
2176	16	81	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118175	2025-12-03 19:57:30.854266	\N	\N	0	0	28
2177	16	81	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118179	2025-12-03 19:57:30.854268	\N	\N	0	0	28
2178	16	81	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118183	2025-12-03 19:57:30.85427	\N	\N	0	0	28
2179	16	81	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118187	2025-12-03 19:57:30.854272	\N	\N	0	0	28
2180	16	81	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118191	2025-12-03 19:57:30.854274	\N	\N	0	0	28
2181	16	81	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118195	2025-12-03 19:57:30.854276	\N	\N	0	0	28
2182	16	81	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118199	2025-12-03 19:57:30.854278	\N	\N	0	0	28
2183	16	81	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118203	2025-12-03 19:57:30.85428	\N	\N	0	0	28
2184	16	81	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118207	2025-12-03 19:57:30.854282	\N	\N	0	0	28
2185	16	81	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118211	2025-12-03 19:57:30.854284	\N	\N	0	0	28
2186	16	81	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118215	2025-12-03 19:57:30.854286	\N	\N	0	0	28
2187	16	81	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118219	2025-12-03 19:57:30.854288	\N	\N	0	0	28
2188	16	81	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118223	2025-12-03 19:57:30.85429	\N	\N	0	0	28
2189	16	81	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118227	2025-12-03 19:57:30.854292	\N	\N	0	0	28
2190	16	81	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118231	2025-12-03 19:57:30.854294	\N	\N	0	0	28
2191	16	81	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118235	2025-12-03 19:57:30.854296	\N	\N	0	0	28
2192	16	81	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118238	2025-12-03 19:57:30.854298	\N	\N	0	0	28
2193	16	81	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118243	2025-12-03 19:57:30.8543	\N	\N	0	0	28
2194	16	81	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118247	2025-12-03 19:57:30.854302	\N	\N	0	0	28
2195	16	81	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.11825	2025-12-03 19:57:30.854304	\N	\N	0	0	28
2196	16	81	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118255	2025-12-03 19:57:30.854306	\N	\N	0	0	28
2197	16	81	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:21.118259	2025-12-03 19:57:30.854308	\N	\N	0	0	28
2203	16	82	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253629	2025-12-03 19:57:36.624869	\N	\N	0	0	28
2204	16	82	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253633	2025-12-03 19:57:36.624871	\N	\N	0	0	28
2205	16	82	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253637	2025-12-03 19:57:36.624873	\N	\N	0	0	28
2206	16	82	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253641	2025-12-03 19:57:36.624875	\N	\N	0	0	28
2207	16	82	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253645	2025-12-03 19:57:36.624877	\N	\N	0	0	28
2208	16	82	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253649	2025-12-03 19:57:36.624879	\N	\N	0	0	28
2209	16	82	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253653	2025-12-03 19:57:36.62488	\N	\N	0	0	28
2210	16	82	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253657	2025-12-03 19:57:36.624882	\N	\N	0	0	28
2211	16	82	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253661	2025-12-03 19:57:36.624884	\N	\N	0	0	28
2212	16	82	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253665	2025-12-03 19:57:36.624886	\N	\N	0	0	28
2213	16	82	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253669	2025-12-03 19:57:36.624888	\N	\N	0	0	28
2214	16	82	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 18:58:22.253673	2025-12-03 19:57:36.62489	\N	\N	0	0	28
2218	16	83	2025-12-04	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:23.389258	2025-12-03 19:57:39.792615	\N	\N	0	0	28
2219	16	83	2025-12-05	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:23.389262	2025-12-03 19:57:39.792621	\N	\N	0	0	28
2220	16	83	2025-12-06	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:23.389266	2025-12-03 19:57:39.792623	\N	\N	0	0	28
2221	16	83	2025-12-07	0.00	70.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:23.38927	2025-12-03 19:57:39.792625	\N	\N	0	0	28
2222	16	83	2025-12-08	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389274	2025-12-03 19:57:39.792627	\N	\N	0	0	28
2223	16	83	2025-12-09	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389278	2025-12-03 19:57:39.792629	\N	\N	0	0	28
2224	16	83	2025-12-10	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389282	2025-12-03 19:57:39.792631	\N	\N	0	0	28
2225	16	83	2025-12-11	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389285	2025-12-03 19:57:39.792633	\N	\N	0	0	28
2226	16	83	2025-12-12	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389289	2025-12-03 19:57:39.792635	\N	\N	0	0	28
2227	16	83	2025-12-13	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389294	2025-12-03 19:57:39.792637	\N	\N	0	0	28
2228	16	83	2025-12-14	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389298	2025-12-03 19:57:39.792639	\N	\N	0	0	28
2229	16	83	2025-12-15	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389302	2025-12-03 19:57:39.792642	\N	\N	0	0	28
2230	16	83	2025-12-16	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389306	2025-12-03 19:57:39.792644	\N	\N	0	0	28
2231	16	83	2025-12-17	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.38931	2025-12-03 19:57:39.792645	\N	\N	0	0	28
2232	16	83	2025-12-18	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389314	2025-12-03 19:57:39.792647	\N	\N	0	0	28
2233	16	83	2025-12-19	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389318	2025-12-03 19:57:39.792649	\N	\N	0	0	28
2234	16	83	2025-12-20	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389322	2025-12-03 19:57:39.792652	\N	\N	0	0	28
2235	16	83	2025-12-21	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389326	2025-12-03 19:57:39.792654	\N	\N	0	0	28
2236	16	83	2025-12-22	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389329	2025-12-03 19:57:39.792656	\N	\N	0	0	28
2237	16	83	2025-12-23	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389333	2025-12-03 19:57:39.792658	\N	\N	0	0	28
2238	16	83	2025-12-24	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389337	2025-12-03 19:57:39.79266	\N	\N	0	0	28
2239	16	83	2025-12-25	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389341	2025-12-03 19:57:39.792661	\N	\N	0	0	28
2240	16	83	2025-12-26	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389345	2025-12-03 19:57:39.792664	\N	\N	0	0	28
2241	16	83	2025-12-27	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389349	2025-12-03 19:57:39.792666	\N	\N	0	0	28
2242	16	83	2025-12-28	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389353	2025-12-03 19:57:39.792668	\N	\N	0	0	28
2243	16	83	2025-12-29	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389357	2025-12-03 19:57:39.79267	\N	\N	0	0	28
2244	16	83	2025-12-30	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389361	2025-12-03 19:57:39.792672	\N	\N	0	0	28
2245	16	83	2025-12-31	1.00	70.00	70.00	delivered	f	\N	\N	2025-12-03 18:58:23.389365	2025-12-03 19:57:39.792674	\N	\N	0	0	28
2249	16	84	2025-12-04	0.00	80.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:24.339251	2025-12-03 19:57:39.792675	\N	\N	0	0	28
2250	16	84	2025-12-05	0.00	80.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:24.339255	2025-12-03 19:57:39.792677	\N	\N	0	0	28
2251	16	84	2025-12-06	0.00	80.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:24.339259	2025-12-03 19:57:39.792679	\N	\N	0	0	28
2252	16	84	2025-12-07	0.00	80.00	0.00	paused	t	out of station	\N	2025-12-03 18:58:24.339262	2025-12-03 19:57:39.792681	\N	\N	0	0	28
2253	16	84	2025-12-08	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339267	2025-12-03 19:57:39.792683	\N	\N	0	0	28
2254	16	84	2025-12-09	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339271	2025-12-03 19:57:39.792685	\N	\N	0	0	28
2255	16	84	2025-12-10	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339275	2025-12-03 19:57:39.792687	\N	\N	0	0	28
2256	16	84	2025-12-11	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339279	2025-12-03 19:57:39.792689	\N	\N	0	0	28
2257	16	84	2025-12-12	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339283	2025-12-03 19:57:39.792691	\N	\N	0	0	28
2258	16	84	2025-12-13	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339287	2025-12-03 19:57:39.792693	\N	\N	0	0	28
2259	16	84	2025-12-14	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339291	2025-12-03 19:57:39.792694	\N	\N	0	0	28
2260	16	84	2025-12-15	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339295	2025-12-03 19:57:39.792696	\N	\N	0	0	28
2261	16	84	2025-12-16	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339299	2025-12-03 19:57:39.792698	\N	\N	0	0	28
2262	16	84	2025-12-17	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339303	2025-12-03 19:57:39.7927	\N	\N	0	0	28
2263	16	84	2025-12-18	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339307	2025-12-03 19:57:39.792702	\N	\N	0	0	28
2264	16	84	2025-12-19	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339311	2025-12-03 19:57:39.792704	\N	\N	0	0	28
2265	16	84	2025-12-20	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339315	2025-12-03 19:57:39.792706	\N	\N	0	0	28
2266	16	84	2025-12-21	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339319	2025-12-03 19:57:39.792708	\N	\N	0	0	28
2267	16	84	2025-12-22	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339323	2025-12-03 19:57:39.79271	\N	\N	0	0	28
2268	16	84	2025-12-23	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339327	2025-12-03 19:57:39.792712	\N	\N	0	0	28
2269	16	84	2025-12-24	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339331	2025-12-03 19:57:39.792714	\N	\N	0	0	28
2270	16	84	2025-12-25	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339336	2025-12-03 19:57:39.792716	\N	\N	0	0	28
2271	16	84	2025-12-26	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.33934	2025-12-03 19:57:39.792718	\N	\N	0	0	28
2272	16	84	2025-12-27	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339344	2025-12-03 19:57:39.79272	\N	\N	0	0	28
2273	16	84	2025-12-28	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339348	2025-12-03 19:57:39.792722	\N	\N	0	0	28
2274	16	84	2025-12-29	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339352	2025-12-03 19:57:39.792724	\N	\N	0	0	28
2275	16	84	2025-12-30	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339356	2025-12-03 19:57:39.792726	\N	\N	0	0	28
2276	16	84	2025-12-31	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 18:58:24.339359	2025-12-03 19:57:39.792728	\N	\N	0	0	28
2280	16	85	2025-12-04	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480698	2025-12-03 19:57:50.774406	\N	\N	0	0	28
2281	16	85	2025-12-05	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480702	2025-12-03 19:57:50.774411	\N	\N	0	0	28
2282	16	85	2025-12-06	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480706	2025-12-03 19:57:50.774414	\N	\N	0	0	28
2283	16	85	2025-12-07	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.48071	2025-12-03 19:57:50.774415	\N	\N	0	0	28
2284	16	85	2025-12-08	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480715	2025-12-03 19:57:50.774417	\N	\N	0	0	28
2285	16	85	2025-12-09	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480719	2025-12-03 19:57:50.774419	\N	\N	0	0	28
2286	16	85	2025-12-10	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480723	2025-12-03 19:57:50.774421	\N	\N	0	0	28
2287	16	85	2025-12-11	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480727	2025-12-03 19:57:50.774423	\N	\N	0	0	28
2288	16	85	2025-12-12	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480731	2025-12-03 19:57:50.774425	\N	\N	0	0	28
2289	16	85	2025-12-13	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480735	2025-12-03 19:57:50.774427	\N	\N	0	0	28
2290	16	85	2025-12-14	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480739	2025-12-03 19:57:50.774429	\N	\N	0	0	28
2291	16	85	2025-12-15	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480744	2025-12-03 19:57:50.774431	\N	\N	0	0	28
2292	16	85	2025-12-16	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480748	2025-12-03 19:57:50.774433	\N	\N	0	0	28
2293	16	85	2025-12-17	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480752	2025-12-03 19:57:50.774435	\N	\N	0	0	28
2294	16	85	2025-12-18	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480756	2025-12-03 19:57:50.774438	\N	\N	0	0	28
2295	16	85	2025-12-19	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.48076	2025-12-03 19:57:50.77444	\N	\N	0	0	28
2296	16	85	2025-12-20	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480764	2025-12-03 19:57:50.774442	\N	\N	0	0	28
2297	16	85	2025-12-21	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480768	2025-12-03 19:57:50.774444	\N	\N	0	0	28
2298	16	85	2025-12-22	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480772	2025-12-03 19:57:50.774446	\N	\N	0	0	28
2299	16	85	2025-12-23	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480776	2025-12-03 19:57:50.774448	\N	\N	0	0	28
2300	16	85	2025-12-24	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.48078	2025-12-03 19:57:50.77445	\N	\N	0	0	28
2301	16	85	2025-12-25	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480784	2025-12-03 19:57:50.774451	\N	\N	0	0	28
2302	16	85	2025-12-26	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480788	2025-12-03 19:57:50.774453	\N	\N	0	0	28
2303	16	85	2025-12-27	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480793	2025-12-03 19:57:50.774455	\N	\N	0	0	28
2304	16	85	2025-12-28	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480797	2025-12-03 19:57:50.774457	\N	\N	0	0	28
2305	16	85	2025-12-29	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480801	2025-12-03 19:57:50.774459	\N	\N	0	0	28
2306	16	85	2025-12-30	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480805	2025-12-03 19:57:50.774461	\N	\N	0	0	28
2307	16	85	2025-12-31	1.00	80.00	80.00	delivered	f	\N	\N	2025-12-03 18:58:25.480809	2025-12-03 19:57:50.774463	\N	\N	0	0	28
2477	16	34	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337148	2025-12-03 19:57:56.546804	\N	\N	0	0	28
2478	16	34	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337152	2025-12-03 19:57:56.546806	\N	\N	0	0	28
2479	16	34	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337156	2025-12-03 19:57:56.546808	\N	\N	0	0	28
2480	16	34	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337161	2025-12-03 19:57:56.54681	\N	\N	0	0	28
2481	16	34	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337165	2025-12-03 19:57:56.546812	\N	\N	0	0	28
2482	16	34	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337169	2025-12-03 19:57:56.546814	\N	\N	0	0	28
2483	16	34	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337173	2025-12-03 19:57:56.546816	\N	\N	0	0	28
2484	16	34	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:14:15.337178	2025-12-03 19:57:56.546818	\N	\N	0	0	28
2485	16	36	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221774	2025-12-03 19:58:02.318778	\N	\N	0	0	28
2486	16	36	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221783	2025-12-03 19:58:02.318784	\N	\N	0	0	28
2487	16	36	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221787	2025-12-03 19:58:02.318786	\N	\N	0	0	28
2488	16	36	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221792	2025-12-03 19:58:02.318789	\N	\N	0	0	28
2489	16	36	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221796	2025-12-03 19:58:02.318791	\N	\N	0	0	28
2490	16	36	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.2218	2025-12-03 19:58:02.318793	\N	\N	0	0	28
2491	16	36	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221804	2025-12-03 19:58:02.318795	\N	\N	0	0	28
2492	16	36	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221808	2025-12-03 19:58:02.318797	\N	\N	0	0	28
2493	16	36	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221812	2025-12-03 19:58:02.318799	\N	\N	0	0	28
2494	16	36	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221817	2025-12-03 19:58:02.318801	\N	\N	0	0	28
2495	16	36	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221821	2025-12-03 19:58:02.318803	\N	\N	0	0	28
2496	16	36	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221825	2025-12-03 19:58:02.318806	\N	\N	0	0	28
2497	16	36	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221829	2025-12-03 19:58:02.318808	\N	\N	0	0	28
2498	16	36	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221833	2025-12-03 19:58:02.31881	\N	\N	0	0	28
2499	16	36	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221837	2025-12-03 19:58:02.318812	\N	\N	0	0	28
2500	16	36	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221841	2025-12-03 19:58:02.318814	\N	\N	0	0	28
2501	16	36	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221846	2025-12-03 19:58:02.318816	\N	\N	0	0	28
2502	16	36	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.22185	2025-12-03 19:58:02.318818	\N	\N	0	0	28
2503	16	36	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221854	2025-12-03 19:58:02.31882	\N	\N	0	0	28
2504	16	36	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221858	2025-12-03 19:58:02.318822	\N	\N	0	0	28
2505	16	36	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221863	2025-12-03 19:58:02.318824	\N	\N	0	0	28
2506	16	36	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221867	2025-12-03 19:58:02.318826	\N	\N	0	0	28
2507	16	36	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221871	2025-12-03 19:58:02.318828	\N	\N	0	0	28
2508	16	36	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221876	2025-12-03 19:58:02.31883	\N	\N	0	0	28
2509	16	36	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.22188	2025-12-03 19:58:02.318832	\N	\N	0	0	28
2510	16	36	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221884	2025-12-03 19:58:02.318834	\N	\N	0	0	28
2511	16	36	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221888	2025-12-03 19:58:02.318836	\N	\N	0	0	28
2512	16	36	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:15:17.221892	2025-12-03 19:58:02.318838	\N	\N	0	0	28
2541	16	41	2025-12-04	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137554	2025-12-03 19:58:08.092435	\N	\N	0	0	28
2542	16	41	2025-12-05	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137562	2025-12-03 19:58:08.092441	\N	\N	0	0	28
2543	16	41	2025-12-06	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137567	2025-12-03 19:58:08.092443	\N	\N	0	0	28
2544	16	41	2025-12-07	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137571	2025-12-03 19:58:08.092445	\N	\N	0	0	28
2545	16	41	2025-12-08	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137576	2025-12-03 19:58:08.092447	\N	\N	0	0	28
2546	16	41	2025-12-09	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.13758	2025-12-03 19:58:08.092449	\N	\N	0	0	28
2547	16	41	2025-12-10	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137584	2025-12-03 19:58:08.092451	\N	\N	0	0	28
2548	16	41	2025-12-11	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137588	2025-12-03 19:58:08.092453	\N	\N	0	0	28
2549	16	41	2025-12-12	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137593	2025-12-03 19:58:08.092455	\N	\N	0	0	28
2550	16	41	2025-12-13	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137597	2025-12-03 19:58:08.092457	\N	\N	0	0	28
2551	16	41	2025-12-14	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137601	2025-12-03 19:58:08.092459	\N	\N	0	0	28
2552	16	41	2025-12-15	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137605	2025-12-03 19:58:08.092461	\N	\N	0	0	28
2553	16	41	2025-12-16	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137609	2025-12-03 19:58:08.092463	\N	\N	0	0	28
2554	16	41	2025-12-17	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137613	2025-12-03 19:58:08.092465	\N	\N	0	0	28
2555	16	41	2025-12-18	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137617	2025-12-03 19:58:08.092467	\N	\N	0	0	28
2556	16	41	2025-12-19	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137621	2025-12-03 19:58:08.092469	\N	\N	0	0	28
2557	16	41	2025-12-20	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137625	2025-12-03 19:58:08.092471	\N	\N	0	0	28
2558	16	41	2025-12-21	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.13763	2025-12-03 19:58:08.092473	\N	\N	0	0	28
2559	16	41	2025-12-22	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137634	2025-12-03 19:58:08.092475	\N	\N	0	0	28
2560	16	41	2025-12-23	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137638	2025-12-03 19:58:08.092477	\N	\N	0	0	28
2561	16	41	2025-12-24	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137642	2025-12-03 19:58:08.092479	\N	\N	0	0	28
2562	16	41	2025-12-25	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137646	2025-12-03 19:58:08.092481	\N	\N	0	0	28
2563	16	41	2025-12-26	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.13765	2025-12-03 19:58:08.092483	\N	\N	0	0	28
2564	16	41	2025-12-27	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137654	2025-12-03 19:58:08.092485	\N	\N	0	0	28
2565	16	41	2025-12-28	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137658	2025-12-03 19:58:08.092487	\N	\N	0	0	28
2566	16	41	2025-12-29	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137662	2025-12-03 19:58:08.09249	\N	\N	0	0	28
2567	16	41	2025-12-30	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.137666	2025-12-03 19:58:08.092492	\N	\N	0	0	28
2568	16	41	2025-12-31	0.50	80.00	40.00	delivered	f	\N	\N	2025-12-03 19:16:18.13767	2025-12-03 19:58:08.092494	\N	\N	0	0	28
2429	16	33	2025-12-04	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238311	2025-12-03 19:58:13.864307	\N	\N	0	0	28
2430	16	33	2025-12-05	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.23832	2025-12-03 19:58:13.864314	\N	\N	0	0	28
2431	16	33	2025-12-06	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238325	2025-12-03 19:58:13.864316	\N	\N	0	0	28
2432	16	33	2025-12-07	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.23833	2025-12-03 19:58:13.864318	\N	\N	0	0	28
2433	16	33	2025-12-08	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238334	2025-12-03 19:58:13.86432	\N	\N	0	0	28
2434	16	33	2025-12-09	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238339	2025-12-03 19:58:13.864322	\N	\N	0	0	28
2435	16	33	2025-12-10	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238343	2025-12-03 19:58:13.864324	\N	\N	0	0	28
2436	16	33	2025-12-11	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238348	2025-12-03 19:58:13.864326	\N	\N	0	0	28
2437	16	33	2025-12-12	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238352	2025-12-03 19:58:13.864328	\N	\N	0	0	28
2438	16	33	2025-12-13	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238356	2025-12-03 19:58:13.86433	\N	\N	0	0	28
2439	16	33	2025-12-14	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.23836	2025-12-03 19:58:13.864332	\N	\N	0	0	28
2440	16	33	2025-12-15	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238364	2025-12-03 19:58:13.864335	\N	\N	0	0	28
2441	16	33	2025-12-16	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238369	2025-12-03 19:58:13.864337	\N	\N	0	0	28
2442	16	33	2025-12-17	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238373	2025-12-03 19:58:13.864339	\N	\N	0	0	28
2443	16	33	2025-12-18	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238377	2025-12-03 19:58:13.864341	\N	\N	0	0	28
2444	16	33	2025-12-19	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238381	2025-12-03 19:58:13.864343	\N	\N	0	0	28
2445	16	33	2025-12-20	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238385	2025-12-03 19:58:13.864345	\N	\N	0	0	28
2446	16	33	2025-12-21	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.23839	2025-12-03 19:58:13.864354	\N	\N	0	0	28
2447	16	33	2025-12-22	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238394	2025-12-03 19:58:13.864357	\N	\N	0	0	28
2448	16	33	2025-12-23	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238398	2025-12-03 19:58:13.864359	\N	\N	0	0	28
2449	16	33	2025-12-24	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238402	2025-12-03 19:58:13.864361	\N	\N	0	0	28
2450	16	33	2025-12-25	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238406	2025-12-03 19:58:13.864363	\N	\N	0	0	28
2451	16	33	2025-12-26	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.23841	2025-12-03 19:58:13.864365	\N	\N	0	0	28
2452	16	33	2025-12-27	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238414	2025-12-03 19:58:13.864367	\N	\N	0	0	28
2453	16	33	2025-12-28	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238418	2025-12-03 19:58:13.864369	\N	\N	0	0	28
2454	16	33	2025-12-29	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238423	2025-12-03 19:58:13.864371	\N	\N	0	0	28
2455	16	33	2025-12-30	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238427	2025-12-03 19:58:13.864373	\N	\N	0	0	28
2456	16	33	2025-12-31	0.50	70.00	35.00	delivered	f	\N	\N	2025-12-03 19:13:11.238431	2025-12-03 19:58:13.864375	\N	\N	0	0	28
2632	16	92	2025-12-07	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904067	2025-12-03 19:58:19.636439	\N	\N	0	0	28
2633	16	92	2025-12-10	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904071	2025-12-03 19:58:19.636446	\N	\N	0	0	28
2634	16	92	2025-12-14	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904076	2025-12-03 19:58:19.636448	\N	\N	0	0	28
2635	16	92	2025-12-17	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.90408	2025-12-03 19:58:19.63645	\N	\N	0	0	28
2636	16	92	2025-12-21	1.50	70.00	105.00	delivered	f	\N	\N	2025-12-03 19:32:02.904084	2025-12-03 19:58:19.636452	\N	\N	0	0	28
\.


--
-- Data for Name: subscription_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.subscription_payments (id, tenant_id, subscription_id, invoice_id, payment_date, amount, payment_mode, period_start, period_end, billing_period_label, notes, created_at) FROM stdin;
3	11	3	27	2025-11-12	500.00	Cash	2025-11-12	2025-12-12	Nov 2025	\N	2025-11-12 18:39:04.819417
4	11	3	28	2025-11-12	500.00	Cash	2025-12-13	2026-01-12	Dec 2025	\N	2025-11-12 18:46:14.365832
5	11	4	\N	2025-11-13	500.00	Cash	2025-11-13	2025-12-13	Nov 2025	\N	2025-11-13 06:36:52.162971
6	11	5	\N	2025-11-13	0.00	Cash	2025-11-13	2025-12-13	Nov 2025	\N	2025-11-13 06:40:34.375924
7	11	6	29	2025-11-13	500.00	Cash	2025-11-13	2025-12-13	Nov 2025	\N	2025-11-13 10:12:48.431327
8	11	9	31	2025-11-23	1440.00	Pending	2025-11-22	2025-11-30	Nov 22 - Nov 30, 2025	\N	2025-11-23 03:59:27.689679
9	11	10	32	2025-11-23	840.00	Pending	2025-11-23	2025-11-30	Nov 23 - Nov 30, 2025	\N	2025-11-23 04:19:25.201201
10	11	11	59	2025-12-02	1040.00	Pending	2025-11-23	2025-11-30	Nov 23 - Nov 30, 2025	\N	2025-12-02 20:20:55.116863
\.


--
-- Data for Name: subscription_plans; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.subscription_plans (id, tenant_id, name, description, price, duration_days, is_active, created_at, updated_at, plan_type, unit_rate, unit_name, delivery_pattern, custom_days) FROM stdin;
1	11	Monthly Gym Membership		500.00	30	t	2025-11-12 18:21:00.644978	2025-11-12 18:21:00.644985	fixed	\N	\N	daily	\N
2	11	Quarterly Gym membership		1200.00	90	t	2025-11-12 18:35:29.240673	2025-11-12 18:35:29.24068	fixed	\N	\N	daily	\N
3	11	Yearly Gym Membership		5000.00	365	t	2025-11-12 18:36:00.308188	2025-11-12 18:36:00.308194	fixed	\N	\N	daily	\N
5	11	Daily milk Delivery		\N	30	t	2025-11-22 19:49:17.345142	2025-11-22 19:49:17.345147	metered	80.00	liter	daily	\N
10	16	buffalo Milk - 1 Liter		\N	30	t	2025-12-02 15:48:45.476226	2025-12-02 15:48:45.476232	metered	80.00	liter	daily	\N
8	16	Cow Milk- Alternate Days		\N	30	t	2025-12-02 15:47:34.232952	2025-12-02 18:52:59.872333	metered	70.00	liter	alternate	\N
9	16	Buffalo Milk - AlternateDays		\N	30	t	2025-12-02 15:48:12.154411	2025-12-02 18:54:26.078411	metered	80.00	liter	alternate	\N
11	11	cow milk custom dates - Sunday and Wednesday	cow milk custom dates - Sunday and Wednesday	\N	30	t	2025-12-02 20:14:56.541223	2025-12-02 20:14:56.541228	metered	70.00	liter	custom	2,6
7	16	Cow Milk- 1 litre		\N	30	t	2025-12-02 15:46:49.839921	2025-12-03 18:28:46.165123	metered	70.00	liter	daily	\N
6	16	Cow Milk Custom dates- Sunday and Wednesday		\N	30	f	2025-12-02 15:46:21.798569	2025-12-03 19:29:57.760757	metered	70.00	liter	custom	2,6
12	16	Cow Milk Custom dates - Sunday & Wednesday		\N	30	t	2025-12-03 19:30:58.375189	2025-12-03 19:30:58.375195	metered	70.00	liter	custom	2,6
\.


--
-- Data for Name: task_materials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_materials (id, task_id, material_name, quantity, unit, cost_per_unit, total_cost, added_by, created_at) FROM stdin;
4	9	Fans	100	pcs	0	0	15	2025-11-03 05:16:41.793252
5	9	Buld	500	pcs	0	0	15	2025-11-03 05:16:41.793259
\.


--
-- Data for Name: task_media; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_media (id, task_id, media_type, file_path, caption, uploaded_by, created_at) FROM stdin;
4	10	photo	https://pyr7htm7ayy38zig.public.blob.vercel-storage.com/task_media/20251103_042032-ErJaK9YRgSskHboSZw4fqHTKm1kwFK.jpg		13	2025-11-03 04:20:33.69567
\.


--
-- Data for Name: task_updates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_updates (id, task_id, status, notes, progress_percentage, worker_count, hours_worked, updated_by, created_at) FROM stdin;
9	7	completed	Slept well	100	1	8	13	2025-11-02 19:29:00.831069
10	8	completed	Dropped	100	1	1	13	2025-11-02 19:29:44.49912
11	10	in_progress	Checking	58	1	2	13	2025-11-03 04:20:33.888103
12	9	in_progress	Worked on stock updates	100	1	8	15	2025-11-03 05:16:42.018893
13	6	in_progress	Update ledger	26	1	5.5	15	2025-11-03 06:46:30.525511
14	6	in_progress	Update ledger	26	1	5.5	15	2025-11-03 06:46:32.887304
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tasks (id, tenant_id, task_number, title, description, priority, status, assigned_to, site_id, start_date, deadline, completed_at, created_by, created_at, updated_at) FROM stdin;
7	11	TASK-0002	go and sleep buddy	go and sleep buddy	medium	completed	13	12	2025-11-02	2025-11-02	2025-11-02 19:29:00.639611	\N	2025-11-02 19:02:53.276786	2025-11-02 19:29:00.641763
8	11	TASK-0003	drop khush	drop khush	medium	completed	13	12	2025-11-02	2025-11-03	2025-11-02 19:29:44.312306	\N	2025-11-02 19:20:24.944918	2025-11-02 19:29:44.31295
10	11	TASK-0005	check if image is working	check if image is working	medium	in_progress	13	12	2025-11-03	2025-11-03	\N	\N	2025-11-03 04:16:55.569208	2025-11-03 04:20:33.508055
9	11	TASK-0004	scrore to bata do bhai 	scrore to bata do bhai 	medium	in_progress	15	12	2025-11-02	2025-11-03	\N	\N	2025-11-02 19:32:01.381472	2025-11-03 05:16:41.507905
11	11	TASK-0006	work on first floor slap	work on first floor slap	medium	new	13	12	2025-11-03	2025-11-04	\N	\N	2025-11-03 05:41:08.206441	2025-11-03 05:41:08.206448
6	11	TASK-0001	Please update the match score buddy	Please update the match score buddy	medium	in_progress	15	12	2025-11-02	2025-11-03	\N	\N	2025-11-02 18:33:57.634624	2025-11-03 06:46:30.325203
\.


--
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tenants (id, company_name, subdomain, admin_name, admin_email, admin_phone, admin_password_hash, plan, status, trial_ends_at, subscription_ends_at, max_employees, max_sites, storage_limit_mb, features, settings, created_at, updated_at, last_login_at, email_verified, verification_token, token_expiry, total_bottles_inventory, damaged_bottles_count) FROM stdin;
17	Saumya steels	saumyasteel	Vinod Jain	amritajain15@gmail.com	9960035512	b54f23848c604c9e9323c584e2d180d1cd9bd2d58ade67da23136d10a47b553f	trial	trial	2025-12-20 06:03:50.050265	\N	50	5	1000	\N	\N	2025-11-20 06:03:50.052577	2025-11-20 06:04:13.331094	\N	t	\N	\N	0	0
12	cleanbowl	cleanbowl	Medha Mehta	medha.mehta27@gmail.com	6262070700	dfd126d4c042f3eebf175be040069d6d9a76737690bc401237a1a5ac41251290	trial	trial	2026-01-09 06:29:51.454363	\N	50	5	1000	\N	\N	2025-11-03 18:02:41.025552	2025-12-10 06:29:51.45584	2025-11-03 18:03:10.866296	t	\N	\N	0	0
18	tally professinal	tallyprof	richa jain	shobhitj909@gmail.com	9424437060	8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92	trial	trial	2025-12-31 10:57:17.340991	\N	50	5	1000	\N	\N	2025-12-01 10:57:17.343501	2025-12-01 10:57:17.343506	\N	f	PTOognHSUTtptPNQcTcqBCIVGYgirjZA4wJtguYbxtc	2025-12-02 10:57:17.340826	0	0
13	Ayush Agrawal	ayushagrawal	Ayush Agrawal	ayush.agrawal@live.com	9174901901	4316057c49ac7e49f9a0038e0ab9626ab3e0766876908b0e0c11cae4b01642ba	trial	trial	2026-01-09 13:25:21.604128	\N	50	5	1000	\N	\N	2025-11-03 19:57:19.745123	2025-12-10 13:25:21.606257	2025-11-29 12:39:02.352186	t	\N	\N	0	0
19	tally professinal	tallyproff	richa jain	shobhitj990099@gmail.com	9424437060	19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd	trial	trial	2025-12-31 11:07:27.425756	\N	50	5	1000	\N	\N	2025-12-01 11:07:27.426511	2025-12-02 16:56:49.439073	2025-12-02 16:56:49.436933	t	\N	\N	0	0
16	Anand motor	anand	Shubham Sethi	sethishubham@gmail.com	+917032018290	076ad9e1779e7528a54e3f7968ca234d484533a2e584cf411232caa604a63f7b	trial	trial	2025-12-20 05:50:55.308994	\N	50	5	1000	\N	\N	2025-11-20 05:50:55.311441	2025-12-03 18:22:29.080362	2025-12-03 18:22:29.078077	t	\N	\N	0	0
20	SW Test Projecf	swtest	Sagar Jain	sagarjain26@gmail.com	9766460248	245340c29342734a1a68fecec9c295eed22d0d1ded9de141cf4cf3692de2a1a2	trial	trial	2026-01-09 07:05:54.182691	\N	50	5	1000	\N	\N	2025-12-10 07:05:54.184957	2025-12-10 11:27:06.215409	2025-12-10 11:27:06.214587	t	\N	\N	0	0
11	Mahaveer Electricals	mahaveerelectricals	Rohit Jain	11rohit84@gmail.com	8983121201	19513fdc9da4fb72a4a05eb66917548d3c90ff94d5419e1f2363eea89dfee1dd	trial	trial	2026-01-01 15:42:34.554564	\N	50	5	1000	\N	{"gstin": "23AWZPJ0869M1ZQ", "pan": "", "address": "mahaveer Electricals 18 MG Road", "city": "Itarsi", "state": "Madhya Pradesh", "pincode": "461111", "website": "", "phone": "8983121201", "email": "11rohit84@gmail.com", "invoice_terms": "Payment due within 30 days.\\r\\nGoods once sold will not be taken back.\\r\\nSubject to Pune jurisdiction only.", "invoice_footer": "Thank you for your business!", "logo_url": "https://pyr7htm7ayy38zig.public.blob.vercel-storage.com/logos/20251123_055001-Rxn5c63wR9inW2eGmGqmZbLDLWNSh0.png"}	2025-11-02 10:46:07.737531	2025-12-11 04:01:48.623355	2025-12-11 04:01:48.620919	t	\N	\N	50	0
21	Anand Vastralaya	ayushi	Ayushi	ayushi.jain.aj71@gmail.com	9617217821	5434958a0b2e1063c91713c970f33640b56ca6e9193eac09e256e047409089f3	trial	trial	2026-01-09 11:09:03.102108	\N	50	5	1000	\N	\N	2025-12-10 11:09:03.106244	2025-12-11 04:24:41.232721	2025-12-11 04:24:41.230816	t	\N	\N	0	0
\.


--
-- Data for Name: transfers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.transfers (id, tenant_id, material_id, from_site_id, to_site_id, quantity, reason, status, initiated_by, "timestamp", completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password_hash, is_admin, active, created_at, updated_at) FROM stdin;
1	admin	240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9	t	t	2025-10-25 18:11:34.567158	2025-10-25 18:11:34.567163
\.


--
-- Data for Name: vendor_payments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vendor_payments (id, tenant_id, payment_number, payment_date, vendor_id, vendor_name, amount, payment_method, reference_number, bank_account, notes, created_by, created_at, updated_at) FROM stdin;
2	11	PAY-0001	2025-11-07	1	Rishi Jain	2000.00	cash				Admin	2025-11-07 05:55:21.485435	2025-11-07 05:55:21.485441
3	11	PAY-0002	2025-11-29	6	self	4000.00	cash		Cash in Hand		Admin	2025-11-29 19:24:43.949522	2025-11-29 19:24:43.949528
\.


--
-- Data for Name: vendors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vendors (id, tenant_id, vendor_code, name, company_name, phone, email, address, gstin, state, credit_limit, payment_terms_days, opening_balance, notes, is_active, created_at, updated_at) FROM stdin;
1	11	VEND-0001	Rishi Jain	bajaj electrical	123456789				Madhya Pradesh	200000	45	0		t	2025-11-07 05:04:54.532401	2025-11-07 05:04:54.532408
2	11	VEND-0002	Ayushi Samaiya	Anand electricals	8983121201				Maharashtra	0	30	0		t	2025-11-07 06:20:38.475772	2025-11-07 06:20:38.475778
3	11	VEND-0003	Puja						Maharashtra	0	30	0		t	2025-11-10 11:44:03.417271	2025-11-10 11:44:03.417278
4	13	VEND-0001	Bhura Patel	Dalchand Patel	9827240358		Itarsi		Madhya Pradesh	100000	60	0		t	2025-11-28 19:11:43.244695	2025-11-28 19:11:43.244701
6	11	VEN-0001	self	self					Maharashtra	0	30	0	\N	t	2025-11-29 19:24:43.334484	2025-11-29 19:24:43.33449
7	11	VEND-0004	fashion world	\N	9797979731		Itarsi		Madhya Pradesh	0	30	0	\N	t	2025-11-30 10:12:20.166436	2025-11-30 10:12:20.166443
\.


--
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: realtime; Owner: -
--

COPY realtime.schema_migrations (version, inserted_at) FROM stdin;
20211116024918	2025-12-10 14:56:13
20211116045059	2025-12-10 14:56:16
20211116050929	2025-12-10 14:56:18
20211116051442	2025-12-10 14:56:21
20211116212300	2025-12-10 14:56:23
20211116213355	2025-12-10 14:56:26
20211116213934	2025-12-10 14:56:28
20211116214523	2025-12-10 14:56:31
20211122062447	2025-12-10 14:56:34
20211124070109	2025-12-10 14:56:36
20211202204204	2025-12-10 14:56:38
20211202204605	2025-12-10 14:56:41
20211210212804	2025-12-10 14:56:48
20211228014915	2025-12-10 14:56:51
20220107221237	2025-12-10 14:56:53
20220228202821	2025-12-10 14:56:55
20220312004840	2025-12-10 14:56:58
20220603231003	2025-12-10 14:57:01
20220603232444	2025-12-10 14:57:04
20220615214548	2025-12-10 14:57:07
20220712093339	2025-12-10 14:57:09
20220908172859	2025-12-10 14:57:11
20220916233421	2025-12-10 14:57:14
20230119133233	2025-12-10 14:57:16
20230128025114	2025-12-10 14:57:20
20230128025212	2025-12-10 14:57:22
20230227211149	2025-12-10 14:57:25
20230228184745	2025-12-10 14:57:28
20230308225145	2025-12-10 14:57:30
20230328144023	2025-12-10 14:57:33
20231018144023	2025-12-10 14:57:36
20231204144023	2025-12-10 14:57:39
20231204144024	2025-12-10 14:57:42
20231204144025	2025-12-10 14:57:44
20240108234812	2025-12-10 14:57:46
20240109165339	2025-12-10 14:57:49
20240227174441	2025-12-10 14:57:53
20240311171622	2025-12-10 14:57:56
20240321100241	2025-12-10 14:58:01
20240401105812	2025-12-10 14:58:08
20240418121054	2025-12-10 14:58:11
20240523004032	2025-12-10 14:58:19
20240618124746	2025-12-10 14:58:22
20240801235015	2025-12-10 14:58:24
20240805133720	2025-12-10 14:58:26
20240827160934	2025-12-10 14:58:29
20240919163303	2025-12-10 14:58:32
20240919163305	2025-12-10 14:58:34
20241019105805	2025-12-10 14:58:36
20241030150047	2025-12-10 14:58:45
20241108114728	2025-12-10 14:58:48
20241121104152	2025-12-10 14:58:51
20241130184212	2025-12-10 14:58:53
20241220035512	2025-12-10 14:58:56
20241220123912	2025-12-10 14:58:58
20241224161212	2025-12-10 14:59:00
20250107150512	2025-12-10 14:59:03
20250110162412	2025-12-10 14:59:05
20250123174212	2025-12-10 14:59:07
20250128220012	2025-12-10 14:59:10
20250506224012	2025-12-10 14:59:12
20250523164012	2025-12-10 14:59:14
20250714121412	2025-12-10 14:59:16
20250905041441	2025-12-10 14:59:18
20251103001201	2025-12-10 14:59:21
\.


--
-- Data for Name: subscription; Type: TABLE DATA; Schema: realtime; Owner: -
--

COPY realtime.subscription (id, subscription_id, entity, filters, claims, created_at) FROM stdin;
\.


--
-- Data for Name: buckets; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.buckets (id, name, owner, created_at, updated_at, public, avif_autodetection, file_size_limit, allowed_mime_types, owner_id, type) FROM stdin;
\.


--
-- Data for Name: buckets_analytics; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.buckets_analytics (name, type, format, created_at, updated_at, id, deleted_at) FROM stdin;
\.


--
-- Data for Name: buckets_vectors; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.buckets_vectors (id, type, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: migrations; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.migrations (id, name, hash, executed_at) FROM stdin;
0	create-migrations-table	e18db593bcde2aca2a408c4d1100f6abba2195df	2025-12-10 14:56:09.056904
1	initialmigration	6ab16121fbaa08bbd11b712d05f358f9b555d777	2025-12-10 14:56:09.066389
2	storage-schema	5c7968fd083fcea04050c1b7f6253c9771b99011	2025-12-10 14:56:09.076248
3	pathtoken-column	2cb1b0004b817b29d5b0a971af16bafeede4b70d	2025-12-10 14:56:09.102822
4	add-migrations-rls	427c5b63fe1c5937495d9c635c263ee7a5905058	2025-12-10 14:56:09.154518
5	add-size-functions	79e081a1455b63666c1294a440f8ad4b1e6a7f84	2025-12-10 14:56:09.161457
6	change-column-name-in-get-size	f93f62afdf6613ee5e7e815b30d02dc990201044	2025-12-10 14:56:09.16931
7	add-rls-to-buckets	e7e7f86adbc51049f341dfe8d30256c1abca17aa	2025-12-10 14:56:09.175977
8	add-public-to-buckets	fd670db39ed65f9d08b01db09d6202503ca2bab3	2025-12-10 14:56:09.182158
9	fix-search-function	3a0af29f42e35a4d101c259ed955b67e1bee6825	2025-12-10 14:56:09.188346
10	search-files-search-function	68dc14822daad0ffac3746a502234f486182ef6e	2025-12-10 14:56:09.195639
11	add-trigger-to-auto-update-updated_at-column	7425bdb14366d1739fa8a18c83100636d74dcaa2	2025-12-10 14:56:09.202788
12	add-automatic-avif-detection-flag	8e92e1266eb29518b6a4c5313ab8f29dd0d08df9	2025-12-10 14:56:09.212893
13	add-bucket-custom-limits	cce962054138135cd9a8c4bcd531598684b25e7d	2025-12-10 14:56:09.219886
14	use-bytes-for-max-size	941c41b346f9802b411f06f30e972ad4744dad27	2025-12-10 14:56:09.227189
15	add-can-insert-object-function	934146bc38ead475f4ef4b555c524ee5d66799e5	2025-12-10 14:56:09.252783
16	add-version	76debf38d3fd07dcfc747ca49096457d95b1221b	2025-12-10 14:56:09.260982
17	drop-owner-foreign-key	f1cbb288f1b7a4c1eb8c38504b80ae2a0153d101	2025-12-10 14:56:09.268698
18	add_owner_id_column_deprecate_owner	e7a511b379110b08e2f214be852c35414749fe66	2025-12-10 14:56:09.277405
19	alter-default-value-objects-id	02e5e22a78626187e00d173dc45f58fa66a4f043	2025-12-10 14:56:09.288566
20	list-objects-with-delimiter	cd694ae708e51ba82bf012bba00caf4f3b6393b7	2025-12-10 14:56:09.296757
21	s3-multipart-uploads	8c804d4a566c40cd1e4cc5b3725a664a9303657f	2025-12-10 14:56:09.308878
22	s3-multipart-uploads-big-ints	9737dc258d2397953c9953d9b86920b8be0cdb73	2025-12-10 14:56:09.330407
23	optimize-search-function	9d7e604cddc4b56a5422dc68c9313f4a1b6f132c	2025-12-10 14:56:09.343448
24	operation-function	8312e37c2bf9e76bbe841aa5fda889206d2bf8aa	2025-12-10 14:56:09.350598
25	custom-metadata	d974c6057c3db1c1f847afa0e291e6165693b990	2025-12-10 14:56:09.356796
26	objects-prefixes	ef3f7871121cdc47a65308e6702519e853422ae2	2025-12-10 14:56:09.36312
27	search-v2	33b8f2a7ae53105f028e13e9fcda9dc4f356b4a2	2025-12-10 14:56:09.377657
28	object-bucket-name-sorting	ba85ec41b62c6a30a3f136788227ee47f311c436	2025-12-10 14:56:09.390351
29	create-prefixes	a7b1a22c0dc3ab630e3055bfec7ce7d2045c5b7b	2025-12-10 14:56:09.399385
30	update-object-levels	6c6f6cc9430d570f26284a24cf7b210599032db7	2025-12-10 14:56:09.407296
31	objects-level-index	33f1fef7ec7fea08bb892222f4f0f5d79bab5eb8	2025-12-10 14:56:09.414949
32	backward-compatible-index-on-objects	2d51eeb437a96868b36fcdfb1ddefdf13bef1647	2025-12-10 14:56:09.423635
33	backward-compatible-index-on-prefixes	fe473390e1b8c407434c0e470655945b110507bf	2025-12-10 14:56:09.436775
34	optimize-search-function-v1	82b0e469a00e8ebce495e29bfa70a0797f7ebd2c	2025-12-10 14:56:09.439159
35	add-insert-trigger-prefixes	63bb9fd05deb3dc5e9fa66c83e82b152f0caf589	2025-12-10 14:56:09.452002
36	optimise-existing-functions	81cf92eb0c36612865a18016a38496c530443899	2025-12-10 14:56:09.459096
37	add-bucket-name-length-trigger	3944135b4e3e8b22d6d4cbb568fe3b0b51df15c1	2025-12-10 14:56:09.469417
38	iceberg-catalog-flag-on-buckets	19a8bd89d5dfa69af7f222a46c726b7c41e462c5	2025-12-10 14:56:09.477916
39	add-search-v2-sort-support	39cf7d1e6bf515f4b02e41237aba845a7b492853	2025-12-10 14:56:09.492385
40	fix-prefix-race-conditions-optimized	fd02297e1c67df25a9fc110bf8c8a9af7fb06d1f	2025-12-10 14:56:09.500126
41	add-object-level-update-trigger	44c22478bf01744b2129efc480cd2edc9a7d60e9	2025-12-10 14:56:09.510678
42	rollback-prefix-triggers	f2ab4f526ab7f979541082992593938c05ee4b47	2025-12-10 14:56:09.517805
43	fix-object-level	ab837ad8f1c7d00cc0b7310e989a23388ff29fc6	2025-12-10 14:56:09.527171
44	vector-bucket-type	99c20c0ffd52bb1ff1f32fb992f3b351e3ef8fb3	2025-12-10 14:56:09.53495
45	vector-buckets	049e27196d77a7cb76497a85afae669d8b230953	2025-12-10 14:56:09.541523
46	buckets-objects-grants	fedeb96d60fefd8e02ab3ded9fbde05632f84aed	2025-12-10 14:56:09.553739
47	iceberg-table-metadata	649df56855c24d8b36dd4cc1aeb8251aa9ad42c2	2025-12-10 14:56:09.560136
48	iceberg-catalog-ids	2666dff93346e5d04e0a878416be1d5fec345d6f	2025-12-10 14:56:09.566296
\.


--
-- Data for Name: objects; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.objects (id, bucket_id, name, owner, created_at, updated_at, last_accessed_at, metadata, version, owner_id, user_metadata, level) FROM stdin;
\.


--
-- Data for Name: prefixes; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.prefixes (bucket_id, name, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: s3_multipart_uploads; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.s3_multipart_uploads (id, in_progress_size, upload_signature, bucket_id, key, version, owner_id, created_at, user_metadata) FROM stdin;
\.


--
-- Data for Name: s3_multipart_uploads_parts; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.s3_multipart_uploads_parts (id, upload_id, size, part_number, bucket_id, key, etag, owner_id, version, created_at) FROM stdin;
\.


--
-- Data for Name: vector_indexes; Type: TABLE DATA; Schema: storage; Owner: -
--

COPY storage.vector_indexes (id, name, bucket_id, data_type, dimension, distance_metric, metadata_configuration, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: secrets; Type: TABLE DATA; Schema: vault; Owner: -
--

COPY vault.secrets (id, name, description, secret, key_id, nonce, created_at, updated_at) FROM stdin;
\.


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: -
--

SELECT pg_catalog.setval('auth.refresh_tokens_id_seq', 1, false);


--
-- Name: account_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.account_transactions_id_seq', 49, true);


--
-- Name: attendance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.attendance_id_seq', 11, true);


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bank_accounts_id_seq', 12, true);


--
-- Name: commission_agents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.commission_agents_id_seq', 6, true);


--
-- Name: customer_loyalty_points_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customer_loyalty_points_id_seq', 1, true);


--
-- Name: customer_order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customer_order_items_id_seq', 17, true);


--
-- Name: customer_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customer_orders_id_seq', 17, true);


--
-- Name: customer_subscriptions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customer_subscriptions_id_seq', 93, true);


--
-- Name: customers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customers_id_seq', 97, true);


--
-- Name: delivery_challan_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.delivery_challan_items_id_seq', 6, true);


--
-- Name: delivery_challans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.delivery_challans_id_seq', 9, true);


--
-- Name: delivery_day_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.delivery_day_notes_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.employees_id_seq', 38, true);


--
-- Name: expense_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.expense_categories_id_seq', 4, true);


--
-- Name: expenses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.expenses_id_seq', 14, true);


--
-- Name: inventory_adjustment_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventory_adjustment_lines_id_seq', 1, false);


--
-- Name: inventory_adjustments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.inventory_adjustments_id_seq', 1, false);


--
-- Name: invoice_commissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.invoice_commissions_id_seq', 3, true);


--
-- Name: invoice_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.invoice_items_id_seq', 74, true);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.invoices_id_seq', 63, true);


--
-- Name: item_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.item_categories_id_seq', 86, true);


--
-- Name: item_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.item_groups_id_seq', 56, true);


--
-- Name: item_images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.item_images_id_seq', 1, false);


--
-- Name: item_stock_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.item_stock_movements_id_seq', 61, true);


--
-- Name: item_stocks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.item_stocks_id_seq', 147, true);


--
-- Name: items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.items_id_seq', 309, true);


--
-- Name: loyalty_programs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.loyalty_programs_id_seq', 11, true);


--
-- Name: loyalty_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.loyalty_transactions_id_seq', 3, true);


--
-- Name: materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.materials_id_seq', 17, true);


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.password_reset_tokens_id_seq', 4, true);


--
-- Name: payment_allocations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payment_allocations_id_seq', 2, true);


--
-- Name: payroll_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.payroll_payments_id_seq', 4, true);


--
-- Name: purchase_bill_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.purchase_bill_items_id_seq', 29, true);


--
-- Name: purchase_bills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.purchase_bills_id_seq', 29, true);


--
-- Name: purchase_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.purchase_requests_id_seq', 18, true);


--
-- Name: salary_slips_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.salary_slips_id_seq', 4, true);


--
-- Name: sales_order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sales_order_items_id_seq', 20, true);


--
-- Name: sales_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sales_orders_id_seq', 16, true);


--
-- Name: sites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sites_id_seq', 29, true);


--
-- Name: stock_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stock_movements_id_seq', 29, true);


--
-- Name: stocks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stocks_id_seq', 20, true);


--
-- Name: subscription_deliveries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.subscription_deliveries_id_seq', 2669, true);


--
-- Name: subscription_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.subscription_payments_id_seq', 10, true);


--
-- Name: subscription_plans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.subscription_plans_id_seq', 12, true);


--
-- Name: task_materials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_materials_id_seq', 5, true);


--
-- Name: task_media_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_media_id_seq', 4, true);


--
-- Name: task_updates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_updates_id_seq', 14, true);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tasks_id_seq', 11, true);


--
-- Name: tenants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tenants_id_seq', 21, true);


--
-- Name: transfers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.transfers_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: vendor_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vendor_payments_id_seq', 3, true);


--
-- Name: vendors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vendors_id_seq', 7, true);


--
-- Name: subscription_id_seq; Type: SEQUENCE SET; Schema: realtime; Owner: -
--

SELECT pg_catalog.setval('realtime.subscription_id_seq', 1, false);


--
-- Name: mfa_amr_claims amr_id_pk; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT amr_id_pk PRIMARY KEY (id);


--
-- Name: audit_log_entries audit_log_entries_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.audit_log_entries
    ADD CONSTRAINT audit_log_entries_pkey PRIMARY KEY (id);


--
-- Name: flow_state flow_state_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.flow_state
    ADD CONSTRAINT flow_state_pkey PRIMARY KEY (id);


--
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_pkey PRIMARY KEY (id);


--
-- Name: identities identities_provider_id_provider_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_provider_id_provider_unique UNIQUE (provider_id, provider);


--
-- Name: instances instances_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.instances
    ADD CONSTRAINT instances_pkey PRIMARY KEY (id);


--
-- Name: mfa_amr_claims mfa_amr_claims_session_id_authentication_method_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT mfa_amr_claims_session_id_authentication_method_pkey UNIQUE (session_id, authentication_method);


--
-- Name: mfa_challenges mfa_challenges_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_challenges
    ADD CONSTRAINT mfa_challenges_pkey PRIMARY KEY (id);


--
-- Name: mfa_factors mfa_factors_last_challenged_at_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_last_challenged_at_key UNIQUE (last_challenged_at);


--
-- Name: mfa_factors mfa_factors_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_pkey PRIMARY KEY (id);


--
-- Name: oauth_authorizations oauth_authorizations_authorization_code_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_authorization_code_key UNIQUE (authorization_code);


--
-- Name: oauth_authorizations oauth_authorizations_authorization_id_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_authorization_id_key UNIQUE (authorization_id);


--
-- Name: oauth_authorizations oauth_authorizations_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_pkey PRIMARY KEY (id);


--
-- Name: oauth_clients oauth_clients_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_clients
    ADD CONSTRAINT oauth_clients_pkey PRIMARY KEY (id);


--
-- Name: oauth_consents oauth_consents_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_pkey PRIMARY KEY (id);


--
-- Name: oauth_consents oauth_consents_user_client_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_user_client_unique UNIQUE (user_id, client_id);


--
-- Name: one_time_tokens one_time_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.one_time_tokens
    ADD CONSTRAINT one_time_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_token_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_unique UNIQUE (token);


--
-- Name: saml_providers saml_providers_entity_id_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_entity_id_key UNIQUE (entity_id);


--
-- Name: saml_providers saml_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_pkey PRIMARY KEY (id);


--
-- Name: saml_relay_states saml_relay_states_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sso_domains sso_domains_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sso_domains
    ADD CONSTRAINT sso_domains_pkey PRIMARY KEY (id);


--
-- Name: sso_providers sso_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sso_providers
    ADD CONSTRAINT sso_providers_pkey PRIMARY KEY (id);


--
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: inventory_adjustments _tenant_adjustment_number_uc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT _tenant_adjustment_number_uc UNIQUE (tenant_id, adjustment_number);


--
-- Name: item_stocks _tenant_item_site_uc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stocks
    ADD CONSTRAINT _tenant_item_site_uc UNIQUE (tenant_id, item_id, site_id);


--
-- Name: stocks _tenant_material_site_uc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT _tenant_material_site_uc UNIQUE (tenant_id, material_id, site_id);


--
-- Name: tasks _tenant_task_number_uc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT _tenant_task_number_uc UNIQUE (tenant_id, task_number);


--
-- Name: account_transactions account_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_transactions
    ADD CONSTRAINT account_transactions_pkey PRIMARY KEY (id);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- Name: bank_accounts bank_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_pkey PRIMARY KEY (id);


--
-- Name: commission_agents commission_agents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents
    ADD CONSTRAINT commission_agents_pkey PRIMARY KEY (id);


--
-- Name: customer_loyalty_points customer_loyalty_points_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_loyalty_points
    ADD CONSTRAINT customer_loyalty_points_pkey PRIMARY KEY (id);


--
-- Name: customer_order_items customer_order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_order_items
    ADD CONSTRAINT customer_order_items_pkey PRIMARY KEY (id);


--
-- Name: customer_orders customer_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_pkey PRIMARY KEY (id);


--
-- Name: customer_subscriptions customer_subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_subscriptions
    ADD CONSTRAINT customer_subscriptions_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: delivery_challan_items delivery_challan_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challan_items
    ADD CONSTRAINT delivery_challan_items_pkey PRIMARY KEY (id);


--
-- Name: delivery_challans delivery_challans_challan_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challans
    ADD CONSTRAINT delivery_challans_challan_number_key UNIQUE (challan_number);


--
-- Name: delivery_challans delivery_challans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challans
    ADD CONSTRAINT delivery_challans_pkey PRIMARY KEY (id);


--
-- Name: delivery_day_notes delivery_day_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_day_notes
    ADD CONSTRAINT delivery_day_notes_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: expense_categories expense_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_pkey PRIMARY KEY (id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: inventory_adjustment_lines inventory_adjustment_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustment_lines
    ADD CONSTRAINT inventory_adjustment_lines_pkey PRIMARY KEY (id);


--
-- Name: inventory_adjustments inventory_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_pkey PRIMARY KEY (id);


--
-- Name: invoice_commissions invoice_commissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_commissions
    ADD CONSTRAINT invoice_commissions_pkey PRIMARY KEY (id);


--
-- Name: invoice_items invoice_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: item_categories item_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_categories
    ADD CONSTRAINT item_categories_pkey PRIMARY KEY (id);


--
-- Name: item_groups item_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_groups
    ADD CONSTRAINT item_groups_pkey PRIMARY KEY (id);


--
-- Name: item_images item_images_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_images
    ADD CONSTRAINT item_images_pkey PRIMARY KEY (id);


--
-- Name: item_stock_movements item_stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements
    ADD CONSTRAINT item_stock_movements_pkey PRIMARY KEY (id);


--
-- Name: item_stocks item_stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stocks
    ADD CONSTRAINT item_stocks_pkey PRIMARY KEY (id);


--
-- Name: items items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_pkey PRIMARY KEY (id);


--
-- Name: loyalty_programs loyalty_programs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_programs
    ADD CONSTRAINT loyalty_programs_pkey PRIMARY KEY (id);


--
-- Name: loyalty_transactions loyalty_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_transactions
    ADD CONSTRAINT loyalty_transactions_pkey PRIMARY KEY (id);


--
-- Name: materials materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_key UNIQUE (token);


--
-- Name: payment_allocations payment_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT payment_allocations_pkey PRIMARY KEY (id);


--
-- Name: payroll_payments payroll_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_payments
    ADD CONSTRAINT payroll_payments_pkey PRIMARY KEY (id);


--
-- Name: purchase_bill_items purchase_bill_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bill_items
    ADD CONSTRAINT purchase_bill_items_pkey PRIMARY KEY (id);


--
-- Name: purchase_bills purchase_bills_bill_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bills
    ADD CONSTRAINT purchase_bills_bill_number_key UNIQUE (bill_number);


--
-- Name: purchase_bills purchase_bills_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bills
    ADD CONSTRAINT purchase_bills_pkey PRIMARY KEY (id);


--
-- Name: purchase_requests purchase_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_requests
    ADD CONSTRAINT purchase_requests_pkey PRIMARY KEY (id);


--
-- Name: salary_slips salary_slips_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_slips
    ADD CONSTRAINT salary_slips_pkey PRIMARY KEY (id);


--
-- Name: sales_order_items sales_order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_order_items
    ADD CONSTRAINT sales_order_items_pkey PRIMARY KEY (id);


--
-- Name: sales_orders sales_orders_order_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_order_number_key UNIQUE (order_number);


--
-- Name: sales_orders sales_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_pkey PRIMARY KEY (id);


--
-- Name: sites sites_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (id);


--
-- Name: subscription_deliveries subscription_deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries
    ADD CONSTRAINT subscription_deliveries_pkey PRIMARY KEY (id);


--
-- Name: subscription_payments subscription_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_payments
    ADD CONSTRAINT subscription_payments_pkey PRIMARY KEY (id);


--
-- Name: subscription_plans subscription_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_plans
    ADD CONSTRAINT subscription_plans_pkey PRIMARY KEY (id);


--
-- Name: task_materials task_materials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_materials
    ADD CONSTRAINT task_materials_pkey PRIMARY KEY (id);


--
-- Name: task_media task_media_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_media
    ADD CONSTRAINT task_media_pkey PRIMARY KEY (id);


--
-- Name: task_updates task_updates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT task_updates_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_admin_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_admin_email_key UNIQUE (admin_email);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: transfers transfers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_pkey PRIMARY KEY (id);


--
-- Name: customers unique_customer_code_per_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT unique_customer_code_per_tenant UNIQUE (tenant_id, customer_code);


--
-- Name: invoice_commissions unique_invoice_commission; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_commissions
    ADD CONSTRAINT unique_invoice_commission UNIQUE (invoice_id);


--
-- Name: customer_orders unique_order_number_per_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT unique_order_number_per_tenant UNIQUE (tenant_id, order_number);


--
-- Name: commission_agents unique_tenant_agent_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents
    ADD CONSTRAINT unique_tenant_agent_code UNIQUE (tenant_id, code);


--
-- Name: commission_agents unique_tenant_employee_agent; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents
    ADD CONSTRAINT unique_tenant_employee_agent UNIQUE (tenant_id, employee_id);


--
-- Name: payroll_payments unique_tenant_payroll; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_payments
    ADD CONSTRAINT unique_tenant_payroll UNIQUE (tenant_id, payment_month, payment_year);


--
-- Name: employees unique_tenant_pin; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT unique_tenant_pin UNIQUE (tenant_id, pin);


--
-- Name: vendors unique_vendor_code_per_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT unique_vendor_code_per_tenant UNIQUE (tenant_id, vendor_code);


--
-- Name: delivery_day_notes uq_delivery_day_note_tenant_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_day_notes
    ADD CONSTRAINT uq_delivery_day_note_tenant_date UNIQUE (tenant_id, note_date);


--
-- Name: items uq_items_barcode_tenant; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT uq_items_barcode_tenant UNIQUE (tenant_id, barcode);


--
-- Name: subscription_deliveries uq_subscription_delivery_date; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries
    ADD CONSTRAINT uq_subscription_delivery_date UNIQUE (subscription_id, delivery_date);


--
-- Name: items uq_tenant_sku; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT uq_tenant_sku UNIQUE (tenant_id, sku);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: vendor_payments vendor_payments_payment_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendor_payments
    ADD CONSTRAINT vendor_payments_payment_number_key UNIQUE (payment_number);


--
-- Name: vendor_payments vendor_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendor_payments
    ADD CONSTRAINT vendor_payments_pkey PRIMARY KEY (id);


--
-- Name: vendors vendors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY realtime.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id, inserted_at);


--
-- Name: subscription pk_subscription; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY realtime.subscription
    ADD CONSTRAINT pk_subscription PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY realtime.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: buckets_analytics buckets_analytics_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.buckets_analytics
    ADD CONSTRAINT buckets_analytics_pkey PRIMARY KEY (id);


--
-- Name: buckets buckets_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.buckets
    ADD CONSTRAINT buckets_pkey PRIMARY KEY (id);


--
-- Name: buckets_vectors buckets_vectors_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.buckets_vectors
    ADD CONSTRAINT buckets_vectors_pkey PRIMARY KEY (id);


--
-- Name: migrations migrations_name_key; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.migrations
    ADD CONSTRAINT migrations_name_key UNIQUE (name);


--
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.migrations
    ADD CONSTRAINT migrations_pkey PRIMARY KEY (id);


--
-- Name: objects objects_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.objects
    ADD CONSTRAINT objects_pkey PRIMARY KEY (id);


--
-- Name: prefixes prefixes_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.prefixes
    ADD CONSTRAINT prefixes_pkey PRIMARY KEY (bucket_id, level, name);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_pkey PRIMARY KEY (id);


--
-- Name: s3_multipart_uploads s3_multipart_uploads_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads
    ADD CONSTRAINT s3_multipart_uploads_pkey PRIMARY KEY (id);


--
-- Name: vector_indexes vector_indexes_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.vector_indexes
    ADD CONSTRAINT vector_indexes_pkey PRIMARY KEY (id);


--
-- Name: audit_logs_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX audit_logs_instance_id_idx ON auth.audit_log_entries USING btree (instance_id);


--
-- Name: confirmation_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX confirmation_token_idx ON auth.users USING btree (confirmation_token) WHERE ((confirmation_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_current_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX email_change_token_current_idx ON auth.users USING btree (email_change_token_current) WHERE ((email_change_token_current)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_new_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX email_change_token_new_idx ON auth.users USING btree (email_change_token_new) WHERE ((email_change_token_new)::text !~ '^[0-9 ]*$'::text);


--
-- Name: factor_id_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX factor_id_created_at_idx ON auth.mfa_factors USING btree (user_id, created_at);


--
-- Name: flow_state_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX flow_state_created_at_idx ON auth.flow_state USING btree (created_at DESC);


--
-- Name: identities_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX identities_email_idx ON auth.identities USING btree (email text_pattern_ops);


--
-- Name: INDEX identities_email_idx; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX auth.identities_email_idx IS 'Auth: Ensures indexed queries on the email column';


--
-- Name: identities_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX identities_user_id_idx ON auth.identities USING btree (user_id);


--
-- Name: idx_auth_code; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX idx_auth_code ON auth.flow_state USING btree (auth_code);


--
-- Name: idx_user_id_auth_method; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX idx_user_id_auth_method ON auth.flow_state USING btree (user_id, authentication_method);


--
-- Name: mfa_challenge_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX mfa_challenge_created_at_idx ON auth.mfa_challenges USING btree (created_at DESC);


--
-- Name: mfa_factors_user_friendly_name_unique; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX mfa_factors_user_friendly_name_unique ON auth.mfa_factors USING btree (friendly_name, user_id) WHERE (TRIM(BOTH FROM friendly_name) <> ''::text);


--
-- Name: mfa_factors_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX mfa_factors_user_id_idx ON auth.mfa_factors USING btree (user_id);


--
-- Name: oauth_auth_pending_exp_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_auth_pending_exp_idx ON auth.oauth_authorizations USING btree (expires_at) WHERE (status = 'pending'::auth.oauth_authorization_status);


--
-- Name: oauth_clients_deleted_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_clients_deleted_at_idx ON auth.oauth_clients USING btree (deleted_at);


--
-- Name: oauth_consents_active_client_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_consents_active_client_idx ON auth.oauth_consents USING btree (client_id) WHERE (revoked_at IS NULL);


--
-- Name: oauth_consents_active_user_client_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_consents_active_user_client_idx ON auth.oauth_consents USING btree (user_id, client_id) WHERE (revoked_at IS NULL);


--
-- Name: oauth_consents_user_order_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX oauth_consents_user_order_idx ON auth.oauth_consents USING btree (user_id, granted_at DESC);


--
-- Name: one_time_tokens_relates_to_hash_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX one_time_tokens_relates_to_hash_idx ON auth.one_time_tokens USING hash (relates_to);


--
-- Name: one_time_tokens_token_hash_hash_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX one_time_tokens_token_hash_hash_idx ON auth.one_time_tokens USING hash (token_hash);


--
-- Name: one_time_tokens_user_id_token_type_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX one_time_tokens_user_id_token_type_key ON auth.one_time_tokens USING btree (user_id, token_type);


--
-- Name: reauthentication_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX reauthentication_token_idx ON auth.users USING btree (reauthentication_token) WHERE ((reauthentication_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: recovery_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX recovery_token_idx ON auth.users USING btree (recovery_token) WHERE ((recovery_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: refresh_tokens_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_instance_id_idx ON auth.refresh_tokens USING btree (instance_id);


--
-- Name: refresh_tokens_instance_id_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_instance_id_user_id_idx ON auth.refresh_tokens USING btree (instance_id, user_id);


--
-- Name: refresh_tokens_parent_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_parent_idx ON auth.refresh_tokens USING btree (parent);


--
-- Name: refresh_tokens_session_id_revoked_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_session_id_revoked_idx ON auth.refresh_tokens USING btree (session_id, revoked);


--
-- Name: refresh_tokens_updated_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX refresh_tokens_updated_at_idx ON auth.refresh_tokens USING btree (updated_at DESC);


--
-- Name: saml_providers_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_providers_sso_provider_id_idx ON auth.saml_providers USING btree (sso_provider_id);


--
-- Name: saml_relay_states_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_relay_states_created_at_idx ON auth.saml_relay_states USING btree (created_at DESC);


--
-- Name: saml_relay_states_for_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_relay_states_for_email_idx ON auth.saml_relay_states USING btree (for_email);


--
-- Name: saml_relay_states_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX saml_relay_states_sso_provider_id_idx ON auth.saml_relay_states USING btree (sso_provider_id);


--
-- Name: sessions_not_after_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sessions_not_after_idx ON auth.sessions USING btree (not_after DESC);


--
-- Name: sessions_oauth_client_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sessions_oauth_client_id_idx ON auth.sessions USING btree (oauth_client_id);


--
-- Name: sessions_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sessions_user_id_idx ON auth.sessions USING btree (user_id);


--
-- Name: sso_domains_domain_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX sso_domains_domain_idx ON auth.sso_domains USING btree (lower(domain));


--
-- Name: sso_domains_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sso_domains_sso_provider_id_idx ON auth.sso_domains USING btree (sso_provider_id);


--
-- Name: sso_providers_resource_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX sso_providers_resource_id_idx ON auth.sso_providers USING btree (lower(resource_id));


--
-- Name: sso_providers_resource_id_pattern_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX sso_providers_resource_id_pattern_idx ON auth.sso_providers USING btree (resource_id text_pattern_ops);


--
-- Name: unique_phone_factor_per_user; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX unique_phone_factor_per_user ON auth.mfa_factors USING btree (user_id, phone);


--
-- Name: user_id_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX user_id_created_at_idx ON auth.sessions USING btree (user_id, created_at);


--
-- Name: users_email_partial_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX users_email_partial_key ON auth.users USING btree (email) WHERE (is_sso_user = false);


--
-- Name: INDEX users_email_partial_key; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX auth.users_email_partial_key IS 'Auth: A partial unique index that applies only when is_sso_user is false';


--
-- Name: users_instance_id_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_instance_id_email_idx ON auth.users USING btree (instance_id, lower((email)::text));


--
-- Name: users_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_instance_id_idx ON auth.users USING btree (instance_id);


--
-- Name: users_is_anonymous_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_is_anonymous_idx ON auth.users USING btree (is_anonymous);


--
-- Name: idx_account_transactions_account; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_account_transactions_account ON public.account_transactions USING btree (account_id, transaction_date DESC);


--
-- Name: idx_account_transactions_reference; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_account_transactions_reference ON public.account_transactions USING btree (reference_type, reference_id);


--
-- Name: idx_account_transactions_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_account_transactions_tenant ON public.account_transactions USING btree (tenant_id, transaction_date DESC);


--
-- Name: idx_account_transactions_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_account_transactions_type ON public.account_transactions USING btree (tenant_id, transaction_type);


--
-- Name: idx_adjustment_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_adjustment_tenant ON public.inventory_adjustments USING btree (tenant_id);


--
-- Name: idx_bank_accounts_default; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bank_accounts_default ON public.bank_accounts USING btree (tenant_id, is_default);


--
-- Name: idx_bank_accounts_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bank_accounts_tenant ON public.bank_accounts USING btree (tenant_id, is_active);


--
-- Name: idx_bank_accounts_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bank_accounts_type ON public.bank_accounts USING btree (tenant_id, account_type, is_active);


--
-- Name: idx_category_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_category_group ON public.item_categories USING btree (group_id);


--
-- Name: idx_category_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_category_tenant ON public.item_categories USING btree (tenant_id);


--
-- Name: idx_customer_order_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_order_date ON public.customer_orders USING btree (tenant_id, order_date);


--
-- Name: idx_customer_order_invoice; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_order_invoice ON public.customer_orders USING btree (invoice_id);


--
-- Name: idx_customer_order_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_order_status ON public.customer_orders USING btree (tenant_id, status);


--
-- Name: idx_customer_phone_pin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_phone_pin ON public.customers USING btree (tenant_id, phone, pin) WHERE (pin IS NOT NULL);


--
-- Name: idx_customer_subscriptions_customer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_customer ON public.customer_subscriptions USING btree (customer_id);


--
-- Name: idx_customer_subscriptions_due_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_due_date ON public.customer_subscriptions USING btree (tenant_id, current_period_end);


--
-- Name: idx_customer_subscriptions_due_soon; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_due_soon ON public.customer_subscriptions USING btree (tenant_id, status, current_period_end);


--
-- Name: idx_customer_subscriptions_period_end; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_period_end ON public.customer_subscriptions USING btree (current_period_end);


--
-- Name: idx_customer_subscriptions_plan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_plan ON public.customer_subscriptions USING btree (plan_id);


--
-- Name: idx_customer_subscriptions_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_tenant ON public.customer_subscriptions USING btree (tenant_id);


--
-- Name: idx_customer_subscriptions_tenant_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customer_subscriptions_tenant_status ON public.customer_subscriptions USING btree (tenant_id, status);


--
-- Name: idx_customers_tenant_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customers_tenant_active ON public.customers USING btree (tenant_id, is_active);


--
-- Name: idx_deliveries_assigned_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_deliveries_assigned_employee ON public.subscription_deliveries USING btree (assigned_to, delivery_date) WHERE (assigned_to IS NOT NULL);


--
-- Name: idx_delivery_challans_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_delivery_challans_tenant_date ON public.delivery_challans USING btree (tenant_id, challan_date);


--
-- Name: idx_employee_requests; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_employee_requests ON public.purchase_requests USING btree (employee_id, created_at);


--
-- Name: idx_expense_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expense_category ON public.expenses USING btree (category_id);


--
-- Name: idx_expense_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expense_tenant_date ON public.expenses USING btree (tenant_id, expense_date);


--
-- Name: idx_expenses_tenant_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expenses_tenant_category ON public.expenses USING btree (tenant_id, category_id);


--
-- Name: idx_expenses_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_expenses_tenant_date ON public.expenses USING btree (tenant_id, expense_date);


--
-- Name: idx_group_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_group_tenant ON public.item_groups USING btree (tenant_id);


--
-- Name: idx_invoice_item_invoice; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoice_item_invoice ON public.invoice_items USING btree (invoice_id);


--
-- Name: idx_invoice_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoice_number ON public.invoices USING btree (tenant_id, invoice_number);


--
-- Name: idx_invoice_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoice_tenant ON public.invoices USING btree (tenant_id, invoice_date);


--
-- Name: idx_invoices_loyalty; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoices_loyalty ON public.invoices USING btree (tenant_id, loyalty_discount) WHERE (loyalty_discount > (0)::numeric);


--
-- Name: idx_invoices_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoices_tenant_date ON public.invoices USING btree (tenant_id, invoice_date);


--
-- Name: idx_invoices_tenant_payment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoices_tenant_payment ON public.invoices USING btree (tenant_id, payment_status);


--
-- Name: idx_invoices_tenant_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_invoices_tenant_status ON public.invoices USING btree (tenant_id, status);


--
-- Name: idx_item_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_category ON public.items USING btree (category_id);


--
-- Name: idx_item_movement_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_movement_item ON public.item_stock_movements USING btree (item_id);


--
-- Name: idx_item_movement_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_movement_site ON public.item_stock_movements USING btree (site_id);


--
-- Name: idx_item_movement_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_movement_tenant ON public.item_stock_movements USING btree (tenant_id, created_at);


--
-- Name: idx_item_sku; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_sku ON public.items USING btree (sku);


--
-- Name: idx_item_stock_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_stock_item ON public.item_stocks USING btree (item_id);


--
-- Name: idx_item_stock_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_stock_tenant ON public.item_stocks USING btree (tenant_id, site_id);


--
-- Name: idx_item_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_item_tenant ON public.items USING btree (tenant_id, is_active);


--
-- Name: idx_items_barcode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_items_barcode ON public.items USING btree (tenant_id, barcode) WHERE (barcode IS NOT NULL);


--
-- Name: idx_items_mrp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_items_mrp ON public.items USING btree (mrp);


--
-- Name: idx_items_tenant_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_items_tenant_active ON public.items USING btree (tenant_id, is_active);


--
-- Name: idx_items_tenant_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_items_tenant_category ON public.items USING btree (tenant_id, category_id);


--
-- Name: idx_items_tenant_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_items_tenant_group ON public.items USING btree (tenant_id, item_group_id);


--
-- Name: idx_items_tenant_track; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_items_tenant_track ON public.items USING btree (tenant_id, track_inventory);


--
-- Name: idx_loyalty_points_customer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_loyalty_points_customer ON public.customer_loyalty_points USING btree (tenant_id, customer_id);


--
-- Name: idx_loyalty_transactions_customer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_loyalty_transactions_customer ON public.loyalty_transactions USING btree (tenant_id, customer_id, created_at DESC);


--
-- Name: idx_loyalty_transactions_invoice; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_loyalty_transactions_invoice ON public.loyalty_transactions USING btree (invoice_id);


--
-- Name: idx_loyalty_transactions_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_loyalty_transactions_type ON public.loyalty_transactions USING btree (tenant_id, transaction_type);


--
-- Name: idx_password_reset_expires; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_password_reset_expires ON public.password_reset_tokens USING btree (expires_at);


--
-- Name: idx_password_reset_token; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_password_reset_token ON public.password_reset_tokens USING btree (token) WHERE (used = false);


--
-- Name: idx_payment_allocations_bill; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_allocations_bill ON public.payment_allocations USING btree (purchase_bill_id);


--
-- Name: idx_payment_allocations_payment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payment_allocations_payment ON public.payment_allocations USING btree (payment_id);


--
-- Name: idx_payroll_payments_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_payroll_payments_tenant ON public.payroll_payments USING btree (tenant_id, payment_year, payment_month);


--
-- Name: idx_purchase_bill_items_bill; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bill_items_bill ON public.purchase_bill_items USING btree (purchase_bill_id);


--
-- Name: idx_purchase_bill_items_item; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bill_items_item ON public.purchase_bill_items USING btree (item_id);


--
-- Name: idx_purchase_bills_bill_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_bill_date ON public.purchase_bills USING btree (bill_date);


--
-- Name: idx_purchase_bills_payment_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_payment_status ON public.purchase_bills USING btree (payment_status);


--
-- Name: idx_purchase_bills_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_status ON public.purchase_bills USING btree (status);


--
-- Name: idx_purchase_bills_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_tenant ON public.purchase_bills USING btree (tenant_id);


--
-- Name: idx_purchase_bills_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_tenant_date ON public.purchase_bills USING btree (tenant_id, bill_date);


--
-- Name: idx_purchase_bills_tenant_payment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_tenant_payment ON public.purchase_bills USING btree (tenant_id, payment_status);


--
-- Name: idx_purchase_bills_tenant_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_tenant_status ON public.purchase_bills USING btree (tenant_id, status);


--
-- Name: idx_purchase_bills_vendor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_purchase_bills_vendor ON public.purchase_bills USING btree (vendor_id);


--
-- Name: idx_salary_slips_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_salary_slips_employee ON public.salary_slips USING btree (employee_id, payment_year, payment_month);


--
-- Name: idx_salary_slips_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_salary_slips_tenant ON public.salary_slips USING btree (tenant_id, payment_year, payment_month);


--
-- Name: idx_sales_orders_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sales_orders_tenant_date ON public.sales_orders USING btree (tenant_id, order_date);


--
-- Name: idx_sales_orders_tenant_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sales_orders_tenant_status ON public.sales_orders USING btree (tenant_id, status);


--
-- Name: idx_subscription_deliveries_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_deliveries_date ON public.subscription_deliveries USING btree (delivery_date);


--
-- Name: idx_subscription_deliveries_subscription; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_deliveries_subscription ON public.subscription_deliveries USING btree (subscription_id);


--
-- Name: idx_subscription_deliveries_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_deliveries_tenant ON public.subscription_deliveries USING btree (tenant_id);


--
-- Name: idx_subscription_payments_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_payments_date ON public.subscription_payments USING btree (payment_date);


--
-- Name: idx_subscription_payments_subscription; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_payments_subscription ON public.subscription_payments USING btree (subscription_id);


--
-- Name: idx_subscription_payments_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_payments_tenant ON public.subscription_payments USING btree (tenant_id);


--
-- Name: idx_subscription_payments_tenant_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_payments_tenant_date ON public.subscription_payments USING btree (tenant_id, payment_date);


--
-- Name: idx_subscription_plans_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_plans_tenant ON public.subscription_plans USING btree (tenant_id, is_active);


--
-- Name: idx_subscription_plans_tenant_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subscription_plans_tenant_active ON public.subscription_plans USING btree (tenant_id, is_active);


--
-- Name: idx_task_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_task_employee ON public.tasks USING btree (tenant_id, assigned_to);


--
-- Name: idx_task_material_task; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_task_material_task ON public.task_materials USING btree (task_id);


--
-- Name: idx_task_media_task; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_task_media_task ON public.task_media USING btree (task_id);


--
-- Name: idx_task_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_task_status ON public.tasks USING btree (tenant_id, status);


--
-- Name: idx_task_update_task; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_task_update_task ON public.task_updates USING btree (task_id);


--
-- Name: idx_tenant_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_active ON public.commission_agents USING btree (tenant_id, is_active);


--
-- Name: idx_tenant_agent_paid; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_agent_paid ON public.invoice_commissions USING btree (tenant_id, agent_id, is_paid);


--
-- Name: idx_tenant_attendance; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_attendance ON public.attendance USING btree (tenant_id, "timestamp");


--
-- Name: idx_tenant_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_employee ON public.employees USING btree (tenant_id, active);


--
-- Name: idx_tenant_employee_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_employee_date ON public.attendance USING btree (tenant_id, employee_id, "timestamp");


--
-- Name: idx_tenant_material; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_material ON public.materials USING btree (tenant_id, active);


--
-- Name: idx_tenant_movement; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_movement ON public.stock_movements USING btree (tenant_id, "timestamp");


--
-- Name: idx_tenant_paid_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_paid_date ON public.invoice_commissions USING btree (tenant_id, paid_date);


--
-- Name: idx_tenant_site; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_site ON public.sites USING btree (tenant_id, active);


--
-- Name: idx_tenant_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_status ON public.purchase_requests USING btree (tenant_id, status);


--
-- Name: idx_tenant_stock; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_stock ON public.stocks USING btree (tenant_id, site_id);


--
-- Name: idx_tenant_transfer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_transfer ON public.transfers USING btree (tenant_id, status);


--
-- Name: idx_tenant_vendor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tenant_vendor ON public.purchase_requests USING btree (tenant_id, vendor_name);


--
-- Name: idx_vendor_payments_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendor_payments_date ON public.vendor_payments USING btree (payment_date);


--
-- Name: idx_vendor_payments_tenant; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendor_payments_tenant ON public.vendor_payments USING btree (tenant_id);


--
-- Name: idx_vendor_payments_vendor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendor_payments_vendor ON public.vendor_payments USING btree (vendor_id);


--
-- Name: idx_vendors_tenant_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendors_tenant_active ON public.vendors USING btree (tenant_id, is_active);


--
-- Name: ix_account_transactions_account_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_account_transactions_account_id ON public.account_transactions USING btree (account_id);


--
-- Name: ix_account_transactions_reference_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_account_transactions_reference_id ON public.account_transactions USING btree (reference_id);


--
-- Name: ix_account_transactions_reference_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_account_transactions_reference_type ON public.account_transactions USING btree (reference_type);


--
-- Name: ix_account_transactions_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_account_transactions_tenant_id ON public.account_transactions USING btree (tenant_id);


--
-- Name: ix_account_transactions_transaction_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_account_transactions_transaction_date ON public.account_transactions USING btree (transaction_date);


--
-- Name: ix_account_transactions_transaction_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_account_transactions_transaction_type ON public.account_transactions USING btree (transaction_type);


--
-- Name: ix_attendance_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_attendance_tenant_id ON public.attendance USING btree (tenant_id);


--
-- Name: ix_bank_accounts_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bank_accounts_is_active ON public.bank_accounts USING btree (is_active);


--
-- Name: ix_bank_accounts_is_default; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bank_accounts_is_default ON public.bank_accounts USING btree (is_default);


--
-- Name: ix_bank_accounts_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bank_accounts_tenant_id ON public.bank_accounts USING btree (tenant_id);


--
-- Name: ix_employees_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_employees_tenant_id ON public.employees USING btree (tenant_id);


--
-- Name: ix_expense_categories_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_expense_categories_tenant_id ON public.expense_categories USING btree (tenant_id);


--
-- Name: ix_expenses_expense_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_expenses_expense_date ON public.expenses USING btree (expense_date);


--
-- Name: ix_expenses_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_expenses_tenant_id ON public.expenses USING btree (tenant_id);


--
-- Name: ix_inventory_adjustments_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_adjustments_tenant_id ON public.inventory_adjustments USING btree (tenant_id);


--
-- Name: ix_invoices_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_invoices_tenant_id ON public.invoices USING btree (tenant_id);


--
-- Name: ix_item_categories_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_item_categories_tenant_id ON public.item_categories USING btree (tenant_id);


--
-- Name: ix_item_groups_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_item_groups_tenant_id ON public.item_groups USING btree (tenant_id);


--
-- Name: ix_item_stock_movements_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_item_stock_movements_tenant_id ON public.item_stock_movements USING btree (tenant_id);


--
-- Name: ix_item_stocks_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_item_stocks_tenant_id ON public.item_stocks USING btree (tenant_id);


--
-- Name: ix_items_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_items_tenant_id ON public.items USING btree (tenant_id);


--
-- Name: ix_materials_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_materials_tenant_id ON public.materials USING btree (tenant_id);


--
-- Name: ix_purchase_requests_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_purchase_requests_tenant_id ON public.purchase_requests USING btree (tenant_id);


--
-- Name: ix_sites_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sites_tenant_id ON public.sites USING btree (tenant_id);


--
-- Name: ix_stock_movements_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stock_movements_tenant_id ON public.stock_movements USING btree (tenant_id);


--
-- Name: ix_stocks_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stocks_tenant_id ON public.stocks USING btree (tenant_id);


--
-- Name: ix_subscription_deliveries_delivery_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_subscription_deliveries_delivery_date ON public.subscription_deliveries USING btree (delivery_date);


--
-- Name: ix_task_materials_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_task_materials_task_id ON public.task_materials USING btree (task_id);


--
-- Name: ix_task_media_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_task_media_task_id ON public.task_media USING btree (task_id);


--
-- Name: ix_task_updates_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_task_updates_task_id ON public.task_updates USING btree (task_id);


--
-- Name: ix_tasks_assigned_to; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tasks_assigned_to ON public.tasks USING btree (assigned_to);


--
-- Name: ix_tasks_site_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tasks_site_id ON public.tasks USING btree (site_id);


--
-- Name: ix_tasks_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_tasks_tenant_id ON public.tasks USING btree (tenant_id);


--
-- Name: ix_tenants_subdomain; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_tenants_subdomain ON public.tenants USING btree (subdomain);


--
-- Name: ix_transfers_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transfers_tenant_id ON public.transfers USING btree (tenant_id);


--
-- Name: loyalty_programs_tenant_id_unique; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX loyalty_programs_tenant_id_unique ON public.loyalty_programs USING btree (tenant_id);


--
-- Name: ix_realtime_subscription_entity; Type: INDEX; Schema: realtime; Owner: -
--

CREATE INDEX ix_realtime_subscription_entity ON realtime.subscription USING btree (entity);


--
-- Name: messages_inserted_at_topic_index; Type: INDEX; Schema: realtime; Owner: -
--

CREATE INDEX messages_inserted_at_topic_index ON ONLY realtime.messages USING btree (inserted_at DESC, topic) WHERE ((extension = 'broadcast'::text) AND (private IS TRUE));


--
-- Name: subscription_subscription_id_entity_filters_key; Type: INDEX; Schema: realtime; Owner: -
--

CREATE UNIQUE INDEX subscription_subscription_id_entity_filters_key ON realtime.subscription USING btree (subscription_id, entity, filters);


--
-- Name: bname; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX bname ON storage.buckets USING btree (name);


--
-- Name: bucketid_objname; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX bucketid_objname ON storage.objects USING btree (bucket_id, name);


--
-- Name: buckets_analytics_unique_name_idx; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX buckets_analytics_unique_name_idx ON storage.buckets_analytics USING btree (name) WHERE (deleted_at IS NULL);


--
-- Name: idx_multipart_uploads_list; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_multipart_uploads_list ON storage.s3_multipart_uploads USING btree (bucket_id, key, created_at);


--
-- Name: idx_name_bucket_level_unique; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX idx_name_bucket_level_unique ON storage.objects USING btree (name COLLATE "C", bucket_id, level);


--
-- Name: idx_objects_bucket_id_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_objects_bucket_id_name ON storage.objects USING btree (bucket_id, name COLLATE "C");


--
-- Name: idx_objects_lower_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_objects_lower_name ON storage.objects USING btree ((path_tokens[level]), lower(name) text_pattern_ops, bucket_id, level);


--
-- Name: idx_prefixes_lower_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX idx_prefixes_lower_name ON storage.prefixes USING btree (bucket_id, level, ((string_to_array(name, '/'::text))[level]), lower(name) text_pattern_ops);


--
-- Name: name_prefix_search; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX name_prefix_search ON storage.objects USING btree (name text_pattern_ops);


--
-- Name: objects_bucket_id_level_idx; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX objects_bucket_id_level_idx ON storage.objects USING btree (bucket_id, level, name COLLATE "C");


--
-- Name: vector_indexes_name_bucket_id_idx; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX vector_indexes_name_bucket_id_idx ON storage.vector_indexes USING btree (name, bucket_id);


--
-- Name: subscription tr_check_filters; Type: TRIGGER; Schema: realtime; Owner: -
--

CREATE TRIGGER tr_check_filters BEFORE INSERT OR UPDATE ON realtime.subscription FOR EACH ROW EXECUTE FUNCTION realtime.subscription_check_filters();


--
-- Name: buckets enforce_bucket_name_length_trigger; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER enforce_bucket_name_length_trigger BEFORE INSERT OR UPDATE OF name ON storage.buckets FOR EACH ROW EXECUTE FUNCTION storage.enforce_bucket_name_length();


--
-- Name: objects objects_delete_delete_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER objects_delete_delete_prefix AFTER DELETE ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.delete_prefix_hierarchy_trigger();


--
-- Name: objects objects_insert_create_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER objects_insert_create_prefix BEFORE INSERT ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.objects_insert_prefix_trigger();


--
-- Name: objects objects_update_create_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER objects_update_create_prefix BEFORE UPDATE ON storage.objects FOR EACH ROW WHEN (((new.name <> old.name) OR (new.bucket_id <> old.bucket_id))) EXECUTE FUNCTION storage.objects_update_prefix_trigger();


--
-- Name: prefixes prefixes_create_hierarchy; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER prefixes_create_hierarchy BEFORE INSERT ON storage.prefixes FOR EACH ROW WHEN ((pg_trigger_depth() < 1)) EXECUTE FUNCTION storage.prefixes_insert_trigger();


--
-- Name: prefixes prefixes_delete_hierarchy; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER prefixes_delete_hierarchy AFTER DELETE ON storage.prefixes FOR EACH ROW EXECUTE FUNCTION storage.delete_prefix_hierarchy_trigger();


--
-- Name: objects update_objects_updated_at; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER update_objects_updated_at BEFORE UPDATE ON storage.objects FOR EACH ROW EXECUTE FUNCTION storage.update_updated_at_column();


--
-- Name: identities identities_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.identities
    ADD CONSTRAINT identities_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: mfa_amr_claims mfa_amr_claims_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_amr_claims
    ADD CONSTRAINT mfa_amr_claims_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;


--
-- Name: mfa_challenges mfa_challenges_auth_factor_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_challenges
    ADD CONSTRAINT mfa_challenges_auth_factor_id_fkey FOREIGN KEY (factor_id) REFERENCES auth.mfa_factors(id) ON DELETE CASCADE;


--
-- Name: mfa_factors mfa_factors_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.mfa_factors
    ADD CONSTRAINT mfa_factors_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: oauth_authorizations oauth_authorizations_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_client_id_fkey FOREIGN KEY (client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: oauth_authorizations oauth_authorizations_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_authorizations
    ADD CONSTRAINT oauth_authorizations_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: oauth_consents oauth_consents_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_client_id_fkey FOREIGN KEY (client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: oauth_consents oauth_consents_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.oauth_consents
    ADD CONSTRAINT oauth_consents_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: one_time_tokens one_time_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.one_time_tokens
    ADD CONSTRAINT one_time_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.refresh_tokens
    ADD CONSTRAINT refresh_tokens_session_id_fkey FOREIGN KEY (session_id) REFERENCES auth.sessions(id) ON DELETE CASCADE;


--
-- Name: saml_providers saml_providers_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_providers
    ADD CONSTRAINT saml_providers_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: saml_relay_states saml_relay_states_flow_state_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_flow_state_id_fkey FOREIGN KEY (flow_state_id) REFERENCES auth.flow_state(id) ON DELETE CASCADE;


--
-- Name: saml_relay_states saml_relay_states_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.saml_relay_states
    ADD CONSTRAINT saml_relay_states_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_oauth_client_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_oauth_client_id_fkey FOREIGN KEY (oauth_client_id) REFERENCES auth.oauth_clients(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: sso_domains sso_domains_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.sso_domains
    ADD CONSTRAINT sso_domains_sso_provider_id_fkey FOREIGN KEY (sso_provider_id) REFERENCES auth.sso_providers(id) ON DELETE CASCADE;


--
-- Name: account_transactions account_transactions_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_transactions
    ADD CONSTRAINT account_transactions_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.bank_accounts(id) ON DELETE CASCADE;


--
-- Name: account_transactions account_transactions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_transactions
    ADD CONSTRAINT account_transactions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: account_transactions account_transactions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.account_transactions
    ADD CONSTRAINT account_transactions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: attendance attendance_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: attendance attendance_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: attendance attendance_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: bank_accounts bank_accounts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: commission_agents commission_agents_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents
    ADD CONSTRAINT commission_agents_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: commission_agents commission_agents_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents
    ADD CONSTRAINT commission_agents_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: commission_agents commission_agents_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.commission_agents
    ADD CONSTRAINT commission_agents_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: customer_loyalty_points customer_loyalty_points_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_loyalty_points
    ADD CONSTRAINT customer_loyalty_points_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: customer_loyalty_points customer_loyalty_points_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_loyalty_points
    ADD CONSTRAINT customer_loyalty_points_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: customer_order_items customer_order_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_order_items
    ADD CONSTRAINT customer_order_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: customer_order_items customer_order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_order_items
    ADD CONSTRAINT customer_order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.customer_orders(id);


--
-- Name: customer_orders customer_orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: customer_orders customer_orders_fulfilled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_fulfilled_by_fkey FOREIGN KEY (fulfilled_by) REFERENCES public.users(id);


--
-- Name: customer_orders customer_orders_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id) ON DELETE SET NULL;


--
-- Name: customer_orders customer_orders_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_orders
    ADD CONSTRAINT customer_orders_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: customer_subscriptions customer_subscriptions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_subscriptions
    ADD CONSTRAINT customer_subscriptions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: customer_subscriptions customer_subscriptions_plan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_subscriptions
    ADD CONSTRAINT customer_subscriptions_plan_id_fkey FOREIGN KEY (plan_id) REFERENCES public.subscription_plans(id);


--
-- Name: customer_subscriptions customer_subscriptions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customer_subscriptions
    ADD CONSTRAINT customer_subscriptions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: customers customers_default_delivery_employee_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_default_delivery_employee_fkey FOREIGN KEY (default_delivery_employee) REFERENCES public.employees(id);


--
-- Name: customers customers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: delivery_challan_items delivery_challan_items_delivery_challan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challan_items
    ADD CONSTRAINT delivery_challan_items_delivery_challan_id_fkey FOREIGN KEY (delivery_challan_id) REFERENCES public.delivery_challans(id) ON DELETE CASCADE;


--
-- Name: delivery_challan_items delivery_challan_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challan_items
    ADD CONSTRAINT delivery_challan_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: delivery_challan_items delivery_challan_items_sales_order_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challan_items
    ADD CONSTRAINT delivery_challan_items_sales_order_item_id_fkey FOREIGN KEY (sales_order_item_id) REFERENCES public.sales_order_items(id);


--
-- Name: delivery_challan_items delivery_challan_items_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challan_items
    ADD CONSTRAINT delivery_challan_items_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: delivery_challans delivery_challans_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challans
    ADD CONSTRAINT delivery_challans_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: delivery_challans delivery_challans_sales_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challans
    ADD CONSTRAINT delivery_challans_sales_order_id_fkey FOREIGN KEY (sales_order_id) REFERENCES public.sales_orders(id);


--
-- Name: delivery_challans delivery_challans_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_challans
    ADD CONSTRAINT delivery_challans_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: delivery_day_notes delivery_day_notes_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.delivery_day_notes
    ADD CONSTRAINT delivery_day_notes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: employees employees_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: employees employees_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: expense_categories expense_categories_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expense_categories
    ADD CONSTRAINT expense_categories_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: expenses expenses_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.expense_categories(id);


--
-- Name: expenses expenses_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expenses
    ADD CONSTRAINT expenses_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: inventory_adjustment_lines inventory_adjustment_lines_adjustment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustment_lines
    ADD CONSTRAINT inventory_adjustment_lines_adjustment_id_fkey FOREIGN KEY (adjustment_id) REFERENCES public.inventory_adjustments(id);


--
-- Name: inventory_adjustment_lines inventory_adjustment_lines_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustment_lines
    ADD CONSTRAINT inventory_adjustment_lines_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: inventory_adjustment_lines inventory_adjustment_lines_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustment_lines
    ADD CONSTRAINT inventory_adjustment_lines_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: inventory_adjustments inventory_adjustments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_adjustments
    ADD CONSTRAINT inventory_adjustments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: invoice_commissions invoice_commissions_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_commissions
    ADD CONSTRAINT invoice_commissions_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.commission_agents(id);


--
-- Name: invoice_commissions invoice_commissions_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_commissions
    ADD CONSTRAINT invoice_commissions_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: invoice_commissions invoice_commissions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_commissions
    ADD CONSTRAINT invoice_commissions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: invoice_items invoice_items_delivery_challan_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_delivery_challan_item_id_fkey FOREIGN KEY (delivery_challan_item_id) REFERENCES public.delivery_challan_items(id);


--
-- Name: invoice_items invoice_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: invoice_items invoice_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: invoice_items invoice_items_sales_order_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_sales_order_item_id_fkey FOREIGN KEY (sales_order_item_id) REFERENCES public.sales_order_items(id);


--
-- Name: invoices invoices_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: invoices invoices_delivery_challan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_delivery_challan_id_fkey FOREIGN KEY (delivery_challan_id) REFERENCES public.delivery_challans(id);


--
-- Name: invoices invoices_sales_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_sales_order_id_fkey FOREIGN KEY (sales_order_id) REFERENCES public.sales_orders(id);


--
-- Name: invoices invoices_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: item_categories item_categories_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_categories
    ADD CONSTRAINT item_categories_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.item_groups(id);


--
-- Name: item_categories item_categories_parent_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_categories
    ADD CONSTRAINT item_categories_parent_category_id_fkey FOREIGN KEY (parent_category_id) REFERENCES public.item_categories(id);


--
-- Name: item_categories item_categories_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_categories
    ADD CONSTRAINT item_categories_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: item_groups item_groups_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_groups
    ADD CONSTRAINT item_groups_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: item_images item_images_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_images
    ADD CONSTRAINT item_images_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: item_stock_movements item_stock_movements_from_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements
    ADD CONSTRAINT item_stock_movements_from_site_id_fkey FOREIGN KEY (from_site_id) REFERENCES public.sites(id);


--
-- Name: item_stock_movements item_stock_movements_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements
    ADD CONSTRAINT item_stock_movements_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: item_stock_movements item_stock_movements_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements
    ADD CONSTRAINT item_stock_movements_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: item_stock_movements item_stock_movements_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements
    ADD CONSTRAINT item_stock_movements_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: item_stock_movements item_stock_movements_to_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stock_movements
    ADD CONSTRAINT item_stock_movements_to_site_id_fkey FOREIGN KEY (to_site_id) REFERENCES public.sites(id);


--
-- Name: item_stocks item_stocks_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stocks
    ADD CONSTRAINT item_stocks_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: item_stocks item_stocks_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stocks
    ADD CONSTRAINT item_stocks_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: item_stocks item_stocks_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.item_stocks
    ADD CONSTRAINT item_stocks_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: items items_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.item_categories(id);


--
-- Name: items items_item_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_item_group_id_fkey FOREIGN KEY (item_group_id) REFERENCES public.item_groups(id);


--
-- Name: items items_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.items
    ADD CONSTRAINT items_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: loyalty_programs loyalty_programs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_programs
    ADD CONSTRAINT loyalty_programs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: loyalty_transactions loyalty_transactions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_transactions
    ADD CONSTRAINT loyalty_transactions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: loyalty_transactions loyalty_transactions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_transactions
    ADD CONSTRAINT loyalty_transactions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: loyalty_transactions loyalty_transactions_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_transactions
    ADD CONSTRAINT loyalty_transactions_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: loyalty_transactions loyalty_transactions_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.loyalty_transactions
    ADD CONSTRAINT loyalty_transactions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: materials materials_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.materials
    ADD CONSTRAINT materials_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: password_reset_tokens password_reset_tokens_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: payment_allocations payment_allocations_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT payment_allocations_payment_id_fkey FOREIGN KEY (payment_id) REFERENCES public.vendor_payments(id);


--
-- Name: payment_allocations payment_allocations_purchase_bill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payment_allocations
    ADD CONSTRAINT payment_allocations_purchase_bill_id_fkey FOREIGN KEY (purchase_bill_id) REFERENCES public.purchase_bills(id);


--
-- Name: payroll_payments payroll_payments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_payments
    ADD CONSTRAINT payroll_payments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: payroll_payments payroll_payments_paid_from_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_payments
    ADD CONSTRAINT payroll_payments_paid_from_account_id_fkey FOREIGN KEY (paid_from_account_id) REFERENCES public.bank_accounts(id);


--
-- Name: payroll_payments payroll_payments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.payroll_payments
    ADD CONSTRAINT payroll_payments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: purchase_bill_items purchase_bill_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bill_items
    ADD CONSTRAINT purchase_bill_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: purchase_bill_items purchase_bill_items_purchase_bill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bill_items
    ADD CONSTRAINT purchase_bill_items_purchase_bill_id_fkey FOREIGN KEY (purchase_bill_id) REFERENCES public.purchase_bills(id);


--
-- Name: purchase_bill_items purchase_bill_items_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bill_items
    ADD CONSTRAINT purchase_bill_items_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: purchase_bill_items purchase_bill_items_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bill_items
    ADD CONSTRAINT purchase_bill_items_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: purchase_bills purchase_bills_purchase_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bills
    ADD CONSTRAINT purchase_bills_purchase_request_id_fkey FOREIGN KEY (purchase_request_id) REFERENCES public.purchase_requests(id);


--
-- Name: purchase_bills purchase_bills_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bills
    ADD CONSTRAINT purchase_bills_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: purchase_bills purchase_bills_vendor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_bills
    ADD CONSTRAINT purchase_bills_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(id);


--
-- Name: purchase_requests purchase_requests_created_expense_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_requests
    ADD CONSTRAINT purchase_requests_created_expense_id_fkey FOREIGN KEY (created_expense_id) REFERENCES public.expenses(id);


--
-- Name: purchase_requests purchase_requests_created_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_requests
    ADD CONSTRAINT purchase_requests_created_item_id_fkey FOREIGN KEY (created_item_id) REFERENCES public.items(id);


--
-- Name: purchase_requests purchase_requests_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_requests
    ADD CONSTRAINT purchase_requests_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: purchase_requests purchase_requests_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.purchase_requests
    ADD CONSTRAINT purchase_requests_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: salary_slips salary_slips_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_slips
    ADD CONSTRAINT salary_slips_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: salary_slips salary_slips_payroll_payment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_slips
    ADD CONSTRAINT salary_slips_payroll_payment_id_fkey FOREIGN KEY (payroll_payment_id) REFERENCES public.payroll_payments(id) ON DELETE CASCADE;


--
-- Name: salary_slips salary_slips_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.salary_slips
    ADD CONSTRAINT salary_slips_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- Name: sales_order_items sales_order_items_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_order_items
    ADD CONSTRAINT sales_order_items_item_id_fkey FOREIGN KEY (item_id) REFERENCES public.items(id);


--
-- Name: sales_order_items sales_order_items_sales_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_order_items
    ADD CONSTRAINT sales_order_items_sales_order_id_fkey FOREIGN KEY (sales_order_id) REFERENCES public.sales_orders(id) ON DELETE CASCADE;


--
-- Name: sales_order_items sales_order_items_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_order_items
    ADD CONSTRAINT sales_order_items_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: sales_order_items sales_order_items_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_order_items
    ADD CONSTRAINT sales_order_items_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: sales_orders sales_orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: sales_orders sales_orders_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sales_orders
    ADD CONSTRAINT sales_orders_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: sites sites_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sites
    ADD CONSTRAINT sites_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: stock_movements stock_movements_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id);


--
-- Name: stock_movements stock_movements_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: stock_movements stock_movements_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: stock_movements stock_movements_transfer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_transfer_id_fkey FOREIGN KEY (transfer_id) REFERENCES public.transfers(id);


--
-- Name: stock_movements stock_movements_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: stocks stocks_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id);


--
-- Name: stocks stocks_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: stocks stocks_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: subscription_deliveries subscription_deliveries_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries
    ADD CONSTRAINT subscription_deliveries_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.employees(id);


--
-- Name: subscription_deliveries subscription_deliveries_delivered_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries
    ADD CONSTRAINT subscription_deliveries_delivered_by_fkey FOREIGN KEY (delivered_by) REFERENCES public.employees(id);


--
-- Name: subscription_deliveries subscription_deliveries_subscription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries
    ADD CONSTRAINT subscription_deliveries_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.customer_subscriptions(id);


--
-- Name: subscription_deliveries subscription_deliveries_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_deliveries
    ADD CONSTRAINT subscription_deliveries_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: subscription_payments subscription_payments_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_payments
    ADD CONSTRAINT subscription_payments_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: subscription_payments subscription_payments_subscription_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_payments
    ADD CONSTRAINT subscription_payments_subscription_id_fkey FOREIGN KEY (subscription_id) REFERENCES public.customer_subscriptions(id);


--
-- Name: subscription_payments subscription_payments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_payments
    ADD CONSTRAINT subscription_payments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: subscription_plans subscription_plans_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.subscription_plans
    ADD CONSTRAINT subscription_plans_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: task_materials task_materials_added_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_materials
    ADD CONSTRAINT task_materials_added_by_fkey FOREIGN KEY (added_by) REFERENCES public.employees(id);


--
-- Name: task_materials task_materials_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_materials
    ADD CONSTRAINT task_materials_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_media task_media_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_media
    ADD CONSTRAINT task_media_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_media task_media_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_media
    ADD CONSTRAINT task_media_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.employees(id);


--
-- Name: task_updates task_updates_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT task_updates_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id);


--
-- Name: task_updates task_updates_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_updates
    ADD CONSTRAINT task_updates_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.employees(id);


--
-- Name: tasks tasks_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.employees(id);


--
-- Name: tasks tasks_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.employees(id);


--
-- Name: tasks tasks_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_site_id_fkey FOREIGN KEY (site_id) REFERENCES public.sites(id);


--
-- Name: tasks tasks_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: transfers transfers_from_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_from_site_id_fkey FOREIGN KEY (from_site_id) REFERENCES public.sites(id);


--
-- Name: transfers transfers_initiated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_initiated_by_fkey FOREIGN KEY (initiated_by) REFERENCES public.users(id);


--
-- Name: transfers transfers_material_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_material_id_fkey FOREIGN KEY (material_id) REFERENCES public.materials(id);


--
-- Name: transfers transfers_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: transfers transfers_to_site_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transfers
    ADD CONSTRAINT transfers_to_site_id_fkey FOREIGN KEY (to_site_id) REFERENCES public.sites(id);


--
-- Name: vendor_payments vendor_payments_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendor_payments
    ADD CONSTRAINT vendor_payments_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: vendor_payments vendor_payments_vendor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendor_payments
    ADD CONSTRAINT vendor_payments_vendor_id_fkey FOREIGN KEY (vendor_id) REFERENCES public.vendors(id);


--
-- Name: vendors vendors_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT vendors_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: objects objects_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.objects
    ADD CONSTRAINT "objects_bucketId_fkey" FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: prefixes prefixes_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.prefixes
    ADD CONSTRAINT "prefixes_bucketId_fkey" FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads s3_multipart_uploads_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads
    ADD CONSTRAINT s3_multipart_uploads_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets(id);


--
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_upload_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.s3_multipart_uploads_parts
    ADD CONSTRAINT s3_multipart_uploads_parts_upload_id_fkey FOREIGN KEY (upload_id) REFERENCES storage.s3_multipart_uploads(id) ON DELETE CASCADE;


--
-- Name: vector_indexes vector_indexes_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY storage.vector_indexes
    ADD CONSTRAINT vector_indexes_bucket_id_fkey FOREIGN KEY (bucket_id) REFERENCES storage.buckets_vectors(id);


--
-- Name: audit_log_entries; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.audit_log_entries ENABLE ROW LEVEL SECURITY;

--
-- Name: flow_state; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.flow_state ENABLE ROW LEVEL SECURITY;

--
-- Name: identities; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.identities ENABLE ROW LEVEL SECURITY;

--
-- Name: instances; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.instances ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_amr_claims; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.mfa_amr_claims ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_challenges; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.mfa_challenges ENABLE ROW LEVEL SECURITY;

--
-- Name: mfa_factors; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.mfa_factors ENABLE ROW LEVEL SECURITY;

--
-- Name: one_time_tokens; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.one_time_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: refresh_tokens; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.refresh_tokens ENABLE ROW LEVEL SECURITY;

--
-- Name: saml_providers; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.saml_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: saml_relay_states; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.saml_relay_states ENABLE ROW LEVEL SECURITY;

--
-- Name: schema_migrations; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.schema_migrations ENABLE ROW LEVEL SECURITY;

--
-- Name: sessions; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.sessions ENABLE ROW LEVEL SECURITY;

--
-- Name: sso_domains; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.sso_domains ENABLE ROW LEVEL SECURITY;

--
-- Name: sso_providers; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.sso_providers ENABLE ROW LEVEL SECURITY;

--
-- Name: users; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE auth.users ENABLE ROW LEVEL SECURITY;

--
-- Name: messages; Type: ROW SECURITY; Schema: realtime; Owner: -
--

ALTER TABLE realtime.messages ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.buckets ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets_analytics; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.buckets_analytics ENABLE ROW LEVEL SECURITY;

--
-- Name: buckets_vectors; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.buckets_vectors ENABLE ROW LEVEL SECURITY;

--
-- Name: migrations; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.migrations ENABLE ROW LEVEL SECURITY;

--
-- Name: objects; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

--
-- Name: prefixes; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.prefixes ENABLE ROW LEVEL SECURITY;

--
-- Name: s3_multipart_uploads; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.s3_multipart_uploads ENABLE ROW LEVEL SECURITY;

--
-- Name: s3_multipart_uploads_parts; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.s3_multipart_uploads_parts ENABLE ROW LEVEL SECURITY;

--
-- Name: vector_indexes; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE storage.vector_indexes ENABLE ROW LEVEL SECURITY;

--
-- Name: supabase_realtime; Type: PUBLICATION; Schema: -; Owner: -
--

CREATE PUBLICATION supabase_realtime WITH (publish = 'insert, update, delete, truncate');


--
-- Name: issue_graphql_placeholder; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_graphql_placeholder ON sql_drop
         WHEN TAG IN ('DROP EXTENSION')
   EXECUTE FUNCTION extensions.set_graphql_placeholder();


--
-- Name: issue_pg_cron_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_pg_cron_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_cron_access();


--
-- Name: issue_pg_graphql_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_pg_graphql_access ON ddl_command_end
         WHEN TAG IN ('CREATE FUNCTION')
   EXECUTE FUNCTION extensions.grant_pg_graphql_access();


--
-- Name: issue_pg_net_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER issue_pg_net_access ON ddl_command_end
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION extensions.grant_pg_net_access();


--
-- Name: pgrst_ddl_watch; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER pgrst_ddl_watch ON ddl_command_end
   EXECUTE FUNCTION extensions.pgrst_ddl_watch();


--
-- Name: pgrst_drop_watch; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER pgrst_drop_watch ON sql_drop
   EXECUTE FUNCTION extensions.pgrst_drop_watch();


--
-- PostgreSQL database dump complete
--

\unrestrict xlAk8vsp5LEapeABurHDvXijW7LTKzi82a81dtHg6eB13N0ypfckS9psmJeBZcy

