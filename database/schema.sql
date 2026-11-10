--
-- PostgreSQL database dump
--

\restrict YC2gS56BjYZ6OZDeAEiILemkypIjDlqGg63c9YBBNEOZz8KxTNfVNE5CfIvrhBy

-- Dumped from database version 15.19 (Debian 15.19-1.pgdg12+2)
-- Dumped by pg_dump version 15.19 (Debian 15.19-1.pgdg12+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: analytics; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA analytics;


--
-- Name: rag; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA rag;


--
-- Name: dim_accounts; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.dim_accounts AS
 SELECT accounts.account_id,
    accounts.customer_id,
    accounts.branch_id,
    accounts.account_number,
    accounts.account_type,
    accounts.currency,
    accounts.status AS account_status,
    accounts.opened_at,
    accounts.updated_at
   FROM raw.accounts;


--
-- Name: dim_branches; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.dim_branches AS
 SELECT branches.branch_id,
    branches.branch_name,
    branches.city,
    branches.updated_at
   FROM raw.branches;


--
-- Name: dim_customers; Type: VIEW; Schema: analytics; Owner: -
--

CREATE VIEW analytics.dim_customers AS
 SELECT customers.customer_id,
    customers.customer_name,
    customers.customer_type,
    customers.created_at,
    customers.updated_at
   FROM raw.customers;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: fact_transactions; Type: TABLE; Schema: analytics; Owner: -
--

CREATE TABLE analytics.fact_transactions (
    transaction_id bigint,
    account_id bigint,
    customer_id bigint,
    branch_id bigint,
    currency character varying(3),
    transaction_type character varying(20),
    transaction_status character varying(20),
    transaction_at timestamp with time zone,
    transaction_date date,
    amount numeric(18,2),
    signed_amount numeric,
    completed_inflow numeric,
    completed_outflow numeric,
    updated_at timestamp with time zone
);


--
-- Name: documents; Type: TABLE; Schema: rag; Owner: -
--

CREATE TABLE rag.documents (
    id bigint NOT NULL,
    document_key text NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    embedding public.vector(768) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: documents_id_seq; Type: SEQUENCE; Schema: rag; Owner: -
--

CREATE SEQUENCE rag.documents_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: documents_id_seq; Type: SEQUENCE OWNED BY; Schema: rag; Owner: -
--

ALTER SEQUENCE rag.documents_id_seq OWNED BY rag.documents.id;


--
-- Name: documents id; Type: DEFAULT; Schema: rag; Owner: -
--

ALTER TABLE ONLY rag.documents ALTER COLUMN id SET DEFAULT nextval('rag.documents_id_seq'::regclass);


--
-- Name: documents documents_document_key_key; Type: CONSTRAINT; Schema: rag; Owner: -
--

ALTER TABLE ONLY rag.documents
    ADD CONSTRAINT documents_document_key_key UNIQUE (document_key);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: rag; Owner: -
--

ALTER TABLE ONLY rag.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict YC2gS56BjYZ6OZDeAEiILemkypIjDlqGg63c9YBBNEOZz8KxTNfVNE5CfIvrhBy

