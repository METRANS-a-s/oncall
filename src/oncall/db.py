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
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='L1' WHERE `name`='L1' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='L2' WHERE `name`='L2' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='L3 + DevOps' WHERE `name`='L3' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='L3 + DevOps' WHERE `name`='Devops' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `name`='primary' WHERE `name`='L1' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `name`='secondary' WHERE `name`='L2' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `name`='shadow' WHERE `name`='L3' ''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='Manažeři' WHERE `id`=4''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='Dovolené' WHERE `id`=5''')
        # cursor.execute('''UPDATE `oncall`.`role` SET `display_name`='Nedostupní' WHERE `id`=6''')
        connection.commit()
        cursor.close()
        connection.close()
