-- Snipex Supabase Schema
-- Run this in the Supabase SQL editor to set up the database.

-- Enable UUID extension
create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- api_keys
-- ---------------------------------------------------------------------------
create table if not exists api_keys (
  id          uuid primary key default gen_random_uuid(),
  user_id     text not null,           -- Clerk user ID (e.g. user_abc123)
  name        text not null default 'Default',
  key         text not null unique,    -- snx_... format
  created_at  timestamptz not null default now(),
  last_used_at timestamptz
);

-- Index for fast lookup by user
create index if not exists api_keys_user_id_idx on api_keys (user_id);

-- RLS
alter table api_keys enable row level security;

-- Users can only read/delete their own keys via service role
-- (We always use service role from API routes, so no anon RLS policy needed)

-- ---------------------------------------------------------------------------
-- usage
-- ---------------------------------------------------------------------------
create table if not exists usage (
  id             uuid primary key default gen_random_uuid(),
  user_id        text not null,
  date           date not null,
  request_count  integer not null default 0,
  unique (user_id, date)
);

create index if not exists usage_user_id_date_idx on usage (user_id, date desc);

alter table usage enable row level security;

-- ---------------------------------------------------------------------------
-- credits
-- ---------------------------------------------------------------------------
create table if not exists credits (
  user_id           text primary key,
  credits_remaining integer not null default 100,  -- default free tier credits
  updated_at        timestamptz not null default now()
);

alter table credits enable row level security;

-- ---------------------------------------------------------------------------
-- Function: increment usage (upsert by user+date)
-- ---------------------------------------------------------------------------
create or replace function increment_usage(p_user_id text, p_date date)
returns void
language plpgsql
as $$
begin
  insert into usage (user_id, date, request_count)
  values (p_user_id, p_date, 1)
  on conflict (user_id, date)
  do update set request_count = usage.request_count + 1;
end;
$$;
