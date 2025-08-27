-- smazání všech záznamů z tabulek

CREATE OR REPLACE FUNCTION clean_tables() RETURNS void AS
$$
DECLARE
    l_stmt text;
BEGIN
    SELECT 'truncate ' || STRING_AGG(FORMAT('%I.%I', schemaname, tablename), ',')
    INTO l_stmt
    FROM pg_tables
    WHERE schemaname IN ('public');

    EXECUTE l_stmt || ' cascade';
END;
$$ LANGUAGE plpgsql;
SELECT clean_tables();

-- reset sekvenci

CREATE OR REPLACE FUNCTION restart_sequences() RETURNS void AS
$$
DECLARE
    i TEXT;
BEGIN
    FOR i IN (SELECT column_default FROM information_schema.columns WHERE column_default SIMILAR TO 'nextval%')
        LOOP
            EXECUTE 'ALTER SEQUENCE' || ' ' || SUBSTRING(SUBSTRING(i FROM '''[a-z_]*') FROM '[a-z_]+') || ' ' ||
                    ' RESTART 1;';
        END LOOP;
END
$$ LANGUAGE plpgsql;
SELECT restart_sequences();



insert into location (location_id, country, region, city, address) values (1, 'UK', 'UK', 'London', '7 Glacier Hill Court');
insert into location (location_id, country, region, city, address) values (2, 'China', 'CN', 'Hedi', '95 Vermont Lane');
insert into location (location_id, country, region, city, address) values (3, 'China', 'CN', 'Sanbaishan', '0 Anniversary Road');
insert into location (location_id, country, region, city, address) values (4, 'Greece', 'GR', 'Kampánis', '5388 Bashford Junction');
insert into location (location_id, country, region, city, address) values (5, 'UK', 'UK', 'London', '04 Bluejay Junction');
insert into location (location_id, country, region, city, address) values (6, 'China', 'CN', 'Gemo', '18 Twin Pines Terrace');
insert into location (location_id, country, region, city, address) values (7, 'Greece', 'GR', 'Asopós', '0103 Kingsford Terrace');
insert into location (location_id, country, region, city, address) values (8, 'Portugal', 'PT', 'Avanca', '34 Petterle Plaza');
insert into location (location_id, country, region, city, address) values (9, 'Belarus', 'BY', 'Hatava', '8 Shopko Park');
insert into location (location_id, country, region, city, address) values (10, 'Czech Republic', 'CZ', 'Prague', 'Thakurova 9');
insert into location (location_id, country, region, city, address) values (11, 'Zambia', 'ZM', 'Kalengwa', '55 Lawn Place');
insert into location (location_id, country, region, city, address) values (12, 'China', 'CN', 'Maxiao', '14417 Browning Terrace');
insert into location (location_id, country, region, city, address) values (13, 'China', 'CN', 'Hongdun', '0466 Main Hill');
insert into location (location_id, country, region, city, address) values (14, 'France', 'FR', 'Saint-Lô', '28 Declaration Alley');
insert into location (location_id, country, region, city, address) values (15, 'United States', 'US', 'Boston', '9417 Hagan Park');
insert into location (location_id, country, region, city, address) values (16, 'Colombia', 'CO', 'Quinchía', '2272 Southridge Point');
insert into location (location_id, country, region, city, address) values (17, 'Greece', 'GR', 'Keratéa', '356 Caliangt Place');
insert into location (location_id, country, region, city, address) values (18, 'Argentina', 'AR', 'Embajador Martini', '23002 Green Ridge Lane');
insert into location (location_id, country, region, city, address) values (19, 'Israel', 'IL', 'Bu‘eina', '180 Scoville Plaza');
insert into location (location_id, country, region, city, address) values (20, 'Pakistan', 'PK', 'Pindi Gheb', '05334 Ridgeway Trail');
-- nastavuji sekvenci kterou identifikuji pomocí pg_get_serial_sequence na hodnotu 2 abych mohl pokračovat přidáváním dalších řádků
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('location', 'location_id'), 20);


insert into event (event_id, location_id, description, date, conditions) values (1, 1, 'sed augue aliquam erat volutpat', '8/29/2022', 'Profit-focused fault-tolerant neural-net');
insert into event (event_id, location_id, description, date, conditions) values (2, 2, 'cursus', '6/15/2022', 'Customer-focused interactive adapter');
insert into event (event_id, location_id, description, date, conditions) values (3, 3, 'sem sed', '4/5/2024', 'Streamlined incremental analyzer');
insert into event (event_id, location_id, description, date, conditions) values (4, 4, 'ac est lacinia nisi', '2/22/2023', 'Customer-focused directional implementation');
insert into event (event_id, location_id, description, date, conditions) values (5, 5, 'sollicitudin ut suscipit a feugiat', '3/24/2024', 'Proactive bi-directional collaboration');
insert into event (event_id, location_id, description, date, conditions) values (6, 6, 'nam nulla integer pede', '9/13/2022', 'Ameliorated optimizing hub');
insert into event (event_id, location_id, description, date, conditions) values (7, 7, 'tortor', '8/23/2023', 'Team-oriented 24 hour middleware');
insert into event (event_id, location_id, description, date, conditions) values (8, 8, 'in quam fringilla', '10/9/2021', 'Upgradable multi-tasking solution');
insert into event (event_id, location_id, description, date, conditions) values (9, 9, 'at feugiat', '5/3/2023', 'Visionary motivating array');
insert into event (event_id, location_id, description, date, conditions) values (10, 10, 'massa quis augue', '7/30/2022', 'Adaptive logistical info-mediaries');
insert into event (event_id, location_id, description, date, conditions) values (11, 11, 'vel ipsum praesent', '11/2/2022', 'Compatible impactful initiative');
insert into event (event_id, location_id, description, date, conditions) values (12, 12, 'gravida', '10/15/2023', 'Synchronised non-volatile moderator');
insert into event (event_id, location_id, description, date, conditions) values (13, 13, 'ac tellus semper interdum mauris', '11/26/2022', 'Up-sized zero tolerance secured line');
insert into event (event_id, location_id, description, date, conditions) values (14, 14, 'orci luctus', '12/9/2023', 'Seamless bottom-line conglomeration');
insert into event (event_id, location_id, description, date, conditions) values (15, 15, 'ut', '4/6/2023', 'Team-oriented non-volatile capability');
insert into event (event_id, location_id, description, date, conditions) values (16, 16, 'ligula', '8/20/2023', 'Advanced optimal local area network');
insert into event (event_id, location_id, description, date, conditions) values (17, 17, 'dapibus at diam', '7/13/2023', 'Organized tangible utilisation');
insert into event (event_id, location_id, description, date, conditions) values (18, 18, 'varius integer ac leo', '4/3/2022', 'Switchable zero administration encryption');
insert into event (event_id, location_id, description, date, conditions) values (19, 19, 'semper', '12/11/2023', 'Diverse national hierarchy');
insert into event (event_id, location_id, description, date, conditions) values (20, 20, 'nisi venenatis tristique fusce congue', '9/7/2021', 'Streamlined zero administration flexibility');
-- nastavuji sekvenci kterou identifikuji pomocí pg_get_serial_sequence na hodnotu 2 abych mohl pokračovat přidáváním dalších řádků
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('event', 'event_id'), 20);


insert into song (song_id, name) values (1, 'Push it');
insert into song (song_id, name) values (2, 'I am');
insert into song (song_id, name) values (3, 'love song');
insert into song (song_id, name) values (4, 'Remain Calm');
insert into song (song_id, name) values (5, 'Kids with guns');
insert into song (song_id, name) values (6, 'Happy inc.');
insert into song (song_id, name) values (7, 'ABCD');
insert into song (song_id, name) values (8, 'antichrist superstar');
insert into song (song_id, name) values (9, 'cap');
insert into song (song_id, name) values (10, 'pede');
insert into song (song_id, name) values (11, 'blues song');
insert into song (song_id, name) values (12, 'Imagine');
insert into song (song_id, name) values (13, 'let it be');
insert into song (song_id, name) values (14, 'suck my 401k');
insert into song (song_id, name) values (15, 'whistling dixie');
insert into song (song_id, name) values (16, 'the satanic rights of blacula');
insert into song (song_id, name) values (17, 'dracula');
insert into song (song_id, name) values (18, 'living dead girl');
insert into song (song_id, name) values (19, 'death trip to wisconsin');
insert into song (song_id, name) values (20, 'snot');
-- nastavuji sekvenci kterou identifikuji pomocí pg_get_serial_sequence na hodnotu 2 abych mohl pokračovat přidáváním dalších řádků
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('song', 'song_id'), 20);


INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (1, 'Ingra Pettendrich', '325-705-7937', 'ipettendrich0@sciencedaily.com', 'http://admin.ch', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (2, 'Heather Ganley', '989-869-0284', 'hganley1@eventbrite.com', 'https://bbb.org', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (3, 'Hart Winteringham', '334-425-1920', 'hwinteringham2@nationalgeographic.com', 'http://free.fr', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (4, 'Griffy Gosselin', '428-787-9863', 'ggosselin3@ocn.ne.jp', 'http://desdev.cn', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (5, 'Marcelo Tift', '389-256-1851', 'mtift4@yahoo.co.jp', 'http://skype.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (6, 'Dorie Londesborough', '834-492-1701', 'dlondesborough5@imgur.com', 'https://noaa.gov', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (7, 'Bartolomeo Knath', '207-381-8598', 'bknath6@statcounter.com', 'https://ibm.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (8, 'Ferdy Kalderon', '138-704-1462', 'fkalderon7@hhs.gov', 'http://wired.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (9, 'Osmond Matiebe', '563-621-6241', 'omatiebe8@xrea.com', 'https://istockphoto.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (10, 'Rex Witz', '536-916-1107', 'rwitz9@opera.com', 'http://fema.gov', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (11, 'Static-X', '999-121-9718', 'csedena@sfgate.com', 'http://wiley.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (12, 'Hannah Jackson', '667-381-7995', 'gveltib@edublogs.org', 'http://twitpic.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (13, 'The Beatles', '580-698-4740', 'jillistonc@virginia.edu', 'http://discuz.net', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (14, 'Valerie Theriot', '927-674-0266', 'vtheriotd@webeden.co.uk', 'http://dropbox.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (15, 'Courtnay Bartosik', '273-351-8347', 'cbartosike@hao123.com', 'http://sogou.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (16, 'Mar Farthing', '715-374-5966', 'mfarthingf@zimbio.com', 'http://exblog.jp', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (17, 'Adriena Nekrews', '904-935-3398', 'anekrewsg@fda.gov', 'https://google.nl', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (18, 'Natale Duthie', '178-207-8539', 'nduthieh@nymag.com', 'http://hhs.gov', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (19, 'Reagen Harrema', '531-293-2272', 'rharremai@tumblr.com', 'http://marketwatch.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (20, 'Hannah Jacksons', '265-769-3132', 'tbutteryj@chron.com', 'http://flickr.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (21, 'mariia123', '633-534-0875', 'lleasek@pinterest.com', 'http://twitpic.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (22, 'Mariia Ternavska', '263-840-2643', 'helkingtonl@engadget.com', 'http://dropbox.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (23, 'Phaidra Faull', '845-551-2238', 'pfaullm@instagram.com', 'https://joomla.org', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (24, 'Jamill Spyvye', '443-533-4791', 'jspyvyen@plala.or.jp', 'https://godaddy.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (25, 'Ame Licence', '644-451-0416', 'alicenceo@simplemachines.org', 'http://paginegialle.it', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (26, 'Janela covino', '668-264-3068', 'jcovinop@wikimedia.org', 'http://nhs.uk', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (27, 'Gauthier Spear', '821-903-3654', 'gspearq@thetimes.co.uk', 'https://blinklist.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (28, 'Georgie Tellenbrok', '532-517-4362', 'gtellenbrokr@a8.net', 'https://bloglines.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (29, 'Kirbee Farden', '425-415-0556', 'kfardens@wikia.com', 'http://army.mil', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (30, 'Angeli Gazey', '471-324-7319', 'agazeyt@usda.gov', 'http://biglobe.ne.jp', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (31, 'Jon Shotbolt', 'Shotbolt', 'jshotbolt0@cmu.edu', 'http://who.int', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (32, 'Felicle Bramley', 'Bramley', 'fbramley1@purevolume.com', 'https://hubpages.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (33, 'Ursala Neame', 'Neame', 'uneame2@typepad.com', 'https://sfgate.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (34, 'Beryle Moran', 'Moran', 'bmoran3@sourceforge.net', 'https://cloudflare.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (35, 'Augustine Novkovic', 'Novkovic', 'anovkovic4@omniture.com', 'https://cpanel.net', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (36, 'Kerry Leirmonth', 'Leirmonth', 'kleirmonth5@reddit.com', 'http://youtube.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (37, 'Georas Prestney', 'Prestney', 'gprestney6@gmpg.org', 'https://hhs.gov', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (38, 'Blaine Phillpotts', 'Phillpotts', 'bphillpotts7@dmoz.org', 'http://yandex.ru', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (39, 'Faustine de Cullip', 'de Cullip', 'fde8@jigsy.com', 'http://hexun.com', 'default_hash_placeholder');

INSERT INTO users (username, full_name, mobile_phone, email, links_media, password_hash)
VALUES (40, 'Christina Thick', 'Thick', 'cthick9@a8.net', 'http://berkeley.edu', 'default_hash_placeholder');

-- nastavuji sekvenci kterou identifikuji pomocí pg_get_serial_sequence na hodnotu 2 abych mohl pokračovat přidáváním dalších řádků
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('users', 'username'), 40);




insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (21, NULL, '10/13/1998', 'approach', 'Cross-platform bandwidth-monitored project', '4041379695717521', 'incremental', 0.00, '11/26/2024', 'GB14 CTOD 5100 4968 9633 58');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (22, 21, '3/10/1989', 'infrastructure', 'Vision-oriented regional complexity', '3575613836391457', 'multimedia', 9.08, '11/7/2024', 'FR72 9734 7929 21UN I6ER TWKI 211');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (23, 22, '3/23/1991', 'Open-architected', 'Customer-focused 6th generation solution', '3572490760100508', 'Optional', 4.45, '11/13/2024', 'IE26 SSHG 2001 5056 7298 26');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (24, 23, '3/6/2003', 'complexity', 'Expanded client-driven intranet', '5602235185700211', 'upward-trending', 7.93, '2/18/2024', 'HU26 0167 4230 6242 8249 4557 4384');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (25, 24, '6/19/1999', 'Synchronised', 'Horizontal content-based collaboration', '5108755482384178', 'Inverse', 0.00, '12/14/2024', 'PL77 1986 8694 1430 4055 5236 3859');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (26, 25, '2/26/1994', 'migration', 'Enhanced reciprocal application', '201551226536745', 'multimedia', 3.48, '6/16/2024', 'IT93 S266 6693 3995 YGUV WOYV ALU');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (27, 26, '4/17/1994', '24 hour', 'Future-proofed needs-based array', '3557166604752345', 'task-force', 7.92, '9/4/2024', 'GL54 7665 8258 9065 74');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (28, 27, '6/18/1998', 'moderator', 'Automated local Graphical User Interface', '3546317211682078', 'functionalities', 7.59, '5/25/2024', 'FR54 1327 1443 67YR TMPX ZLPE G86');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (29, 28, '5/17/1988', 'Intuitive', 'Profit-focused tertiary product', '3541832705656888', 'actuating', 0.00, '7/21/2024', 'GT03 H8WO TU5F M8VB NPI0 P7IU VJKX');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (30, 21, '2/18/1995', 'product', 'Focused homogeneous installation', '4913110143306426', 'success', 0.00, '10/10/2024', 'MD41 L2S1 JEO6 BSVR EFLJ G33C');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (31, 21, '2/15/1996', 'dynamic', 'Centralized full-range database', '3552729619277585', 'protocol', 3.13, '2/21/2024', 'BG39 JJFL 8293 37NI JQI4 5M');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (32, 22, '10/20/2003', 'solution-oriented', 'Proactive explicit paradigm', '3567284751836601', 'Multi-channelled', 5.83, '5/7/2024', 'FR94 7280 9193 27CO PXO6 UALT 521');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (33, 23, '5/20/1987', 'standardization', 'Cross-platform zero administration framework', '372707935828160', 'Right-sized', 3.58, '9/4/2024', 'IT37 X710 8622 030Q U4B5 Z3RB BL7');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (34, 24, '12/31/1992', 'mission-critical', 'Function-based object-oriented orchestration', '5602224351188328', 'directional', 6.94, '1/21/2024', 'HR64 5741 0192 8494 4935 1');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (35, 24, '2/13/2000', 'Grass-roots', 'Intuitive dynamic leverage', '4405553325711027', 'implementation', 8.89, '2/27/2024', 'DE10 0951 0360 6154 8290 96');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (36, 25, '10/25/1991', 'object-oriented', 'Persistent dynamic firmware', '3530835919622672', 'discrete', 6.53, '6/25/2024', 'EE11 0381 7415 3713 2538');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (37, 26, '6/27/1992', 'Persistent', 'Horizontal didactic help-desk', '3547629930274527', 'Reactive', 1.44, '1/6/2024', 'BH98 QLDX BQEH QSZN 8K5E ZN');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (38, 27, '10/25/1999', 'hybrid', 'Assimilated 24 hour internet solution', '3568554652025275', 'extranet', 8.15, '3/11/2024', 'BH98 GWJI OJL3 GN1O OSJM CO');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (39, 38, '8/2/2004', 'time-frame', 'Team-oriented dynamic open architecture', '374622830166194', 'productivity', 3.85, '02/27/2024', 'GB20 CAIG 5583 0896 1188 73');
insert into basic_user (username, basic_user_username, birth_date, preferences, profile_description, credit_card, subscription_type, subscription_price, subscription_date, bank_information) values (40, 39, '10/11/1986', 'time-frame', 'Secured context-sensitive database', '5048379803388561', 'uniform', 6.72, '10/25/2024', 'MU59 LOST 2599 3033 2800 4523 875D WG');



insert into manager_user (username, role_for_artist, tasks) values (1, 'artist manager', 'merchandise and booking');
insert into manager_user (username, role_for_artist, tasks) values (2, 'artist manager and promoter', 'booking and promotion');
insert into manager_user (username, role_for_artist, tasks) values (3, 'promotion', 'special events and advertisement');
insert into manager_user (username, role_for_artist, tasks) values (4, 'agent', 'shows, merchadise and promotion');
insert into manager_user (username, role_for_artist, tasks) values (5, 'artist manager', 'merchandise, adverts, colabs');


insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (11, 1, 'approach', 'De-engineered', 'Pop', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (12, 2, 'Versatile', 'Compatible', 'Alternative rock', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (13, 3, 'system-worthy', 'executive', 'Rock', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (14, 4, 'Adaptive', 'bandwidth-monitored', 'Groovy metal', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (15, 5, 'user-facing', 'uniform', 'k-pop', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (16, 1, 'Secured', '3rd generation', 'Pop', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (17, 1, 'Sharable', 'secured line', 'Rock', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (18, 2, 'Ergonomic', 'analyzer', 'Jazz', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (19, 4, 'most popular rock singer in the 90s', 'solution', 'Rock', NULL);
insert into artist_user (username, manager_user_username, discography, biography, genre, photos) values (20, 5, 'benchmark', 'Open-architected', 'Pop', NULL);


insert into content_moderator_user (username, tasks, moderation_history) values (6, 'moderate channel', NULL);
insert into content_moderator_user (username, tasks, moderation_history) values (7, 'content evaluation', 'deleted a post on 11/11/2023');
insert into content_moderator_user (username, tasks, moderation_history) values (8, 'monitor community guidelines', 'excluded user mariia123 from subscribers');
insert into content_moderator_user (username, tasks, moderation_history) values (9, 'database analyzer', NULL);
insert into content_moderator_user (username, tasks, moderation_history) values (10, 'check users` authentification', 'checked 100 users on 17/04/2024');

insert into event_artist_user (event_id, username) values (1, 16);
insert into event_artist_user (event_id, username) values (2, 15);
insert into event_artist_user (event_id, username) values (3, 14);
insert into event_artist_user (event_id, username) values (4, 13);
insert into event_artist_user (event_id, username) values (1, 12);
insert into event_artist_user (event_id, username) values (2, 12);
insert into event_artist_user (event_id, username) values (3, 12);
insert into event_artist_user (event_id, username) values (4, 12);
insert into event_artist_user (event_id, username) values (5, 12);
insert into event_artist_user (event_id, username) values (6, 12);
insert into event_artist_user (event_id, username) values (7, 12);
insert into event_artist_user (event_id, username) values (8, 12);
insert into event_artist_user (event_id, username) values (9, 12);
insert into event_artist_user (event_id, username) values (10, 12);
insert into event_artist_user (event_id, username) values (11, 12);
insert into event_artist_user (event_id, username) values (12, 12);
insert into event_artist_user (event_id, username) values (13, 12);
insert into event_artist_user (event_id, username) values (14, 12);
insert into event_artist_user (event_id, username) values (15, 12);
insert into event_artist_user (event_id, username) values (16, 12);
insert into event_artist_user (event_id, username) values (17, 12);
insert into event_artist_user (event_id, username) values (18, 12);
insert into event_artist_user (event_id, username) values (19, 12);
insert into event_artist_user (event_id, username) values (20, 12);
insert into event_artist_user (event_id, username) values (15, 13);
insert into event_artist_user (event_id, username) values (16, 14);
insert into event_artist_user (event_id, username) values (17, 11);
insert into event_artist_user (event_id, username) values (18, 15);
insert into event_artist_user (event_id, username) values (19, 15);
insert into event_artist_user (event_id, username) values (20, 17);
insert into event_artist_user (event_id, username) values (11, 18);
insert into event_artist_user (event_id, username) values (12, 19);
insert into event_artist_user (event_id, username) values (13, 20);


-- insert into content_moderator_user (username, tasks, moderation_history) values (6, 'moderate channel', NULL);
-- insert into content_moderator_user (username, tasks, moderation_history) values (7, 'content evaluation', 'deleted a post on 11/11/2023');
-- insert into content_moderator_user (username, tasks, moderation_history) values (8, 'monitor community guidelines', 'excluded user mariia123 from subscribers');
-- insert into content_moderator_user (username, tasks, moderation_history) values (9, 'database analyzer', NULL);
-- insert into content_moderator_user (username, tasks, moderation_history) values (10, 'check users` authentification', 'checked 100 users on 17/04/2024');

insert into song_artist_user (song_id, username) values (1, 11);
insert into song_artist_user (song_id, username) values (2, 11);
insert into song_artist_user (song_id, username) values (3, 17);
insert into song_artist_user (song_id, username) values (4, 14);
insert into song_artist_user (song_id, username) values (5, 15);
insert into song_artist_user (song_id, username) values (6, 16);
insert into song_artist_user (song_id, username) values (7, 17);
insert into song_artist_user (song_id, username) values (8, 18);
insert into song_artist_user (song_id, username) values (9, 19);
insert into song_artist_user (song_id, username) values (10, 14);
insert into song_artist_user (song_id, username) values (11, 16);
insert into song_artist_user (song_id, username) values (12, 13);
insert into song_artist_user (song_id, username) values (13, 13);
insert into song_artist_user (song_id, username) values (14, 14);
insert into song_artist_user (song_id, username) values (15, 15);
insert into song_artist_user (song_id, username) values (16, 16);
--insert into song_artist_user (song_id, username) values (37 87);
insert into song_artist_user (song_id, username) values (18, 18);
insert into song_artist_user (song_id, username) values (19, 19);
insert into song_artist_user (song_id, username) values (20, 20);



insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (1, 'Chanel123', 6, 1, 'Business-focused exuding migration', 'Rock', 'prlog.org/libero/rutrum/ac/lobortis/vel/dapibus.png');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (2, 'Ernser LLC', 7, 2, 'Front-line stable application', 'Pop', 'addtoany.com/sapien/iaculis/congue/vivamus/metus/arcu.png');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (3, 'Champlin, Hermann and Keebler', 8, 3, 'Multi-lateral client-driven paradigm', 'Classical', 'prlog.org/aliquet/at/feugiat/non.jpg');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (4, 'Bosco and Sons', 9, 4, 'Digitized regional superstructure', 'Groovy metal', 'icio.us/imperdiet/et/commodo/vulputate/justo/in/blandit.xml');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (5, 'Schoen, Blanda and O''Kon', 10, 5, 'Function-based needs-based intranet', 'techno', 'imgur.com/morbi/non/lectus/aliquam/sit.js');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (6, 'Larson-Runolfsdottir', 7, 6, 'Streamlined exuding monitoring', 'Rock', 'google.it/nunc/vestibulum/ante.html');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (7, 'Collier Group', 7, 7, 'Grass-roots even-keeled model', 'Hard rock', 'jimdo.com/nec/condimentum/neque/sapien/placerat/ante.xml');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (8, 'Pacocha Group', 8, 8, 'Balanced mission-critical budgetary management', NULL, 'theatlantic.com/aliquet/ultrices/erat/tortor/sollicitudin/mi/sit.jpg');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (9, 'Abernathy-Moen', 9, 9, 'Digitized discrete infrastructure', NULL, 'usgs.gov/lorem/vitae/mattis/nibh/ligula/nec.json');
insert into public_channel (channel_id, channel_name, username, location_id, description, preferred_genre, link) values (10, 'Schneider, Huel and Thompson', 10, 10, 'Object-based next generation complexity', NULL, 'umich.edu/nullam.json');
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('public_channel', 'channel_id'), 10);


insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (1, 12, 'Jacket', 'under a week', 'migration', '63.76', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (2, 13, 'Stickers', 'international', 'Persistent', '26.67', false);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (3, 14, 'Shopper', '14-days', 'Upgradable', '42.60', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (4, 13, 'Blue trousers', 'international', 'Operative', '88.26', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (5, 16, 'White shirt', 'optimal', 'Enhanced', '23.16', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (6, 17, 'Pink shorts', 'international', 'data-warehouse', '96.91', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (7, 18, 'Sweatpants', 'Customizable', 'implementation', '75.76', false);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (8, 19, 'Red hoodie', 'international', 'function', '12.33', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (9, 20, 'Pink hoodie', '14-days', 'eco-centric', '85.23', false);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (10, 11, 'Contact lenses', '14 to 21 days', 'Up-sized', '42.28', false);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (11, 12, 'Phone case', 'up to 21 days', 'portal', '49.59', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (12, 13, 'Phone case', 'internet solution', 'Enterprise-wide', '43.10', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (13, 14, 'Temp', 'secondary', 'under a week', '45.85', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (14, 15, 'Red jacket', 'flexible', 'Realigned', '40.06', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (15, 16, 'Pink hoodie', 'Europe only', 'Multi-channelled', '58.79', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (16, 17, 'Blue shorts', 'international', 'benchmark', '76.60', true);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (17, 18, 'Running shoes', 'USA only', 'middleware', '78.25', false);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (18, 19, 'Cup', 'Upgradable', 'under 5 days', '5.41', false);
insert into merchandise_product (product_id, username, product_name, shipping, description, product_price, availibility) values (19, 20, 'Sneakers', 'intangible', 'Automated', '78.40', true);
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('merchandise_product', 'product_id'), 19);



insert into playlist (playlist_id, username, description, link) values (1, 21, 'Inverse', 'https://fema.gov');
insert into playlist (playlist_id, username, description, link) values (2, 22, 'modular', 'https://wordpress.com');
insert into playlist (playlist_id, username, description, link) values (3, 23, 'optimal', 'https://yahoo.co.jp');
insert into playlist (playlist_id, username, description, link) values (4, 24, 'explicit', 'https://tmall.com');
insert into playlist (playlist_id, username, description, link) values (5, 25, 'hub', 'https://delicious.com');
insert into playlist (playlist_id, username, description, link) values (6, 26, 'encoding', 'http://scientificamerican.com');
insert into playlist (playlist_id, username, description, link) values (7, 27, 'intranet', 'http://over-blog.com');
insert into playlist (playlist_id, username, description, link) values (8, 28, 'Multi-tiered', 'https://ebay.co.uk');
insert into playlist (playlist_id, username, description, link) values (9, 29, 'modular', 'https://amazonaws.com');
insert into playlist (playlist_id, username, description, link) values (10, 30, 'holistic', 'https://ebay.com');
SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('playlist', 'playlist_id'), 10);


insert into song_playlist (song_id, playlist_id) values (1, 1);
insert into song_playlist (song_id, playlist_id) values (2, 2);
insert into song_playlist (song_id, playlist_id) values (3, 3);
insert into song_playlist (song_id, playlist_id) values (4, 4);
insert into song_playlist (song_id, playlist_id) values (5, 5);
insert into song_playlist (song_id, playlist_id) values (6, 6);
insert into song_playlist (song_id, playlist_id) values (7, 7);
insert into song_playlist (song_id, playlist_id) values (8, 8);
insert into song_playlist (song_id, playlist_id) values (9, 9);
insert into song_playlist (song_id, playlist_id) values (10, 10);
insert into song_playlist (song_id, playlist_id) values (11, 1);
insert into song_playlist (song_id, playlist_id) values (12, 2);
insert into song_playlist (song_id, playlist_id) values (13, 3);
insert into song_playlist (song_id, playlist_id) values (14, 4);
insert into song_playlist (song_id, playlist_id) values (15, 5);
insert into song_playlist (song_id, playlist_id) values (16, 6);
insert into song_playlist (song_id, playlist_id) values (17, 7);
