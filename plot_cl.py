# plotting confidence intervals

from matplotlib import pyplot as plt
import numpy as np
import os
import mplhep as hep

from Dumbledraw.Dumbledraw import styles

hep.style.use("CMS")

##############################
# No systematic uncertainties
##############################

##############################
# CL values for equal events
##############################
# tt
# Expected  2.5%: r < 7.4121                                                                                                                                                                                                                          
# Expected 16.0%: r < 10.0232                                                                                                                                                                                                                         
# Expected 50.0%: r < 14.3750                                                                                                                                                                                                                         
# Expected 84.0%: r < 20.8498                                                                                                                                                                                                                         
# Expected 97.5%: r < 29.0660 
# tt_cl_equal_events = [7.4121, 10.0232, 14.3750, 20.8498, 29.0660]

# Observed Limit: r < 13.7075                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 6.9507                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 9.4770                                                                                                                                                                                                                                                   
# Expected 50.0%: r < 13.6875                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 20.0709                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 28.2366 
tt_cl_equal_events = [6.7188, 9.2383, 13.4375, 19.8114, 28.0341]

# mt
# Expected  2.5%: r < 12.1213
# Expected 16.0%: r < 16.5490
# Expected 50.0%: r < 23.687d5
# Expected 84.0%: r < 34.4513
# Expected 97.5%: r < 48.1030
# mt_cl_equal_events = [12.1213, 16.5490, 23.6875, 34.4513, 48.1030]

# Observed Limit: r < 24.3258                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 12.5361                                                                                                                                                                                                                                                  
# Expected 16.0%: r < 17.0443                                                                                                                                                                                                                                                  
# Expected 50.0%: r < 24.3125                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 35.2634                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 49.0084
mt_cl_equal_events = [11.7114, 16.0568, 23.0625, 33.6342, 47.1775]


# et
# Expected  2.5%: r < 17.4624                                                                                                                                                                                                                         
# Expected 16.0%: r < 23.8411
# Expected 50.0%: r < 34.1250
# Expected 84.0%: r < 49.7677
# Expected 97.5%: r < 69.8073
# et_cl_equal_events = [17.4624, 23.8411, 34.1250, 49.7677, 69.8073]

# Observed Limit: r < 31.6935                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 15.8125                                                                                                                                                                                                                                                  
# Expected 16.0%: r < 21.7422                                                                                                                                                                                                                                                  
# Expected 50.0%: r < 31.6250                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 46.7520                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 66.2478
et_cl_equal_events = [15.1250, 20.7969, 30.2500, 44.8399, 63.6246]

# all together
# Expected  2.5%: r < 5.8069
# Expected 16.0%: r < 7.8308
# Expected 50.0%: r < 11.0938
# Expected 84.0%: r < 15.9137
# Expected 97.5%: r < 21.8308
# all_cl_equal_events = [5.8069, 7.8308, 11.0938, 15.9137, 21.8308]

# Observed Limit: r < 10.6363
# Expected  2.5%: r < 5.4946
# Expected 16.0%: r < 7.4706
# Expected 50.0%: r < 10.6562
# Expected 84.0%: r < 15.3711
# Expected 97.5%: r < 21.2927
all_cl_equal_events = [5.2852, 7.1858, 10.2500, 14.8668, 20.6617]


##############################
# CL values for equal weights
##############################
# tt
# Observed Limit: r < 15.2772                                                                                             
# Expected  2.5%: r < 7.8633                                                                                              
# Expected 16.0%: r < 10.6333                                                                                             
# Expected 50.0%: r < 15.2500                                                                                             
# Expected 84.0%: r < 22.1189                                                                                             
# Expected 97.5%: r < 30.9300 
tt_cl_equal_weights = [7.8633, 10.6333, 15.2500, 22.1189, 30.9300]

# mt
# Observed Limit: r < 27.8663                                                                                             
# Expected  2.5%: r < 14.4495                                                                                             
# Expected 16.0%: r < 19.5650                                                                                             
# Expected 50.0%: r < 27.8125                                                                                             
# Expected 84.0%: r < 39.8964                                                                                             
# Expected 97.5%: r < 55.0797 
mt_cl_equal_weights = [14.4495, 19.5650, 27.8125, 39.8964, 55.0797]	

# et
# Observed Limit: r < 45.5357                                                                                             
# Expected  2.5%: r < 23.9941                                                                                             
# Expected 16.0%: r < 32.2269                                                                                             
# Expected 50.0%: r < 45.5000                                                                                             
# Expected 84.0%: r < 64.9061                                                                                             
# Expected 97.5%: r < 88.7208     
et_cl_equal_weights = [23.9941, 32.2269, 45.5000, 64.9061, 88.7208]

