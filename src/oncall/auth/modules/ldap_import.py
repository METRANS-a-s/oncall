# Copyright (c) LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.
import ldap
from oncall import db
import os
import logging
from oncall.user_sync.ldap_sync import user_exists, import_user, update_user
from falcon import HTTPNotFound
import oncall.utils
import sys

logger = logging.getLogger(__name__)


class Authenticator:
    def __init__(self, config):
        if config.get('debug'):
            self.authenticate = self.debug_auth
            return
        self.authenticate = self.ldap_auth

        # if 'ldap_cert_path' in config:
        #     self.cert_path = config['ldap_cert_path']
        #     if not os.access(self.cert_path, os.R_OK):
        #         logger.error("Failed to read ldap_cert_path certificate")
        #         raise IOError
        # else:
        #     self.cert_path = None

        # self.bind_user = config.get('ldap_bind_user')
        # self.bind_password = config.get('ldap_bind_password')
        # self.search_filter = config.get('ldap_search_filter')

        # self.ldap_url = config.get('ldap_url')
        # self.base_dn = config.get('ldap_base_dn')

        # self.user_suffix = config.get('ldap_user_suffix')
        # self.import_user = config.get('import_user', False)
        # self.attrs = config.get('attrs')

    def get_ldap_config(self, config, ldap_domain):
        if ldap_domain not in config['ldap']:
            raise HTTPNotFound(
                title='Chosen domain not found',
                description='LDAP Domain "%s" not found' % ldap_domain
            )

        ldap_config = config['ldap'][ldap_domain]
        
        return {
            'cert_path': ldap_config.get('ldap_cert_path'),
            'bind_user': ldap_config.get('ldap_bind_user'),
            'bind_password': ldap_config.get('ldap_bind_password'),
            'search_filter': ldap_config.get('ldap_search_filter'),
            'ldap_url': ldap_config.get('ldap_url'),
            'base_dn': ldap_config.get('ldap_base_dn'),
            'user_suffix': ldap_config.get('ldap_user_suffix'),
            'import_user': ldap_config.get('import_user', False),
            'attrs': ldap_config.get('attrs')
        }

    def ldap_auth(self, username, password, ldap_domain):
        config = oncall.utils.read_config(sys.argv[1])['auth']

        ldap_config = self.get_ldap_config(config, ldap_domain)

        logger.info(ldap_config)

        if ldap_config['cert_path'] is not None and ldap_config['cert_path'] != '':
            logger.info("Setting LDAP TLS CA Cert File to %s", ldap_config['cert_path'])
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, ldap_config['cert_path'])

        connection = ldap.initialize(ldap_config['ldap_url'])
        connection.set_option(ldap.OPT_REFERRALS, 0)
        attrs = ['dn'] + list(ldap_config['attrs'].values())
        ldap_contacts = {}

        if not password:
            return False

        auth_user = username + ldap_config['user_suffix']
        try:
            if ldap_config['bind_user']:
                # use search filter to find DN of username
                connection.simple_bind_s(ldap_config['bind_user'], ldap_config['bind_password'])
                sfilter = ldap_config['search_filter'] % username
                result = connection.search_s(ldap_config['base_dn'], ldap.SCOPE_SUBTREE, sfilter, attrs)
                if len(result) < 1:
                    return False
                auth_user = result[0][0]
                ldap_attrs = result[0][1]
                for key, val in ldap_config['attrs'].items():
                    if ldap_attrs.get(val):
                        if type(ldap_attrs.get(val)) == list:
                            ldap_contacts[key] = ldap_attrs.get(val)[0]
                        else:
                            ldap_contacts[key] = ldap_attrs.get(val)
                    else:
                        ldap_contacts[key] = val

            connection.simple_bind_s(auth_user, password)

        except ldap.INVALID_CREDENTIALS:
            return False
        except (ldap.SERVER_DOWN, ldap.INVALID_DN_SYNTAX) as err:
            logger.warn("%s", err)
            return None

        if ldap_config['import_user']:
            connection = db.connect()
            cursor = connection.cursor(db.DictCursor)
            if user_exists(username, cursor):
                logger.info("user %s already exists, updating from ldap", username)
                update_user(username, ldap_contacts, cursor)
            else:
                logger.info("user %s does not exists. importing.", username)
                import_user(username, ldap_contacts, cursor)
            connection.commit()
            cursor.close()
            connection.close()

        return True

    def debug_auth(self, username, password, ldap_domain):
        return True
