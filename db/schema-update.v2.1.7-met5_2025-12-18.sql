-- -----------------------------------------------------
-- Update to Table `role`
-- -----------------------------------------------------

ALTER TABLE `role`
    ADD COLUMN IF NOT EXISTS display_name varchar(100) NULL;
