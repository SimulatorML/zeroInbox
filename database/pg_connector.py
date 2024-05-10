import psycopg2
from psycopg2 import pool
from typing import Tuple, Dict, List
from loguru import logger


class PgConnector:
    """
    A singleton class to manage connections to a PostgreSQL database.

    Attributes:
        _instance (PgConnector): Singleton instance of PgConnector.
        _connection_pool (psycopg2.pool.SimpleConnectionPool): Connection pool for managing database connections.
    """
    _instance = None
    _connection_pool = None

    def __new__(cls, host, database, port, user, password):
        """
        Ensure only one instance of PgConnector is created.

        Args:
            host (str): Database host address.
            database (str): Name of the database.
            port (int): Port number.
            user (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            PgConnector: The singleton instance of PgConnector.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            cls._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=host,
                database=database,
                port=port,
                user=user,
                password=password
            )

        return cls._instance

    def connect(self):
        """
        Get a connection from the connection pool.

        Returns:
            psycopg2.extensions.connection: A database connection.
        """
        return self._connection_pool.getconn()

    def disconnect(self, conn):
        """
        Return a connection to the connection pool.

        Args:
            conn (psycopg2.extensions.connection): Connection to be returned.
        """
        self._connection_pool.putconn(conn)

    def save_data(self, query: str, params: Dict) -> Tuple[int, str]:
        """
        Execute a query to save data into the database.

        Args:
            query (str): SQL query.
            params (Dict): Parameters to be used in the query.

        Returns:
            Tuple[int, str]: A tuple containing a status code (0 for success, 1 for failure) and a message.
        """
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)
            conn.commit()
            return 0, 'OK'
        except psycopg2.Error as e:
            logger.exception(f'psycopg2.Error: {e}')
            conn.rollback()
            return 1, e.args[0]
        finally:
            cursor.close()
            self.disconnect(conn)

    def get_data(self, query: str, params: Dict) -> Tuple[int, str, List]:
        """
        Execute a query to retrieve data from the database.

        Args:
            query (str): SQL query.
            params (Dict): Parameters to be used in the query.

        Returns:
            Tuple[int, str, List]: A tuple containing a status code (0 for success, 1 for failure),
            a message and a list of fetched data.
        """
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)
            return 0, 'OK', cursor.fetchall()
        except KeyError as e:
            logger.exception('Query params error: {e}')
            return 1, f'Query params error: {e}', []
        except Exception as e:
            logger.exception(f'Exception during `save_data`: {e}')
            return 2, e.args[0], []
        finally:
            cursor.close()
            self.disconnect(conn)
