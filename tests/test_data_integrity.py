"""Data integrity test identities backed by focused semantic mixins."""

from ._data_integrity_cases import (
    _ForeignKeyConstraintMixin,
    _IngestWriteOrderingMixin,
    _SchemaMigrationMixin,
    _SQLiteVectorConsistencyMixin,
    _SqlSafetyMixin,
    _StorageTypeContractMixin,
)


class TestSchemaIdempotency(_SchemaMigrationMixin):
    """Verify that init_schema can be called twice without error."""


class TestConsistencyCheck(_SQLiteVectorConsistencyMixin):
    """Verify the consistency_check method."""


class TestSqlInjectionSurface(_SqlSafetyMixin):
    """Verify _escape_like and parameterized queries prevent injection."""


class TestDataTypeContracts(_StorageTypeContractMixin):
    """Verify UIDs are strings, JSON columns are valid, booleans are 0/1."""


class TestForeignKeys(_ForeignKeyConstraintMixin):
    """Verify PRAGMA foreign_keys=ON is active."""


class TestPipelineWriteOrdering(_IngestWriteOrderingMixin):
    """Verify SQLite is written before vector storage in _process_batch."""
