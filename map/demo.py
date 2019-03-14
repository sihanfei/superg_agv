import numpy as np

dt = np.dtype([
  ('name', np.unicode_, 16), 
  ('grades', np.float64, (2,))
  ])
x = np.array([('Sarah', (8.0, 7.0))], dtype=dt)
print(x)

demo_type = np.dtype([
  ('point', np.float16, (2,)),
  ('width', np.float16, (2,))
  ])
print(demo_type['point'])
demo_list = []
demo_data = np.array(
  [((1.0, 2.0),
    (1.5, 1.5))], dtype = demo_type)
demo_list.append(demo_data)
print(demo_list)
