from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import nh3

Base = declarative_base()
engine = create_engine('sqlite:///igs_data.db')

class CensusTract(Base):
    __tablename__ = 'census_tracts'
    id = Column(Integer, primary_key=True)
    census_tract = Column(String, unique=True)
    inclusion_score = Column(Float)
    growth_score = Column(Float)
    economy_score = Column(Float)
    community_score = Column(Float)

Base.metadata.create_all(engine)

def init_db():
    try:
        df = pd.read_csv("igs_data.csv")
        # Ensure census_tract is a string and remove leading/trailing spaces
        df['census_tract'] = df['census_tract'].astype(str).str.strip()
        
        with sessionmaker(bind=engine)() as session:
            # Check what's already in the DB
            existing_tracts = {str(row.census_tract) for row in session.query(CensusTract.census_tract).all()}
            
            for _, row in df.iterrows():
                # Only add if it's NOT in the database already
                if row["census_tract"] not in existing_tracts:
                    tract = CensusTract(
                        census_tract=nh3.clean(row["census_tract"]),
                        inclusion_score=row["inclusion_score"],
                        growth_score=row["growth_score"],
                        economy_score=row["economy_score"],
                        community_score=row["community_score"]
                    )
                    session.add(tract)
            
            session.commit()
            print("Database initialized successfully.")
    except Exception as e:
        print(f"Error during initialization: {e}")
def get_db():
    db = sessionmaker(bind=engine)()
    try:
        yield db
    finally:
        db.close()

init_db()