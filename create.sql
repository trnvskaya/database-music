-- odeberu pokud existuje funkce na oodebrání tabulek a sekvencí
DROP FUNCTION IF EXISTS remove_all();

CREATE or replace FUNCTION remove_all() RETURNS void AS $$
DECLARE
    rec RECORD;
    cmd text;
BEGIN
    cmd := '';

    FOR rec IN SELECT
            'DROP SEQUENCE ' || quote_ident(n.nspname) || '.'
                || quote_ident(c.relname) || ' CASCADE;' AS name
        FROM
            pg_catalog.pg_class AS c
        LEFT JOIN
            pg_catalog.pg_namespace AS n
        ON
            n.oid = c.relnamespace
        WHERE
            relkind = 'S' AND
            n.nspname NOT IN ('pg_catalog', 'pg_toast') AND
            pg_catalog.pg_table_is_visible(c.oid)
    LOOP
        cmd := cmd || rec.name;
    END LOOP;

    FOR rec IN SELECT
            'DROP TABLE ' || quote_ident(n.nspname) || '.'
                || quote_ident(c.relname) || ' CASCADE;' AS name
        FROM
            pg_catalog.pg_class AS c
        LEFT JOIN
            pg_catalog.pg_namespace AS n
        ON
            n.oid = c.relnamespace WHERE relkind = 'r' AND
            n.nspname NOT IN ('pg_catalog', 'pg_toast') AND
            pg_catalog.pg_table_is_visible(c.oid)
    LOOP
        cmd := cmd || rec.name;
    END LOOP;

    EXECUTE cmd;
    RETURN;
END;
$$ LANGUAGE plpgsql;
select remove_all();

CREATE TABLE artist_user (
    username SERIAL NOT NULL,
    manager_user_username SERIAL NOT NULL,
    discography VARCHAR(80) NOT NULL,
    biography VARCHAR(80) NOT NULL,
    genre VARCHAR(20) NOT NULL,
    photos VARCHAR(256)
);
ALTER TABLE artist_user ADD CONSTRAINT pk_artist_user PRIMARY KEY (username);

CREATE TABLE basic_user (
    username SERIAL NOT NULL,
    basic_user_username INTEGER,
    birth_date DATE NOT NULL,
    preferences VARCHAR(256) NOT NULL,
    profile_description VARCHAR(256) NOT NULL,
    credit_card VARCHAR(20) NOT NULL,
    subscription_type VARCHAR(256),
    subscription_price FLOAT,
    subscription_date DATE,
    bank_information VARCHAR(256)
);
ALTER TABLE basic_user ADD CONSTRAINT pk_basic_user PRIMARY KEY (username);

CREATE TABLE content_moderator_user (
    username SERIAL NOT NULL,
    tasks VARCHAR(40) NOT NULL,
    moderation_history VARCHAR(80)
);
ALTER TABLE content_moderator_user ADD CONSTRAINT pk_content_moderator_user PRIMARY KEY (username);

CREATE TABLE event (
    event_id SERIAL NOT NULL,
    location_id SERIAL,
    description VARCHAR(256) NOT NULL,
    date DATE NOT NULL,
    conditions VARCHAR(256) NOT NULL
);
ALTER TABLE event ADD CONSTRAINT pk_event PRIMARY KEY (event_id);

CREATE TABLE location (
    location_id SERIAL NOT NULL,
    country VARCHAR(256) NOT NULL,
    region VARCHAR(256) NOT NULL,
    city VARCHAR(256) NOT NULL,
    address VARCHAR(256)
);
ALTER TABLE location ADD CONSTRAINT pk_location PRIMARY KEY (location_id);

CREATE TABLE manager_user (
    username SERIAL NOT NULL,
    role_for_artist VARCHAR(30) NOT NULL,
    tasks VARCHAR(80) NOT NULL
);
ALTER TABLE manager_user ADD CONSTRAINT pk_manager_user PRIMARY KEY (username);

CREATE TABLE merchandise_product (
    product_id SERIAL NOT NULL,
    username SERIAL NOT NULL,
    product_name VARCHAR(50) NOT NULL,
    shipping VARCHAR(256) NOT NULL,
    description VARCHAR(256),
    product_price FLOAT NOT NULL,
    availibility BOOLEAN NOT NULL
);
ALTER TABLE merchandise_product ADD CONSTRAINT pk_merchandise_product PRIMARY KEY (product_id);

CREATE TABLE playlist (
    playlist_id SERIAL NOT NULL,
    username INTEGER NOT NULL,
    description VARCHAR(80),
    link VARCHAR(50) NOT NULL
);
ALTER TABLE playlist ADD CONSTRAINT pk_playlist PRIMARY KEY (playlist_id);