# all together
# Observed Limit: r < 12.4679                                                                                             
# Expected  2.5%: r < 6.5430                                                                                              
# Expected 16.0%: r < 8.7769                                                                                              
# Expected 50.0%: r < 12.5000                                                                                             
# Expected 84.0%: r < 17.8812                                                                                             
# Expected 97.5%: r < 24.5648   
all_cl_equal_weights = [6.5430, 8.7769, 12.5000, 17.8812, 24.5648]


##############################
# CL values for custom events
##############################
# tt
# Observed Limit: r < 14.9797                                                                                             
# Expected  2.5%: r < 7.7930                                                                                              
# Expected 16.0%: r < 10.5519                                                                                             
# Expected 50.0%: r < 15.0000                                                                                             
# Expected 84.0%: r < 21.5770                                                                                             
# Expected 97.5%: r < 29.9332 
tt_cl_custom_events = [7.7930, 10.5519, 15.0000, 21.5770, 29.9332]

# mt
# Observed Limit: r < 33.7873                                                                                             
# Expected  2.5%: r < 17.9297                                                                                             
# Expected 16.0%: r < 24.1095                                                                                             
# Expected 50.0%: r < 33.7500                                                                                             
# Expected 84.0%: r < 47.7410                                                                                             
# Expected 97.5%: r < 64.6790  
mt_cl_custom_events = [17.9297, 24.1095, 33.7500, 47.7410, 64.6790]

# et
# Observed Limit: r < 44.6070                                                                                             
# Expected  2.5%: r < 23.2930                                                                                             
# Expected 16.0%: r < 31.5770                                                                                             
# Expected 50.0%: r < 44.5000                                                                                             
# Expected 84.0%: r < 63.4795                                                                                             
# Expected 97.5%: r < 87.3322  
et_cl_custom_events = [23.2930, 31.5770, 44.5000, 63.4795, 87.3322]

# all together
# Observed Limit: r < 12.8801                                                                                             
# Expected  2.5%: r < 6.7896                                                                                              
# Expected 16.0%: r < 9.1191                                                                                              
# Expected 50.0%: r < 12.8750                                                                                             
# Expected 84.0%: r < 18.3150                                                                                             
# Expected 97.5%: r < 25.0704 
all_cl_custom_events = [6.7896, 9.1191, 12.8750, 18.3150, 25.0704]

##############################
# CL values for custom weights
##############################
# tt
# Observed Limit: r < 15.1423                                                                                             
# Expected  2.5%: r < 7.8579                                                                                              
# Expected 16.0%: r < 10.6398                                                                                             
# Expected 50.0%: r < 15.1250                                                                                             
# Expected 84.0%: r < 21.7568                                                                                             
# Expected 97.5%: r < 29.9933 
tt_cl_custom_weights = [7.8579, 10.6398, 15.1250, 21.7568, 29.9933]

# mt
# Observed Limit: r < 32.0128                                                                                             
# Expected  2.5%: r < 17.0000                                                                                             
# Expected 16.0%: r < 22.7422                                                                                             
# Expected 50.0%: r < 32.0000                                                                                             
# Expected 84.0%: r < 45.1380                                                                                             
# Expected 97.5%: r < 61.2371 
mt_cl_custom_weights = [17.0000, 22.7422, 32.0000, 45.1380, 61.2371]

# et
# Observed Limit: r < 44.1264                                                                                             
# Expected  2.5%: r < 23.2690                                                                                             
# Expected 16.0%: r < 31.2530                                                                                             
# Expected 50.0%: r < 44.1250                                                                                             
# Expected 84.0%: r < 62.5928                                                                                             
# Expected 97.5%: r < 85.8020                                                                                             
et_cl_custom_weights = [23.2690, 31.2530, 44.1250, 62.5928, 85.8020]

# all together
# Observed Limit: r < 12.8434                                                                                             
# Expected  2.5%: r < 6.7566                                                                                              
# Expected 16.0%: r < 9.1222                                                                                              
# Expected 50.0%: r < 12.8125                                                                                             
# Expected 84.0%: r < 18.2771                                                                                             
# Expected 97.5%: r < 24.8216  
all_cl_custom_weights = [6.7566, 9.1222, 12.8125, 18.2771, 24.8216]


##############################
# With systematic uncertainties
##############################

##############################
# CL values for equal events with systematics
##############################
# tt
# Observed Limit: r < 14.8705                                                                                                                                                                                                                     
# Expected  2.5%: r < 7.5798                                                                                                                                                                                                                      
# Expected 16.0%: r < 10.2921                                                                                                                                                                                                                     
# Expected 50.0%: r < 14.8125                                                                                                                                                                                                                     
# Expected 84.0%: r < 21.8386                                                                                                                                                                                                                     
# Expected 97.5%: r < 30.8121 
# tt_cl_equal_events_sys = [7.5798, 10.2921, 14.8125, 21.8386, 30.8121]

