from django.test.runner import DiscoverRunner


class NazRiyTestRunner(DiscoverRunner):
    """Clean up PostgreSQL test database connections before teardown.

    Supabase/local PostgreSQL connections can occasionally stay open long
    enough for Django's final DROP DATABASE step to fail with ObjectInUse.
    The tests have already passed at that point, so before teardown we ask
    PostgreSQL to terminate any remaining sessions for the temporary test DB.
    """

    def setup_databases(self, **kwargs):
        if not self.keepdb:
            from django.db import connections

            for alias in connections.databases:
                connection = connections[alias]
                if connection.vendor == "postgresql":
                    self._drop_stale_test_database(connection)

        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        postgres_only = all(
            connection.vendor == "postgresql" for connection, _old_name, _destroy in old_config
        )
        if postgres_only:
            for connection, _old_name, _destroy in old_config:
                connection.close()
            return

        return super().teardown_databases(old_config, **kwargs)

    def _terminate_test_database_sessions(self, connection):
        test_database_name = connection.settings_dict.get("NAME")
        if not test_database_name:
            return

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                  AND pid <> pg_backend_pid();
                """,
                [test_database_name],
            )

    def _drop_stale_test_database(self, connection):
        test_database_name = connection.creation._get_test_db_name()
        if not test_database_name or not test_database_name.startswith("test_"):
            return

        connection.ensure_connection()
        connection.set_autocommit(True)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s
                  AND pid <> pg_backend_pid();
                """,
                [test_database_name],
            )
            cursor.execute(
                f"DROP DATABASE IF EXISTS {connection.ops.quote_name(test_database_name)};"
            )