CREATE TABLE public_channel (
    channel_id SERIAL NOT NULL,
    channel_name VARCHAR(40),
    username SERIAL NOT NULL,
    location_id SERIAL,
    description VARCHAR(100) NOT NULL,
    preferred_genre VARCHAR(20),
    link VARCHAR(256) NOT NULL
);
ALTER TABLE public_channel ADD CONSTRAINT pk_public_channel PRIMARY KEY (channel_id);

CREATE TABLE song (
    song_id SERIAL NOT NULL,
    name VARCHAR(40) NOT NULL,
    lyrics VARCHAR(256)
);
ALTER TABLE song ADD CONSTRAINT pk_song PRIMARY KEY (song_id);

CREATE TABLE users (
    username SERIAL NOT NULL,
    full_name VARCHAR(40) NOT NULL,
    mobile_phone VARCHAR(15),
    email VARCHAR(50) NOT NULL,
    links_media VARCHAR(100)
);
ALTER TABLE users ADD CONSTRAINT pk_user PRIMARY KEY (username);

CREATE TABLE event_artist_user (
    event_id SERIAL NOT NULL,
    username SERIAL NOT NULL
);
ALTER TABLE event_artist_user ADD CONSTRAINT pk_event_artist_user PRIMARY KEY (event_id, username);

CREATE TABLE song_playlist (
    song_id SERIAL NOT NULL,
    playlist_id SERIAL NOT NULL
);
ALTER TABLE song_playlist ADD CONSTRAINT pk_song_playlist PRIMARY KEY (song_id, playlist_id);

CREATE TABLE song_artist_user (
    song_id SERIAL NOT NULL,
    username SERIAL NOT NULL
);
ALTER TABLE song_artist_user ADD CONSTRAINT pk_song_artist_user PRIMARY KEY (song_id, username);

ALTER TABLE artist_user ADD CONSTRAINT fk_artist_user_user FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE;
ALTER TABLE artist_user ADD CONSTRAINT fk_artist_user_manager_user FOREIGN KEY (manager_user_username) REFERENCES manager_user (username) ON DELETE CASCADE;

ALTER TABLE basic_user ADD CONSTRAINT fk_basic_user_user FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE;
ALTER TABLE basic_user ADD CONSTRAINT fk_basic_user_basic_user FOREIGN KEY (basic_user_username) REFERENCES basic_user (username) ON DELETE CASCADE;

ALTER TABLE content_moderator_user ADD CONSTRAINT fk_content_moderator_user_user FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE;

ALTER TABLE event ADD CONSTRAINT fk_event_location FOREIGN KEY (location_id) REFERENCES location (location_id) ON DELETE CASCADE;

ALTER TABLE manager_user ADD CONSTRAINT fk_manager_user_user FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE;

ALTER TABLE merchandise_product ADD CONSTRAINT fk_merchandise_product_artist_u FOREIGN KEY (username) REFERENCES artist_user (username) ON DELETE CASCADE;

ALTER TABLE playlist ADD CONSTRAINT fk_playlist_basic_user FOREIGN KEY (username) REFERENCES basic_user (username) ON DELETE CASCADE;

ALTER TABLE public_channel ADD CONSTRAINT fk_public_channel_content_moder FOREIGN KEY (username) REFERENCES content_moderator_user (username) ON DELETE CASCADE;
ALTER TABLE public_channel ADD CONSTRAINT fk_public_channel_location FOREIGN KEY (location_id) REFERENCES location (location_id) ON DELETE CASCADE;

ALTER TABLE event_artist_user ADD CONSTRAINT fk_event_artist_user_event FOREIGN KEY (event_id) REFERENCES event (event_id) ON DELETE CASCADE;
ALTER TABLE event_artist_user ADD CONSTRAINT fk_event_artist_user_artist_use FOREIGN KEY (username) REFERENCES artist_user (username) ON DELETE CASCADE;

ALTER TABLE song_playlist ADD CONSTRAINT fk_song_playlist_song FOREIGN KEY (song_id) REFERENCES song (song_id) ON DELETE CASCADE;
ALTER TABLE song_playlist ADD CONSTRAINT fk_song_playlist_playlist FOREIGN KEY (playlist_id) REFERENCES playlist (playlist_id) ON DELETE CASCADE;

ALTER TABLE song_artist_user ADD CONSTRAINT fk_song_artist_user_song FOREIGN KEY (song_id) REFERENCES song (song_id) ON DELETE CASCADE;
ALTER TABLE song_artist_user ADD CONSTRAINT fk_song_artist_user_artist_user FOREIGN KEY (username) REFERENCES artist_user (username) ON DELETE CASCADE;