# Observed Limit: r < 14.1159                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 7.0625                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 9.7109                                                                                                                                                                                                                                                   
# Expected 50.0%: r < 14.1250                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 20.9376                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 29.9670   
tt_cl_equal_events_sys = [7.0625, 9.7109, 14.1250, 20.9376, 29.9670]

# mt
# Observed Limit: r < 24.1344                                                                                             
# Expected  2.5%: r < 12.2510                                                                                             
# Expected 16.0%: r < 16.7037                                                                                             
# Expected 50.0%: r < 24.1250                                                                                             
# Expected 84.0%: r < 35.3761                                                                                             
# Expected 97.5%: r < 50.0654 
# mt_cl_equal_events_sys = [12.2510, 16.7037, 24.1250, 35.3761, 50.0654]

# Observed Limit: r < 24.7613                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 12.6650                                                                                                                                                                                                                                                  
# Expected 16.0%: r < 17.1969                                                                                                                                                                                                                                                  
# Expected 50.0%: r < 24.7500                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 36.0953                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 50.9355 
mt_cl_equal_events_sys = [12.6650, 17.1969, 24.7500, 36.0953, 50.9355]

# et
# Observed Limit: r < 34.8394                                                                                             
# Expected  2.5%: r < 17.7100                                                                                             
# Expected 16.0%: r < 24.1469                                                                                             
# Expected 50.0%: r < 34.8750                                                                                             
# Expected 84.0%: r < 51.1395                                                                                             
# Expected 97.5%: r < 72.8034 
# et_cl_equal_events_sys = [17.7100, 24.1469, 34.8750, 51.1395, 72.8034]

# Observed Limit: r < 32.2548                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 15.9990                                                                                                                                                                                                                                                  
# Expected 16.0%: r < 22.0931                                                                                                                                                                                                                                                  
# Expected 50.0%: r < 32.2500                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 48.0616                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 68.9625 
et_cl_equal_events_sys = [15.9990, 22.0931, 32.2500, 48.0616, 68.9625]

# all together
# Observed Limit: r < 11.3985                                                                                             
# Expected  2.5%: r < 5.9097                                                                                              
# Expected 16.0%: r < 8.0019                                                                                              
# Expected 50.0%: r < 11.3750                                                                                             
# Expected 84.0%: r < 16.4986                                                                                             
# Expected 97.5%: r < 22.9294 
# all_cl_equal_events_sys = [5.9097, 8.0019, 11.3750, 16.4986, 22.9294]

# Observed Limit: r < 10.9182
# Expected  2.5%: r < 5.5809
# Expected 16.0%: r < 7.6195
# Expected 50.0%: r < 10.9062
# Expected 84.0%: r < 15.9056
# Expected 97.5%: r < 22.3102
all_cl_equal_events_sys = [5.5809, 7.6195, 10.9062, 15.9056, 22.3102]

###############################
# CL values for equal weights with systematics
###############################
# tt
# Observed Limit: r < 15.8247                                                                                                                                                                                                                     
# Expected  2.5%: r < 8.0298                                                                                                                                                                                                                      
# Expected 16.0%: r < 10.9483                                                                                                                                                                                                                     
# Expected 50.0%: r < 15.8125                                                                                                                                                                                                                     
# Expected 84.0%: r < 23.1869                                                                                                                                                                                                                     
# Expected 97.5%: r < 32.9122 
tt_cl_equal_weights_sys = [8.0298, 10.9483, 15.8125, 23.1869, 32.9122]

# mt
# Observed Limit: r < 28.4581                                                                                             
# Expected  2.5%: r < 14.6309                                                                                             
# Expected 16.0%: r < 19.8923                                                                                             
# Expected 50.0%: r < 28.3750                                                                                             
# Expected 84.0%: r < 41.1557                                                                                             
# Expected 97.5%: r < 57.5501
mt_cl_equal_weights_sys = [14.6309, 19.8923, 28.3750, 41.1557, 57.5501]

# et
# Observed Limit: r < 46.7070                                                                                             
# Expected  2.5%: r < 24.4707                                                                                             
# Expected 16.0%: r < 32.9995                                                                                             
# Expected 50.0%: r < 46.7500                                                                                             
# Expected 84.0%: r < 67.4346                                                                                             
# Expected 97.5%: r < 93.4133 
et_cl_equal_weights_sys = [24.4707, 32.9995, 46.7500, 67.4346, 93.4133]

# all together
# Observed Limit: r < 12.8461                                                                                             
# Expected  2.5%: r < 6.6387                                                                                              
# Expected 16.0%: r < 9.0260                                                                                              
# Expected 50.0%: r < 12.8750                                                                                             
# Expected 84.0%: r < 18.6229                                                                                             
# Expected 97.5%: r < 25.9200 
all_cl_equal_weights_sys = [6.6387, 9.0260, 12.8750, 18.6229, 25.9200]

