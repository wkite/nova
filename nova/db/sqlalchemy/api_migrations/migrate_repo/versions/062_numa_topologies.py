#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import MetaData
from sqlalchemy import Table


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    numa_topologies = Table('numa_topologies', meta,
                            Column('id', Integer, primary_key=True, nullable=False),
                            Column('uuid', String(36), nullable=False),
                            Column('nova_numa_topology', Text, nullable=True),
                            Column('zun_numa_topology', Text, nullable=True),
                            Column('created_at', DateTime),
                            Column('updated_at', DateTime),
                            mysql_engine='InnoDB',
                            mysql_charset='latin1'
                            )

    numa_topologies.create(checkfirst=True)
