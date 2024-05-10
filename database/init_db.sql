-- This script requires the pgvector extension to be installed in PostgreSQL.
-- Please ensure pgvector is installed before running this script.

create schema zib;

-- user_topics: table
create table zib.user_topics(
    user_id int default 0 not null,
    chat_id bigint default 0 not null,
    topic_id int default 0 not null,
    topic_name text default ''::text not null,
    constraint user_topics_pkey primary key(user_id, chat_id, topic_id)
);

-- user_topics: indexes
create index user_topics_idx on zib.user_topics (user_id, chat_id);
create unique index user_topics_comp_idx on zib.user_topics (user_id, chat_id, topic_name);

-- user_messages: table
create table zib.user_messages(
    msg_id integer default 0 not null,
    user_id int default 0 not null,
    chat_id bigint default 0 not null,
    topic_id integer default 0 not null,
    msg_text text default ''::text not null,
    msg_emb vector not null,
    constraint user_messages_pkey primary key(msg_id)
);

-- user_messages: foreign keys
alter table zib.user_messages add constraint user_messages_fk
foreign key(user_id, chat_id, topic_id) references zib.user_topics(user_id, chat_id, topic_id);

-- user_messages: indexes
create index user_messages_comp_idx1 on zib.user_messages (user_id, chat_id);
create index user_messages_comp_idx2 on zib.user_messages (user_id, chat_id, topic_id);
create unique index user_messages_comp_idx3 on zib.user_messages (user_id, chat_id, msg_id);