###############################
# CL values for custom events with systematics
###############################
# tt
# Observed Limit: r < 15.5450                                                                                                                                                                                                                     
# Expected  2.5%: r < 7.9922                                                                                                                                                                                                                      
# Expected 16.0%: r < 10.8663                                                                                                                                                                                                                     
# Expected 50.0%: r < 15.5000                                                                                                                                                                                                                     
# Expected 84.0%: r < 22.6051                                                                                                                                                                                                                     
# Expected 97.5%: r < 31.7074
tt_cl_custom_events_sys = [7.9922, 10.8663, 15.5000, 22.6051, 31.7074]

# mt
# Observed Limit: r < 34.7087                                                                                             
# Expected  2.5%: r < 18.2593                                                                                             
# Expected 16.0%: r < 24.6521                                                                                             
# Expected 50.0%: r < 34.6250                                                                                             
# Expected 84.0%: r < 49.5308                                                                                             
# Expected 97.5%: r < 68.0445 
mt_cl_custom_events_sys = [18.2593, 24.6521, 34.6250, 49.5308, 68.0445]

# et
# Observed Limit: r < 45.6882                                                                                             
# Expected  2.5%: r < 23.9473                                                                                             
# Expected 16.0%: r < 32.1233                                                                                             
# Expected 50.0%: r < 45.7500                                                                                             
# Expected 84.0%: r < 65.9921                                                                                             
# Expected 97.5%: r < 91.7008 
et_cl_custom_events_sys = [23.9473, 32.1233, 45.7500, 65.9921, 91.7008]

# all together
# Observed Limit: r < 13.2858                                                                                             
# Expected  2.5%: r < 6.9163                                                                                              
# Expected 16.0%: r < 9.3648                                                                                              
# Expected 50.0%: r < 13.3125                                                                                             
# Expected 84.0%: r < 19.0965                                                                                             
# Expected 97.5%: r < 26.5311   
all_cl_custom_events_sys = [6.9163, 9.3648, 13.3125, 19.0965, 26.5311]

###############################
# CL values for custom weights with systematics
###############################
# tt
# Observed Limit: r < 15.7308                                                                                             
# Expected  2.5%: r < 8.0889                                                                                              
# Expected 16.0%: r < 10.9977                                                                                             
# Expected 50.0%: r < 15.6875                                                                                             
# Expected 84.0%: r < 22.8786                                                                                             
# Expected 97.5%: r < 32.0909 
tt_cl_custom_weights_sys = [8.0889, 10.9977, 15.6875, 22.8786, 32.0909]

# mt
# Observed Limit: r < 32.8598                                                                                             
# Expected  2.5%: r < 17.3364                                                                                             
# Expected 16.0%: r < 23.2848                                                                                             
# Expected 50.0%: r < 32.8750                                                                                             
# Expected 84.0%: r < 46.8964                                                                                             
# Expected 97.5%: r < 64.5179 
mt_cl_custom_weights_sys = [17.3364, 23.2848, 32.8750, 46.8964, 64.5179]

# et
# Observed Limit: r < 45.1930                                                                                             
# Expected  2.5%: r < 23.6855                                                                                             
# Expected 16.0%: r < 31.9407                                                                                             
# Expected 50.0%: r < 45.2500                                                                                             
# Expected 84.0%: r < 64.9102                                                                                             
# Expected 97.5%: r < 90.1808  
et_cl_custom_weights_sys = [23.6855, 31.9407, 45.2500, 64.9102, 90.1808]

# all together
# Observed Limit: r < 13.2844                                                                                             
# Expected  2.5%: r < 6.9683                                                                                              
# Expected 16.0%: r < 9.3474                                                                                              
# Expected 50.0%: r < 13.3125                                                                                             
# Expected 84.0%: r < 19.0965                                                                                             
# Expected 97.5%: r < 26.3640  
all_cl_custom_weights_sys = [6.9683, 9.3474, 13.3125, 19.0965, 26.3640]

###############################
# equal events scaled to lumi 137.66fb-1, no systematics
###############################
# tt
# Observed Limit: r < 10.0901
# Expected  2.5%: r < 5.3229
# Expected 16.0%: r < 7.1492
# Expected 50.0%: r < 10.0938
# Expected 84.0%: r < 14.3586
# Expected 97.5%: r < 19.6547
tt_cl_equal_events_scaled_137 = [5.3229, 7.1492, 10.0938, 14.3586, 19.6547]

# mt
# Observed Limit: r < 16.1990
# Expected  2.5%: r < 8.4731
# Expected 16.0%: r < 11.4263
# Expected 50.0%: r < 16.1875
# Expected 84.0%: r < 23.0916
# Expected 97.5%: r < 31.6662
mt_cl_equal_events_scaled_137 = [8.4731, 11.4263, 16.1875, 23.0916, 31.6662]

