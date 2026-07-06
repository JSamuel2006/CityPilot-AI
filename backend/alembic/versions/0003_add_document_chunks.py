"""add_document_chunks_table

Revision ID: 0003_document_chunks
Revises: 0002_gis_indexes
Create Date: 2026-07-06

Adds the document_chunks table required by the LangChain RAG pipeline.
Each chunk stores a text fragment and its embedding as a float array.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0003_document_chunks"
down_revision: Union[str, Sequence[str], None] = "0002_gis_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create document_chunks table."""
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_filename", sa.String(255), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("embedding", sa.ARRAY(sa.Float()), nullable=False),
    )
    op.create_index("ix_document_chunks_id", "document_chunks", ["id"])
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])


def downgrade() -> None:
    """Drop document_chunks table."""
    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_index("ix_document_chunks_id", table_name="document_chunks")
    op.drop_table("document_chunks")
