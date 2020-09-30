from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import datetime
import logging
import contextlib
from sqlalchemy import engine
from sqlalchemy.orm.session import sessionmaker
from sqlite3 import OperationalError

engine = create_engine('sqlite:///Database/Layer2.db')
Base = declarative_base()

class Vlans(Base):
    """"""


    __tablename__ = "vlans"

    vlan = Column(String, primary_key=True)
    vlan_name = Column(String)
    vlan_description = Column(String)

Base.metadata.create_all(engine)


class DbOps():


    def __init__(self):

        self._session = None
        self.create_session()


    def create_session(self):
        """Create session to DB"""

        Session = sessionmaker(bind=engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        self._session = Session()


    def db_vlan_insert(self, vlan_id, vl_name, vl_description) -> None:
        """Inserts new DB entry"""

        insert_vlans = Vlans(vlan=vlan_id, vlan_name=vl_name, vlan_description=vl_description)
        self._session.add(insert_vlans)
        self._session.commit()


    def db_vlan_name_update(self, vl_id, vl_name) -> None:
        """Updates DB vlan name entry"""

        vl_id = str(vl_id)
        query_vlan = self._session.query(Vlans).filter_by(vlan=vl_id).first()
        query_vlan.vlan_name = str(vl_name)
        self._session.commit()


    def db_desc_vlan_update(self, vl_id, vl_description) -> None:
        """Updates vlan description in vlan entry"""

        vl_id = str(vl_id)
        query_vlan = self._session.query(Vlans).filter_by(vlan=vl_id).first()
        query_vlan.vlan_description = vl_description
        self._session.commit()


    def db_delete_vlan(self, vl_id) -> None:
        """Deletes vlan entry"""

        vl_id = str(vl_id)
        query_vlan = self._session.query(Vlans).filter_by(vlan=vl_id).first()
        self._session.delete(query_vlan)
        self._session.commit()


    def db_delete_name(self, name) -> None:
        """Delete vlan entry by name"""

        query_vlan = self._session.query(Vlans).filter_by(vlan_name=name).first()
        self._session.delete(query_vlan)
        self._session.commit()


    @property
    def session(self):
        return self._session