# et
# Observed Limit: r < 19.9617
# Expected  2.5%: r < 10.1245
# Expected 16.0%: r < 13.8044
# Expected 50.0%: r < 19.9375
# Expected 84.0%: r < 29.2357
# Expected 97.5%: r < 41.1301
et_cl_equal_events_scaled_137 = [10.1245, 13.8044, 19.9375, 29.2357, 41.1301]

# all together
# Observed Limit: r < 7.6213
# Expected  2.5%: r < 4.0342
# Expected 16.0%: r < 5.4246
# Expected 50.0%: r < 7.5938
# Expected 84.0%: r < 10.7720
# Expected 97.5%: r < 14.6700
all_cl_equal_events_scaled_137 = [4.0342, 5.4246, 7.5938, 10.7720, 14.6700]

###############################
# equal events scaled to lumi 137.66fb-1, with systematics
###############################
# tt
# Observed Limit: r < 10.4303                                                                                                                                                                                                                     
# Expected  2.5%: r < 5.4634                                                                                                                                                                                                                      
# Expected 16.0%: r < 7.3287                                                                                                                                                                                                                      
# Expected 50.0%: r < 10.4375                                                                                                                                                                                                                     
# Expected 84.0%: r < 15.0140                                                                                                                                                                                                                     
# Expected 97.5%: r < 20.8285   
# tt_cl_equal_events_scaled_137_sys = [5.4634, 7.3287, 10.4375, 15.0140, 20.8285]

# Observed Limit: r < 9.1653                                                                                                                                                                                                                                                   
# Expected  2.5%: r < 4.6497                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 6.3396                                                                                                                                                                                                                                                   
# Expected 50.0%: r < 9.1562                                                                                                                                                                                                                                                   
# Expected 84.0%: r < 13.4994                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 19.1023  
tt_cl_equal_events_scaled_137_sys = [4.6497, 6.3396, 9.1562, 13.4994, 19.1023]

# mt
# Observed Limit: r < 16.4207
# Expected  2.5%: r < 8.6040
# Expected 16.0%: r < 11.6028
# Expected 50.0%: r < 16.4375
# Expected 84.0%: r < 23.7103
# Expected 97.5%: r < 32.8445
# mt_cl_equal_events_scaled_137_sys = [8.6040, 11.6028, 16.4375, 23.7103, 32.8445]

# Observed Limit: r < 16.8851                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 8.8657                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 11.9557                                                                                                                                                                                                                                                  
# Expected 50.0%: r < 16.9375                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 24.2965                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 33.7555 
mt_cl_equal_events_scaled_137_sys = [8.8657, 11.9557, 16.9375, 24.2965, 33.7555]

# et
# Observed Limit: r < 20.3069
# Expected  2.5%: r < 10.1562
# Expected 16.0%: r < 13.9648
# Expected 50.0%: r < 20.3125
# Expected 84.0%: r < 29.9475
# Expected 97.5%: r < 42.7500
# et_cl_equal_events_scaled_137_sys = [10.1562, 13.9648, 20.3125, 29.9475, 42.7500]

# Observed Limit: r < 20.5151                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 10.4419                                                                                                                                                                                                                                                  
# Expected 16.0%: r < 14.2371                                                                                                                                                                                                                                                  
# Expected 50.0%: r < 20.5625                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 30.1522                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 42.7988 
et_cl_equal_events_scaled_137_sys = [10.4419, 14.2371, 20.5625, 30.1522, 42.7988]

# all together
# Observed Limit: r < 7.7949
# Expected  2.5%: r < 4.1199
# Expected 16.0%: r < 5.5335
# Expected 50.0%: r < 7.8125
# Expected 84.0%: r < 11.1446
# Expected 97.5%: r < 15.3322
# all_cl_equal_events_scaled_137_sys = [4.1199, 5.5335, 7.8125, 11.1446, 15.3322]

# Observed Limit: r < 7.2301
# Expected  2.5%: r < 3.7222
# Expected 16.0%: r < 5.0607
# Expected 50.0%: r < 7.2188
# Expected 84.0%: r < 10.4702
# Expected 97.5%: r < 14.5513
all_cl_equal_events_scaled_137_sys = [3.7222, 5.0607, 7.2188, 10.4702, 14.5513]

###############################
# equal events scaled to lumi 430fb-1, no systematics
###############################
# tt
# Observed Limit: r < 6.4677                                                                                                                                                                                                                      
# Expected  2.5%: r < 3.4113                                                                                                                                                                                                                      
# Expected 16.0%: r < 4.5817
# Expected 50.0%: r < 6.4688
# Expected 84.0%: r < 9.2277
# Expected 97.5%: r < 12.5319
tt_cl_equal_events_scaled_430 = [3.4113, 4.5817, 6.4688, 9.2277, 12.5319]

