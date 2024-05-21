from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    MetaData,
    String,
    Table,
    func,
)

DB_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_`%(constraint_name)s`",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

user = Table(
    "user",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("name", String, nullable=False),
    Column("email", String, index=True, unique=True, nullable=False),
    Column("hash_password", String, nullable=False),
    Column(
        "create_at", DateTime, server_default=func.now(), index=True, nullable=False
    ),
    Column("login_at", DateTime, onupdate=func.now(), index=True),
    Column("profile_image_url", String),
)

package = Table(
    "package",
    metadata,
    Column("id", String, primary_key=True),
    Column("create_at", DateTime, server_default=func.now(), index=True),
    Column("update_at", DateTime, onupdate=func.now(), index=True),
    Column("summary", String, nullable=False),
    Column("description", String, nullable=True),
    Column("home_page", String),
    Column("docs_url", String),
    Column("package_url", String),
    Column("author_name", String),
    Column("author_email", String, index=True, nullable=False),
    Column("license", String, nullable=True),
)

release = Table(
    "release",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("major_ver", BigInteger, index=True, nullable=False),
    Column("minor_ver", BigInteger, index=True),
    Column("build_ver", BigInteger, index=True),
    Column(
        "create_at", DateTime, server_default=func.now(), index=True, nullable=False
    ),
    Column("comment", String),
    Column("url", String),
    Column("size", BigInteger),
    Column("package_id", String, ForeignKey("package.id", ondelete="CASCADE")),
)

maintainer = Table(
    "maintainer",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("maintainer", String),
    Column("maintainer_email", String),
    Column("profile_image_url", String),
    Column("package_id", String, ForeignKey("package.id", ondelete="CASCADE")),
)
