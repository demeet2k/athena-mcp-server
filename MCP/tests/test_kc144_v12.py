import json,pathlib,sys,unittest
MCP=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(MCP))
from kc144_meta_v12 import *
from kc144_navigation_v12 import register_kc144_v12
class M:
 def __init__(self):self.tools={}
 def tool(self):
  def d(f):self.tools[f.__name__]=f;return f
  return d
class T(unittest.TestCase):
 def test_maps(self):self.assertEqual(len(MAPS),54)
 def test_grid(self):self.assertEqual(len({station(g)['grid'] for g in range(1,145)}),144)
 def test_d4(self):
  for g in range(1,145):self.assertEqual(transform(transform(g,'grid-rotate-90')['output_gid'],'grid-rotate-270')['output_gid'],g)
 def test_kc27(self):self.assertEqual(transform(transform(106,'kc27-translate',dx=1,dy=2,dz=1)['output_gid'],'kc27-translate',dx=-1,dy=-2,dz=-1)['output_gid'],106)
 def test_seed(self):
  s=compress_seed(list(range(1,145)));self.assertEqual(reconstruct_seed(s)['gids'],list(range(1,145)))
 def test_route(self):self.assertEqual(route('H06','M12')['status'],'ROUTE_FOUND')
 def test_parallel(self):self.assertEqual(parallel_wave('quaternion proof return',4)['receipt'],parallel_wave('quaternion proof return',4)['receipt'])
 def test_register(self):
  m=M();register_kc144_v12(m);self.assertEqual(len(m.tools),14);self.assertEqual(json.loads(m.tools['kc144_validate']())['status'],'PASS')
 def test_validate(self):self.assertEqual(validate()['status'],'PASS')
if __name__=='__main__':unittest.main()
