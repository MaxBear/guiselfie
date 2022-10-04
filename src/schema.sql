select id, email from  user where email not like "%mns.vc%" and email not like "%selfie.vc%" and email not like "%ivr.vc%";

CREATE TABLE company (
   company_id INT NOT NULL AUTO_INCREMENT,
   name varchar(255) NOT NULL DEFAULT "",
   PRIMARY KEY (`company_id`),
   UNIQUE KEY `name` (`name`)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

ALTER TABLE user ADD COLUMN company_id int(11) admin;

select id, email from  user where email not like "%mns.vc%" and email not like "%selfie.vc%" and email not like "%ivr.vc%";

UNIQUE KEY `email` (`email`) FOREIGN KEY (company_id) REFERENCES companies(id)

ALTER TABLE user ADD active tinyint(1) NOT NULL DEFAULT 1;
ALTER TABLE user ADD FOREIGN KEY (company_id) REFERENCES companies(company_id);
alter table user add unique key (email);

ALTER TABLE user modify COLUMN company_id int NOT NULL;
ALTER TABLE Selfie_Hosts ADD company_id int(11) not null;
ALTER TABLE Selfie_Hosts ADD CONSTRAINT fk_company_id FOREIGN KEY (company_id) REFERENCES company(company_id);
ALTER TABLE Selfie_Hosts DROP COLUMN Tag;
ALTER TABLE Selfie_Hosts CHANGE Host Tag varchar(80) NOT NULL default "";

# visa deployment

INSERT INTO company (name) values ("visa");
INSERT INTO Selfie_Hosts (RendServerIp, Tag, SipAddr, company_id) VALUES (3106176436, "visa", "sip:visa@selfie.vc", 2);
INSERT INTO Selfie_Hosts (RendServerIp, Tag, SipAddr, company_id) VALUES (3106176516, "visa", "sip:visa@selfie.vc", 2);
INSERT INTO Selfie_Hosts (RendServerIp, Tag, SipAddr, company_id) VALUES (3106176532, "visa", "sip:visa@selfie.vc", 2);

update Selfie_Hosts set company_id = 8 where Tag="visa";

create table alerts(
	alert_id INT NOT NULL AUTO_INCREMENT,
	company_id INT NOT NULL,
	user_id INT NOT NULL,
	src_addr varchar(80) default "any",
	dst_addr varchar(80) default "any",
	video_rx_lost float default 0,
	video_tx_lost float default 0,
	audio_rx_lost float default 0,
	audio_tx_lost float default 0,
	content_rx_lost float default 0,
   dst_email varchar(80) default "",
	PRIMARY KEY (alert_id),
	CONSTRAINT fk_alerts_company FOREIGN KEY (company_id) REFERENCES company(company_id),
	CONSTRAINT fk_alerts_user FOREIGN KEY (user_id) REFERENCES user(id)
) DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
