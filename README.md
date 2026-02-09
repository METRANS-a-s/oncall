# Oncall

## Description
- Fork of the official oncall repository, enhanced with features like limited visibility, bug fixes and more.

## Features
- Official oncall documentation can be found [here](https://oncall.tools/docs/index.html). Read changes below first to see if the information you're searching for is still valid
- Limited visibility of events depending on display_order of roles linked to them
    - If you're an user with a schedule that has a role linked to it then you get the priviledge of that role. If you have multiple schedules, the highest display_order of the roles will be chosen. These priviledges only apply within a team
    - If you're someone who has no schedule with a role or are not even logged in, then you will be treated as if your display_order was 0
    - If your display order is higher than or equal to the display order of people in a roster linked to a schedule, you will be able to see all of those people's events and contact information at all times
    - If your display order is lower by one, you will only see the contact information and active event of the people one above you
    - If your display order is lower by two, you will not see those people at all
    - Team admins are only visible to people with display_order of 2 or higher
- Limited visibility of some parts of the app
    - Unlogged users do not see anything besides teams and inside teams only the calendar and team info
    - Only admins see the scheduling templates, subscriptions and audit logs of teams
- Limited priviledges
    - Unlogged users cannot create or edit events
- Multiple LDAP options
    - LDAP authentication accepts more than one option and in combination with with the ldap_domain table in sql, a dropdown for unlogged users appears where they can choose from the multiple LDAP options
- Additional display_name to roles so that they have human readable names
- Many CSS fixes
- Fixed broken routing in chromium based browsers
- Main page is replaced by the teams page

### Development
- docker:
    - `docker build -t oncall:dev . && docker run -p 8080:8080 oncall:dev`
- docker compose:
    - `docker compose -f docker-compose.yaml up -d --build`
    - in the configuration there are two instances of oncall images, one for the runtime and another for initialization. there's also a mysql image for db.
        - oncall is running on localhost:8080
        - mysql is running on localhost:3306
