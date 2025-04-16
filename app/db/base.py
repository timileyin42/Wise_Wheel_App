from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Enable PostGIS extension in SQLAlchemy
def configure_models(base):
    base.metadata.add_extension('postgis')
