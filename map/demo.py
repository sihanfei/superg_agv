import numpy as np

if __name__ == "__main__":
  file_dir = "../data/GPS_info/"
  filename = file_dir + "map_point_data.csv"
  point_data = np.loadtxt(filename, delimiter=',')
  longi = point_data[:,0]
  lanti = point_data[:,1]
  longi_uni, index = np.unique(longi, return_index=True)
  lanti_uni = lanti[index]
  unique_data = tuple(zip(longi_uni, lanti_uni))
  print("longi={}, lanti={}".format(len(point_data), len(unique_data)))
  filename = file_dir + "rmdup_map_point_data.csv"
  np.savetxt(filename, unique_data, fmt='%f', delimiter=',', newline='\n')