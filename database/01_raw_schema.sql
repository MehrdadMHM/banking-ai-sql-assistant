--
-- PostgreSQL database dump
--

\restrict is7n4lQYUYDCJvx2LG2kdSQXhV6cJwtX7GxQWAs4Jl9Rij9haiC3unCHXu3Udbn

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
-- Name: raw; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA raw;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts; Type: TABLE; Schema: raw; Owner: -
--

CREATE TABLE raw.accounts (
    account_id bigint NOT NULL,
    customer_id bigint NOT NULL,
    branch_id bigint NOT NULL,
    account_number character varying(30) NOT NULL,
    account_type character varying(20) NOT NULL,
    currency character varying(3) NOT NULL,
    status character varying(20) NOT NULL,
    opened_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: branches; Type: TABLE; Schema: raw; Owner: -
--

CREATE TABLE raw.branches (
    branch_id bigint NOT NULL,
    branch_name character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: customers; Type: TABLE; Schema: raw; Owner: -
--

CREATE TABLE raw.customers (
    customer_id bigint NOT NULL,
    customer_name character varying(150) NOT NULL,
    customer_type character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: transactions; Type: TABLE; Schema: raw; Owner: -
--

CREATE TABLE raw.transactions (
    transaction_id bigint NOT NULL,
    account_id bigint NOT NULL,
    transaction_type character varying(20) NOT NULL,
    amount numeric(18,2) NOT NULL,
    status character varying(20) NOT NULL,
    transaction_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: accounts accounts_pkey; Type: CONSTRAINT; Schema: raw; Owner: -
--

ALTER TABLE ONLY raw.accounts
    ADD CONSTRAINT accounts_pkey PRIMARY KEY (account_id);


--
-- Name: branches branches_pkey; Type: CONSTRAINT; Schema: raw; Owner: -
--

ALTER TABLE ONLY raw.branches
    ADD CONSTRAINT branches_pkey PRIMARY KEY (branch_id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: raw; Owner: -
--

ALTER TABLE ONLY raw.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: raw; Owner: -
--

ALTER TABLE ONLY raw.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (transaction_id);


--
-- PostgreSQL database dump complete
--

\unrestrict is7n4lQYUYDCJvx2LG2kdSQXhV6cJwtX7GxQWAs4Jl9Rij9haiC3unCHXu3Udbn

