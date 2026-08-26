--
-- PostgreSQL database dump
--

\restrict n63fmcChGd6xjwJguEkhpdQFaeFwBXfbS3TbWdigdtSmF1Ou4gqNsjTs1vgLjBs

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

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

ALTER TABLE ONLY public.threads DROP CONSTRAINT threads_board_id_fkey;
ALTER TABLE ONLY public.threads DROP CONSTRAINT threads_author_id_fkey;
ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_thread_id_fkey;
ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_author_id_fkey;
DROP INDEX public.ix_users_username;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
ALTER TABLE ONLY public.users DROP CONSTRAINT users_email_key;
ALTER TABLE ONLY public.threads DROP CONSTRAINT threads_pkey;
ALTER TABLE ONLY public.posts DROP CONSTRAINT posts_pkey;
ALTER TABLE ONLY public.boards DROP CONSTRAINT boards_pkey;
ALTER TABLE ONLY public.boards DROP CONSTRAINT boards_name_key;
ALTER TABLE public.boards ALTER COLUMN id DROP DEFAULT;
DROP TABLE public.users;
DROP TABLE public.threads;
DROP TABLE public.posts;
DROP SEQUENCE public.boards_id_seq;
DROP TABLE public.boards;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: boards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.boards (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    display_order integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.boards OWNER TO postgres;

--
-- Name: boards_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.boards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.boards_id_seq OWNER TO postgres;

--
-- Name: boards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.boards_id_seq OWNED BY public.boards.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.posts (
    id uuid NOT NULL,
    thread_id uuid NOT NULL,
    author_id uuid NOT NULL,
    body text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- Name: threads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.threads (
    id uuid NOT NULL,
    board_id integer NOT NULL,
    author_id uuid NOT NULL,
    title character varying(200) NOT NULL,
    is_locked boolean NOT NULL,
    is_pinned boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.threads OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    is_admin boolean NOT NULL,
    is_banned boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: boards id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.boards ALTER COLUMN id SET DEFAULT nextval('public.boards_id_seq'::regclass);


--
-- Data for Name: boards; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.boards (id, name, description, display_order, created_at) FROM stdin;
1	Site Hakkında	Kurallar, İletişim, Duyurular	1	2026-05-28 14:11:34.549816+00
2	Sakin	Grup hakkında yorumlar.	2	2026-05-28 14:11:34.549816+00
3	HAYAT - 2008	Albüm hakkında yorumlar	3	2026-05-28 14:11:34.549816+00
4	Müzik	Yerli Müzisyenler, Yabancı Müzisyenler, Amatör Müzik	4	2026-05-28 14:11:34.549816+00
5	Kültür - Sanat	Edebiyat, Felsefe, Sinema & Tiyatro	5	2026-05-28 14:11:34.549816+00
6	Genel	Kategori dışı konular...	6	2026-05-28 14:11:34.549816+00
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.posts (id, thread_id, author_id, body, created_at, updated_at) FROM stdin;
2f760190-d6ad-45b1-bc15-ac5fbdff7a54	738a2b67-f605-413f-bc7d-6ca89327c7ca	efea91e5-89cd-4d2d-992d-6194bcdd7c02	123	2026-05-29 18:28:42.65228+00	\N
549950ce-e75b-49be-aa34-4e0dcfb7c6ac	738a2b67-f605-413f-bc7d-6ca89327c7ca	efea91e5-89cd-4d2d-992d-6194bcdd7c02	bence 345!	2026-05-29 18:28:49.193978+00	\N
aa908658-519e-4a11-bd26-9e544604cb36	831e8970-a3ea-44f6-96ef-e68298921f64	5df64baf-4295-4866-95b6-27ae49acff49	# cok iyi sarki la\r\n*bence* en iyi sarkilari\r\n\r\ngayim	2026-05-29 18:48:30.297119+00	\N
4cb80b6d-fe8c-40a9-9687-bb3ccea7a80a	831e8970-a3ea-44f6-96ef-e68298921f64	5df64baf-4295-4866-95b6-27ae49acff49	kjdhsglksg	2026-05-29 18:48:39.90521+00	\N
\.


--
-- Data for Name: threads; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.threads (id, board_id, author_id, title, is_locked, is_pinned, created_at) FROM stdin;
831e8970-a3ea-44f6-96ef-e68298921f64	2	5df64baf-4295-4866-95b6-27ae49acff49	icarus basarsa 	f	f	2026-05-29 18:48:30.297119+00
738a2b67-f605-413f-bc7d-6ca89327c7ca	2	efea91e5-89cd-4d2d-992d-6194bcdd7c02	test	t	f	2026-05-29 18:28:42.65228+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password_hash, is_admin, is_banned, created_at) FROM stdin;
efea91e5-89cd-4d2d-992d-6194bcdd7c02	admin	admin@sakinfan.com	$2b$12$h7VgyNB5is8974R/P/jsEezdQZSBILG94kNFeIbhT7BewKwjyZk5W	t	f	2026-05-28 14:11:34.549816+00
5df64baf-4295-4866-95b6-27ae49acff49	sevval	sevval@efendim.org.tr	$2b$12$FOJeB2jEjAmWNhFF4trky.84T1Ik61Oeab4Y7aV/xaU6GUjWoZyn.	f	f	2026-05-29 18:47:29.327393+00
\.


--
-- Name: boards_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.boards_id_seq', 33, true);


--
-- Name: boards boards_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.boards
    ADD CONSTRAINT boards_name_key UNIQUE (name);


--
-- Name: boards boards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.boards
    ADD CONSTRAINT boards_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: threads threads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: posts posts_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: posts posts_thread_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_thread_id_fkey FOREIGN KEY (thread_id) REFERENCES public.threads(id);


--
-- Name: threads threads_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- Name: threads threads_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.threads
    ADD CONSTRAINT threads_board_id_fkey FOREIGN KEY (board_id) REFERENCES public.boards(id);


--
-- PostgreSQL database dump complete
--

\unrestrict n63fmcChGd6xjwJguEkhpdQFaeFwBXfbS3TbWdigdtSmF1Ou4gqNsjTs1vgLjBs

