from sqlalchemy import create_engine
import ssl

connect = None
DictCursor = None
IntegrityError = None


def init(config):
    global connect
    global DictCursor
    global IntegrityError

    connect_args = {}
    if config['conn'].get('use_ssl'):
        ssl_ctx = ssl.create_default_context()
        connect_args["ssl"] = ssl_ctx

    engine = create_engine(
        config['conn']['str'] % config['conn']['kwargs'],
        connect_args=connect_args,
        **config['kwargs']
    )

    dbapi = engine.dialect.dbapi
    IntegrityError = dbapi.IntegrityError

    DictCursor = dbapi.cursors.DictCursor
    connect = engine.raw_connection

    if config['conn'].get('migrate_on_startup'):
        connection = connect()
        cursor = connection.cursor(DictCursor)
        cursor.execute('ALTER TABLE `role` ADD COLUMN IF NOT EXISTS `display_name` varchar(100) NULL')
        # UPDATE ALL INSTANCES OF DEVOPS TO SHADOW
        cursor.execute('''UPDATE `event` SET `role_id`=32 WHERE `id`=33''')
        cursor.execute('''UPDATE `schedule` SET `role_id`=32 WHERE `id`=33''')
        cursor.execute('''UPDATE `setting_role` SET `role_id`=32 WHERE `id`=33''')
        cursor.execute('''UPDATE `team_subscription` SET `role_id`=32 WHERE `id`=33''')

        # REMOVE DEVOPS IN ROLE
        cursor.execute('''DELETE FROM `role` WHERE `id`=33''')

        # ADD PRIMARY ROLE
        cursor.execute('''INSERT INTO `role` (`id`, `name`, `display_name`, `display_order`) VALUES (34, 'primary', 'L1', 1)''')

        # SET NORMAL NAMES
        cursor.execute('''UPDATE `role` SET `name`='secondary' WHERE `id`=31''')
        cursor.execute('''UPDATE `role` SET `name`='shadow' WHERE `id`=32''')

        # SET NORMAL DISPLAY ORDER
        cursor.execute('''UPDATE `role` SET `display_order`=2 WHERE `id`=31''')
        cursor.execute('''UPDATE `role` SET `display_order`=3 WHERE `id`=32''')

        # SET NORMAL DISPLAY NAME
        cursor.execute('''UPDATE `role` SET `display_name`='L2' WHERE `id`=31''')
        cursor.execute('''UPDATE `role` SET `display_name`='L3 + DevOps' WHERE `id`=32''')

        connection.commit()
        cursor.close()
        connection.close()
