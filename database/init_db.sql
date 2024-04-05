create schema zib;

create table zib.messages(
    id serial,
    user_id text default ''::text not null,
    msg_id integer default 0 not null,
    msg_text text default ''::text not null,
    category text default ''::text not null,
    constraint messages_pkey primary key(id)
);

create index messages_idx on zib.messages
using btree (user_id);

create index messages_idx1 on zib.messages
using btree (user_id, category);

create index messages_idx2 on zib.messages
using btree (user_id, msg_id);