# mt
# Observed Limit: r < 11.1639
# Expected  2.5%: r < 6.0139
# Expected 16.0%: r < 7.9825
# Expected 50.0%: r < 11.1562
# Expected 84.0%: r < 15.6476
# Expected 97.5%: r < 21.0022
mt_cl_equal_events_scaled_430 = [6.0139, 7.9825, 11.1562, 15.6476, 21.0022]

# et
# Observed Limit: r < 12.1820
# Expected  2.5%: r < 6.4270
# Expected 16.0%: r < 8.6322
# Expected 50.0%: r < 12.1875
# Expected 84.0%: r < 17.3855
# Expected 97.5%: r < 23.9182
et_cl_equal_events_scaled_430 = [6.4270, 8.6322, 12.1875, 17.3855, 23.9182]

# all together
# Observed Limit: r < 4.9924
# Expected  2.5%: r < 2.6562
# Expected 16.0%: r < 3.5718
# Expected 50.0%: r < 5.0000
# Expected 84.0%: r < 7.0528
# Expected 97.5%: r < 9.5046
all_cl_equal_events_scaled_430 = [2.6562, 3.5718, 5.0000, 7.0528, 9.5046]

###############################
# equal events scaled to lumi 430fb-1, with systematics
###############################
# tt
# Observed Limit: r < 6.6722                                                                                                                                                                                                                      
# Expected  2.5%: r < 3.4841                                                                                                                                                                                                                      
# Expected 16.0%: r < 4.6985                                                                                                                                                                                                                      
# Expected 50.0%: r < 6.6562                                                                                                                                                                                                                      
# Expected 84.0%: r < 9.6013
# Expected 97.5%: r < 13.3002
tt_cl_equal_events_scaled_430_sys = [3.4841, 4.6985, 6.6562, 9.6013, 13.3002]

# mt
# Observed Limit: r < 11.3200
# Expected  2.5%: r < 6.0264
# Expected 16.0%: r < 8.1035
# Expected 50.0%: r < 11.3438
# Expected 84.0%: r < 16.0463
# Expected 97.5%: r < 21.8835
mt_cl_equal_events_scaled_430_sys = [6.0264, 8.1035, 11.3438, 16.0463, 21.8835]

# et
# Observed Limit: r < 12.3787
# Expected  2.5%: r < 6.4775
# Expected 16.0%: r < 8.7352
# Expected 50.0%: r < 12.3750
# Expected 84.0%: r < 17.8503
# Expected 97.5%: r < 24.8043
et_cl_equal_events_scaled_430_sys = [6.4775, 8.7352, 12.3750, 17.8503, 24.8043]

# all together
# Observed Limit: r < 5.1137
# Expected  2.5%: r < 2.7144
# Expected 16.0%: r < 3.6312
# Expected 50.0%: r < 5.1094
# Expected 84.0%: r < 7.2682
# Expected 97.5%: r < 9.9490
all_cl_equal_events_scaled_430_sys = [2.7144, 3.6312, 5.1094, 7.2682, 9.9490]

###############################
# with custom bins
# equal events scaled to lumi 500fb-1, with systematics
###############################

# tt
# Observed Limit: r < 5.8553                                                                                                                                                                                                                                                   
# Expected  2.5%: r < 3.0670                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 4.1360                                                                                                                                                                                                                                                   
# Expected 50.0%: r < 5.8594                                                                                                                                                                                                                                                   
# Expected 84.0%: r < 8.4051                                                                                                                                                                                                                                                   
# Expected 97.5%: r < 11.6406   
tt_cl_equal_events_scaled_500_sys = [3.0670, 4.1360, 5.8594, 8.4051, 11.6406]

# mt
# Observed Limit: r < 11.2053                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 6.0038                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 8.0409                                                                                                                                                                                                                                                   
# Expected 50.0%: r < 11.2188                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 15.8247                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 21.6118 
mt_cl_equal_events_scaled_500_sys = [6.0038, 8.0409, 11.2188, 15.8247, 21.6118]

# et
# Observed Limit: r < 12.0268                                                                                                                                                                                                                                                  
# Expected  2.5%: r < 6.2976                                                                                                                                                                                                                                                   
# Expected 16.0%: r < 8.4925                                                                                                                                                                                                                                                   
# Expected 50.0%: r < 12.0312                                                                                                                                                                                                                                                  
# Expected 84.0%: r < 17.2586                                                                                                                                                                                                                                                  
# Expected 97.5%: r < 23.8266  
et_cl_equal_events_scaled_500_sys = [6.2976, 8.4925, 12.0312, 17.2586, 23.8266]

# all together
# Observed Limit: r < 4.6988
# Expected  2.5%: r < 2.4902
# Expected 16.0%: r < 3.3314
# Expected 50.0%: r < 4.6875
# Expected 84.0%: r < 6.6867
# Expected 97.5%: r < 9.1402
all_cl_equal_events_scaled_500_sys = [2.4902, 3.3314, 4.6875, 6.6867, 9.1402]

