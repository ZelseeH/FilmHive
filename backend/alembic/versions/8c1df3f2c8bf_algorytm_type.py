"""algorytm_type

Revision ID: 8c1df3f2c8bf
Revises: b66fe2649af4
Create Date: 2025-10-20 18:11:15.702858

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8c1df3f2c8bf"
down_revision: Union[str, None] = "b66fe2649af4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Dodaje kolumnę algorithm_type do tabeli recommendations
    oraz modyfikuje unique constraint
    """
    # 1. Dodaj kolumnę algorithm_type (nullable=True tymczasowo)
    op.add_column(
        "recommendations", sa.Column("algorithm_type", sa.String(20), nullable=True)
    )

    # 2. Wypełnij istniejące rekordy domyślną wartością 'knn'
    op.execute(
        "UPDATE recommendations SET algorithm_type = 'knn' WHERE algorithm_type IS NULL"
    )

    # 3. Zmień kolumnę na NOT NULL
    op.alter_column(
        "recommendations", "algorithm_type", nullable=False, server_default="knn"
    )

    # 4. Dodaj index na algorithm_type
    op.create_index(
        op.f("ix_recommendations_algorithm_type"),
        "recommendations",
        ["algorithm_type"],
        unique=False,
    )

    # 5. Usuń stary constraint unique_user_movie_recommendation
    op.drop_constraint(
        "unique_user_movie_recommendation", "recommendations", type_="unique"
    )

    # 6. Dodaj nowy constraint z algorithm_type
    op.create_unique_constraint(
        "unique_user_movie_algorithm_recommendation",
        "recommendations",
        ["user_id", "movie_id", "algorithm_type"],
    )


def downgrade() -> None:
    """
    Cofa zmiany - przywraca poprzedni stan tabeli recommendations
    """
    # 1. Usuń nowy constraint
    op.drop_constraint(
        "unique_user_movie_algorithm_recommendation", "recommendations", type_="unique"
    )

    # 2. Usuń duplikaty (zachowaj tylko pierwszy rekord dla każdego user+movie)
    # WAŻNE: To usunie rekordy z algorithm_type != 'knn' jeśli są duplikaty
    op.execute(
        """
        DELETE FROM recommendations 
        WHERE recommendation_id NOT IN (
            SELECT MIN(recommendation_id) 
            FROM recommendations 
            GROUP BY user_id, movie_id
        )
        """
    )

    # 3. Przywróć stary constraint (bez algorithm_type)
    op.create_unique_constraint(
        "unique_user_movie_recommendation", "recommendations", ["user_id", "movie_id"]
    )

    # 4. Usuń index
    op.drop_index(
        op.f("ix_recommendations_algorithm_type"), table_name="recommendations"
    )

    # 5. Usuń kolumnę algorithm_type
    op.drop_column("recommendations", "algorithm_type")
