#!/usr/bin/env python

# Copyright (c) LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import pymysql.cursors
import sys
import re
import oncall.utils


def main():
    if len(sys.argv) <= 2:
        sys.exit("USAGE: %s CONFIG_FILE SQL_FILE" % sys.argv[0])

    config = oncall.utils.read_config(sys.argv[1])
    db = config["db"]["conn"]["kwargs"]

    sql_file = sys.argv[2]

    # Connect to the database
    connection = pymysql.connect(
        host=db["host"],
        user=db["user"],
        password=db["password"],
        database=db["database"],
        cursorclass=pymysql.cursors.DictCursor,
    )

    with open(sql_file) as f:
        with connection:
            with connection.cursor() as c:
                for stmt in f.read().split(");"):
                    if (
                        stmt.startswith("CREATE DATABASE")
                        or stmt.startswith("USE ")
                        or re.match(r"^\s*$", stmt)
                    ):
                        continue
                    stmt = stmt + ")"
                    print("Executing:\n"+stmt+"\n")
                    c.execute(stmt)


if __name__ == "__main__":
    main()
