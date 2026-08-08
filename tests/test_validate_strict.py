import unittest

from athena_mcp.collective_v2_protocol import COLLECTIVE_V2_TOOLS
from athena_mcp.validate import validate


class StrictValidatorTests(unittest.TestCase):
    def test_const_enum_oneof_unique_and_pattern(self):
        with self.assertRaises(ValueError): validate({'const':True},False)
        with self.assertRaises(ValueError): validate({'enum':['A','B']},'C')
        validate({'oneOf':[{'type':'string'},{'type':'number'}]},'x')
        with self.assertRaises(ValueError): validate({'oneOf':[{},{}]},'x')
        with self.assertRaises(ValueError): validate({'type':'array','uniqueItems':True},['x','x'])
        with self.assertRaises(ValueError): validate({'type':'string','pattern':'^AOR\\.'},'COLLECTIVE.1')

    def test_collective_topology_schema_remains_compatible(self):
        tool={row['name']:row for row in COLLECTIVE_V2_TOOLS}['athena_topology_apply']
        validate(tool['inputSchema'],{
            'topology_id':'T1','expected_version':0,'operation':'INIT','payload':{},'actor':'A'
        })
        with self.assertRaises(ValueError):
            validate(tool['inputSchema'],{
                'topology_id':'T1','expected_version':-1,'operation':'INIT','payload':{}
            })

    def test_collective_pheromone_union_types_remain_compatible(self):
        tool={row['name']:row for row in COLLECTIVE_V2_TOOLS}['athena_pheromone_reinforce']
        validate(tool['inputSchema'],{'route_key':'R','observations':{},'age':None})
        validate(tool['inputSchema'],{'route_key':'R','observations':{},'age':3})


if __name__=='__main__':unittest.main()
