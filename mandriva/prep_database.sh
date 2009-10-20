#!/bin/bash

DB_USER=openerp
# DB_NAME=openerp
DB_GROUP=

# This script assumes still that any local user can connect as 'postgres'
# to the local db. TODO: use any appropriate tool (su) when this is not true.

if [ -z "$PG_ROOT" ] ; then
	PG_ROOT=postgres
fi

if ! (psql -qt -U $PG_ROOT -c "SELECT usename FROM pg_user WHERE usename = '$DB_USER';" template1 | \
	grep $DB_USER > /dev/null) ; then
	if ! createuser -U "$PG_ROOT" -S -D -R -l $DB_USER < /dev/null ; then
		echo "Failed to create user $DB_USER"
		exit 1
	fi
else
	echo "User $DB_USER already exists."
fi

if [ -n "$DB_GROUP" ] ; then
    if ! (psql -qt -U $PG_ROOT -c "SELECT groname FROM pg_group WHERE groname = '$DB_GROUP';" template1 | \
	grep $DB_GROUP > /dev/null) ; then
	if ! psql -qt -U $PG_ROOT -c "CREATE GROUP $DB_GROUP; " template1 ; then
		echo "Failed to create group $DB_GROUP"
		exit 1
	fi
    else
	echo "Group $DB_GROUP already exists."
    fi
fi

# not good: we're enabling plpgsql for everybody!
DB_PLPGNAME=template1

if [ -n "$DB_NAME" ] ; then
    if (psql -qt -U $PG_ROOT -c "SELECT datname FROM pg_database WHERE datname = '$DB_NAME';" template1 | \
	grep $DB_NAME > /dev/null ) ; then
	echo -n "Database $DB_NAME already exists." 
	if [ "$1" != "--force"  ] ; then
		echo " It is not wise to continue."
		exit 2
	else
		echo " Continuing anyway."
	fi
    else
	createdb -O $DB_USER -E UTF8 -U $PG_ROOT $DB_NAME || exit $?
    fi
DB_PLPGNAME="$DB_NAME"
fi


if ! (psql -qt -U $PG_ROOT -c "SELECT lanname FROM pg_language WHERE lanname = 'plpgsql';" $DB_PLPGNAME | \
	grep 'plpgsql' > /dev/null) ; then
	if ! psql -U $PG_ROOT -d $DB_PLPGNAME --set ON_ERROR_STOP= -c 'CREATE LANGUAGE plpgsql;' ; then
		ERR_CODE=$?
		echo "Cannot use plpgsql. Do you have the language module installed?"
		exit 2
	fi
fi

echo "Database prepared successfully!"
#eof