def build_interval_dict(training_type: str):
    raw = {}

    if training_type == "equal_events":
        raw = {
            "et": et_cl_equal_events,
            "mt": mt_cl_equal_events,
            "tt": tt_cl_equal_events,
            "all": all_cl_equal_events,
        }
    elif training_type == "equal_weights":
        raw = {
            "et": et_cl_equal_weights,
            "mt": mt_cl_equal_weights,
            "tt": tt_cl_equal_weights,
            "all": all_cl_equal_weights,
		}
    elif training_type == "custom_events":
        raw = {
			"et": et_cl_custom_events,
			"mt": mt_cl_custom_events,
			"tt": tt_cl_custom_events,
			"all": all_cl_custom_events,
		}
    elif training_type == "custom_weights":
        raw = {
			"et": et_cl_custom_weights,
			"mt": mt_cl_custom_weights,
			"tt": tt_cl_custom_weights,
			"all": all_cl_custom_weights,
		}
    elif training_type == "equal_events_sys":
        raw = {
			"et": et_cl_equal_events_sys,
			"mt": mt_cl_equal_events_sys,
			"tt": tt_cl_equal_events_sys,
			"all": all_cl_equal_events_sys,
		}
    elif training_type == "equal_weights_sys":
        raw = {
			"et": et_cl_equal_weights_sys,
			"mt": mt_cl_equal_weights_sys,
			"tt": tt_cl_equal_weights_sys,
			"all": all_cl_equal_weights_sys,
		}
    elif training_type == "custom_events_sys":
        raw = {
			"et": et_cl_custom_events_sys,
			"mt": mt_cl_custom_events_sys,
			"tt": tt_cl_custom_events_sys,
			"all": all_cl_custom_events_sys,
		}
    elif training_type == "custom_weights_sys":
        raw = {
			"et": et_cl_custom_weights_sys,
			"mt": mt_cl_custom_weights_sys,
			"tt": tt_cl_custom_weights_sys,	
			"all": all_cl_custom_weights_sys,
		}
    elif training_type == "equal_events_scaled_137":
        raw = {
			"et": et_cl_equal_events_scaled_137,
			"mt": mt_cl_equal_events_scaled_137,
			"tt": tt_cl_equal_events_scaled_137,
			"all": all_cl_equal_events_scaled_137,
		}
    elif training_type == "equal_events_scaled_137_sys":
        raw = {
			"et": et_cl_equal_events_scaled_137_sys,
			"mt": mt_cl_equal_events_scaled_137_sys,
			"tt": tt_cl_equal_events_scaled_137_sys,
			"all": all_cl_equal_events_scaled_137_sys,
		}
    elif training_type == "equal_events_scaled_430":
        raw = {
			"et": et_cl_equal_events_scaled_430,
			"mt": mt_cl_equal_events_scaled_430,
			"tt": tt_cl_equal_events_scaled_430,
			"all": all_cl_equal_events_scaled_430,
		}
    elif training_type == "equal_events_scaled_430_sys":
        raw = {
			"et": et_cl_equal_events_scaled_430_sys,
			"mt": mt_cl_equal_events_scaled_430_sys,
			"tt": tt_cl_equal_events_scaled_430_sys,
			"all": all_cl_equal_events_scaled_430_sys,
		}
    elif training_type == "equal_events_scaled_500_sys":
        raw = {
			"et": et_cl_equal_events_scaled_500_sys,
			"mt": mt_cl_equal_events_scaled_500_sys,
			"tt": tt_cl_equal_events_scaled_500_sys,
			"all": all_cl_equal_events_scaled_500_sys,
		}

    if not raw:
        raise ValueError(f"Unknown training_type: {training_type}")

    out = {}
    for k, v in raw.items():
        p2, p16, p50, p84, p97 = v
        out[k] = {
            "cl": v,
            "median": p50,
            "err68_low": p50 - p16,
            "err68_high": p84 - p50,
            "err95_low": p50 - p2,
            "err95_high": p97 - p50,
        }
    return out

label_map = {
"all": "all",
"et": r"$e\tau_h$",
"mt": r"$\mu\tau_h$",
"tt": r"$\tau_h\tau_h$",
}


