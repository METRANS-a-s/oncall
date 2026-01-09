-- -----------------------------------------------------
-- Create Table `ldap_domain`
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS `ldap_domain` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `display_name` CHAR(255) NOT NULL,
  `active` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`)
);