def plot_intervals(outdir: str = "plots", training_type: str = "equal_events", ):
	data = build_interval_dict(training_type)
	order = ["all", "et", "mt", "tt"]  # Reihenfolge von unten nach oben

	systematics = training_type.endswith("sys")

	y_positions = np.arange(len(order))

	# Farben
	color_95 = "#b6e3a1"  # hellgrün
	color_68 = "#228B22"  # dunkelgrün

	fig, ax = plt.subplots(figsize=(11, 7))

	bar_width = 0.3

	# 95% Bänder (hellgrün)
	for y, label in zip(y_positions, order):
		d = data[label]
		left = d["median"] - d["err95_low"]
		right = d["median"] + d["err95_high"]
		ax.fill_betweenx([y - bar_width, y + bar_width], left, right, color=color_95, zorder=1)

	# 68% Bänder (dunkelgrün)
	for y, label in zip(y_positions, order):
		d = data[label]
		left = d["median"] - d["err68_low"]
		right = d["median"] + d["err68_high"]
		ax.fill_betweenx([y - bar_width, y + bar_width], left, right, color=color_68, zorder=2)

	# Median Marker
	# Zeichne Median als gestrichelte vertikale Linie über das 95%-Band
	for y, label in zip(y_positions, order):
		d = data[label]
		m = d["median"]
		ax.plot([m, m], [y - bar_width, y + bar_width], color="black", linestyle="--", linewidth=1.4, zorder=4)

		ax.text(
            m,
            y - bar_width - 0.08,           # leicht unterhalb des unteren Linienendes
            f"{m:.1f}",
            ha="center",
            va="top",
            fontsize=20,
            color="black",
            zorder=5,
        )

	# Referenzlinie r=1 nur falls im Bereich sinnvoll
	xmin = 0.0
	xmax = max(d["median"] + d["err95_high"] for d in data.values()) * 1.05
	if xmax < 1.0:
		xmax = 1.2
	# if 0.0 <= 1.0 <= xmax:
	#     ax.axvline(1.0, color="red", linestyle="--", linewidth=1, label="r=1")

	ax.set_yticks(y_positions)
	ax.set_yticklabels([label_map[l] for l in order])
	# Keine sichtbaren Tick-Markierungen zwischen den Labels
	ax.tick_params(axis="y", which="both", length=0)
	# Sicherstellen, dass keine Minor-Ticks erscheinen
	from matplotlib.ticker import NullLocator
	ax.yaxis.set_minor_locator(NullLocator())
	ax.set_xlabel(r"$95\%$ CL upper limit on $\sigma(pp \to HH)\,/\,\sigma_{\mathrm{theory}}$")
	ax.set_ylim(-0.6, len(order) - 0.4)
	ax.set_xlim(xmin, xmax)
	ax.grid(axis="x", alpha=0.3, linestyle=":")
	# Titel
	scaling_note = ""
	if "scaled_137" in training_type:
		scaling_note = "- full Run 2"
	elif "scaled_430" in training_type:
		scaling_note = "- Run 2 and 3"
	# if systematics:
	# 	ax.set_title(f"CLs {scaling_note} - with systematic uncertainties")
	# else:
	# 	ax.set_title(f"CLs {scaling_note} - only statistical uncertainties")

	# Legende
	from matplotlib.patches import Patch
	from matplotlib.lines import Line2D

	legend_elements = [
		Patch(facecolor=color_68, label="68% expected"),
		Patch(facecolor=color_95, label="95% expected"),
		Line2D([0, 1], [0, 1], color="black", linestyle="--", label="Median expected"),
	]
	ax.legend(handles=legend_elements, loc="upper right")

	hep.cms.label(ax=ax, label="Private Work", loc=0, data=True, lumi=138 if "scaled_137" in training_type else 430 if "scaled_430" in training_type else 500 if "scaled_500" in training_type else 59.8)

	filename = f"cl_{training_type}"

	os.makedirs(outdir, exist_ok=True)
	pdf_path = os.path.join(outdir, f"{filename}.pdf")
	png_path = os.path.join(outdir, f"{filename}.png")
	fig.tight_layout()
	fig.savefig(pdf_path)
	fig.savefig(png_path, dpi=150)
	print(f"[INFO] Saved plot to {pdf_path} and {png_path}")


if __name__ == "__main__":
	output_dir = "plots/confidence_intervals"
     
	training_type = "equal_events"
	plot_intervals(outdir=output_dir, training_type=training_type)

	# training_type = "equal_weights"
	# plot_intervals(outdir=output_dir, training_type=training_type)
     
	# training_type = "custom_events"
	# plot_intervals(outdir=output_dir, training_type=training_type)

	# training_type = "custom_weights"
	# plot_intervals(outdir=output_dir, training_type=training_type)
     
	# training_type = "equal_events_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)
     
	# training_type = "equal_weights_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)

	# training_type = "custom_events_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)

	# training_type = "custom_weights_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)

	# training_type = "equal_events_scaled_137"
	# plot_intervals(outdir=output_dir, training_type=training_type)
      
	# training_type = "equal_events_scaled_137_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)
      
	# training_type = "equal_events_scaled_430"
	# plot_intervals(outdir=output_dir, training_type=training_type)

	# training_type = "equal_events_scaled_430_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)
     
	# training_type = "equal_events_scaled_500_sys"
	# plot_intervals(outdir=output_dir, training_type=training_type)
