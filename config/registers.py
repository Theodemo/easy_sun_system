import minimalmodbus
import time


registersMaps = {
# Part 1.1 : Charger Control Message
  # Key : [  jsonName            regType   DisplayName ",                                  multCoef    Link   Unit  Instructions Remarks  Observations
  10001 : [ "ChargrMachineType",   "RO",  "The type of machine",                               1,         0,   "",      "p",     "" ],    # PC1600  
  10002 : [ "ChargrSerialNum",     "WR",  "Charger Serial number",                             1,     10003,   "",      "?",     "" ],
  10003 : [ "ChargrSerialNum2",    "WR",  "Charger Serial number Low",                         1,    -10002,   "",      "?",     "" ],
  10004 : [ "ChargrHardVersion",   "RO",  "Charger Hardware version",                          1,         0,   "ver",   "",      "" ],    # format : 1.0.00 
  10005 : [ "ChargrSoftVersion",   "RO",  "Charger Software version",                          1,         0,   "ver",   "",      "" ],    # format : 1.0.00     
  10006 : [ "PvVCalibCoef",        "WR",  "PV voltage calibration coefficient",                1,         0,   "",      "mn",    "" ],
  10007 : [ "ChargrBatVCalibCoef", "WR",  "Charger Battery voltage calibration coefficient",   1,         0,   "",      "mn",    "" ],
  10008 : [ "ChargrCurACalibCoef", "WR",  "Charger current calibration coefficient",           1,         0,   "",      "mn",    "" ],
  10103 : [ "FloatV",              "WR",  "Float voltage",                                     0.1,       0,   "V",     "p",     "480~584(48.0-58.4)V the default value is 54.0V" ],
  10104 : [ "AbsorpV",             "WR",  "Absorption voltage",                                0.1,       0,   "V",     "p",     "480~584(48.0-58.4)V the default value is 56.4V" ],
  10105 : [ "ChargrBatLowV",       "WR",  "Charger Battery low voltage",                       0.1,       0,   "V",     "p",     "340~440(34.0-44.0)V the default value is 34.0V" ],
  10107 : [ "ChargrBatHighV",      "WR",  "Charger Battery High voltage",                      0.1,       0,   "V",     "p",     "580~600(58.0-60.0)V the default value is 60.0V" ],
  10108 : [ "MaxChargrA",          "WR",  "Max charger current",                               0.1,       0,   "A",     "p",     "0.1A effective range: (0-80.0)A" ],
  10110 : [ "BatType",             "WR",  "Battery type",                                      1,         0,   "map",   {            
              0 : [ "no choose",              "" ],
              1 : [ "Use defined battery",    "" ],
              2 : [ "Li - lithium battery",   "" ],
              3 : [ "LEA - Sealed lead battery",    "" ],
              4 : [ "AGM battery (default)",  "" ],
              5 : [ "GEL battery",            "" ],
              6 : [ "FLD - Flooded battery",  "" ]
              },                                                                                                                 "the default value is 0;  effective range: 0,6" ],
  10111 : [ "BatAH",               "WR",  "Battery AH",                                        1,         0,   "AH",    "p",     "effective range: (0-900)AH;    the default value is 100AH" ],
  10112 : [ "RemoveAccData",       "WR",  "Remove the accumulated data",                       1,         0,   "",      "",      "0: No remove the accumulated data    1: Remove the accumulated data        the default value is 0; effective range: 0,1" ],

# Part 1.2 : Charger Display Message
  # Key : [  jsonName            regType   DisplayName ",                                  multCoef    Link   Unit  Instructions Remarks  Observations
  15201 : [ "ChargrWorkState",     "RO",  "Charger workstate",                                 1,         0,   "map",   {
              0 : [ "Initialization mode",    "" ],
              1 : [ "Selftest mode",          "" ],
              2 : [ "Work mode",              "" ],
              3 : [ "Stop mode",              "" ]
              },                                                                                                                 "" ],
  15202 : [ "MpptState",           "RO",  "Mppt state",                                        1,         0,   "map",   {
              0 : [ "Stop",                   "" ],
              1 : [ "MPPT",                   "" ],
              2 : [ "Current limiting",       "" ]
              },                                                                                                                 "" ],
  15203 : [ "ChargingState",       "RO",  "Charging state",                                    1,         0,   "map",   {
              0 : [ "Stop",                   "" ],
              1 : [ "Absorb charge",          "" ],
              2 : [ "Float charge",           "" ]
              },                                                                                                                 "" ],
  15205 : [ "PvV",                 "RO",  "PV voltage",                                        0.1,       0,   "V",     "p",     "0.1V  (0.0-150.0)V" ],
  15206 : [ "ChargrBatV",          "RO",  "Battery voltage",                                   0.1,       0,   "V",     "p",     "0.1V  (0.0-80.0)V" ],
  15207 : [ "ChargrA",             "RO",  "Charger current",                                   0.1,       0,   "A",     "p",     "0.1A  (0.0-90.0)A" ],
  15208 : [ "ChargrW",             "RO",  "Charger power",                                     1,         0,   "W",     "p",     "1W  (0-5000)W" ],
  15209 : [ "RadiatorT",           "RO",  "Radiator temperature",                              1,         0,   "°C",    "p",     "1℃  (-40-150)℃" ],
  15210 : [ "ExternalT",           "RO",  "External temperature",                              1,         0,   "°C",    "p",     "1℃  (-40-150)℃" ],
  15211 : [ "BatRelay",            "RO",  "Battery Relay",                                     1,         0,   "map",   {
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],    # 
  15212 : [ "PvRelay",             "RO",  "PV Relay",                                          1,         0,   "map",   {
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  15213 : [ "ErrMsg",              "RO",  "Error message",                                     1,         0,   "bit",   {
               0 : "Hardware protection",
               1 : "Over current",
               2 : "Current sensor error",
               3 : "Over temperature",
               4 : "PV voltage is too high",
               6 : "Battery voltage is too high",
               7 : "Battery voltage is too Low",
               8 : "Current is uncontrollable",
               9 : "Parameter error",
              },                                                                                                                 "" ],    # Refer to frame Charger Error message 1   
  15214 : [ "WarnMsg",             "RO",  "Warning message",                                   1,         0,   "bit",   {
               0 : "Fan Error",
              },                                                                                                                 "" ],    # Refer to frame Charger Warning message 1     
  15215 : [ "ChargrBatVGrade",     "RO",  "Battery Voltage Grade",                             1,         0,   "V",     "p",     "" ],    # 1V  
  15216 : [ "RatedA",              "RO",  "Rated Current",                                     0.1,       0,   "A",     "p",     "" ],    # 0.1A    
  15217 : [ "AccPvWh",             "RO",  "Accumulated PV power",                        1000000,     15218,   "Wh",    "p",     "" ],    # 1000KWH  
  15218 : [ "AccPvWh2",            "RO",  "Accumulated PV power low",                        100,    -15217,   "Wh",    "p",     "" ],    # 0.1KWH   
  15219 : [ "AccDay",              "RO",  "Accumulated day",                                   1,     15220,   "day",   "p",     "" ],    # 1day    
  15220 : [ "AccHour",             "RO",  "Accumulated hour",                                  1,     15221,   "hour",  "p",     "" ],    # 1hour   
  15221 : [ "AccMinute",           "RO",  "Accumulated minute",                                1,    -15219,   "mn",    "p",     "" ],    # 1minute 

# Part 2.1 : Inverter Control Message : 20001 - 10016
  # Key : [  jsonName            regType   DisplayName ",                                  multCoef    Link   Unit  Instructions Remarks  Observations
  20000 : [ "InvrtrMachineType",   "RO",  "The type of machine",                               1,     20001,   "",      "?",     "PH1000/PH3000/PH1800" ],
  20001 : [ "InvrtrMachineType2",  "RO",  "The type of machine Low",                           1,    -20000,   "",      "?",     "PH1000/PH3000/PH1800" ],
  20002 : [ "UserSerNum",          "RW",  "User Serial number",                                1,     20003,   "",      "?",     "" ],  
  20003 : [ "UserSerNum2",         "RW",  "User Serial number Low",                            1,    -20002,   "",      "?",     "" ],       
  20004 : [ "InvrtrHardVer",       "RO",  "Inverter Hardware version",                         1,         0,   "",      "ver",   "" ],    # 1.00.00
  20005 : [ "InvrtrSoftVer",       "RO",  "Inverter Software version",                         1,         0,   "",      "ver",   "" ],    # 1.00.00 
  20006 : [ "ProtocolEditionNo",   "RO",  "Protocol Edition number",                           1,         0,   "",      "p",     "" ],
  20009 : [ "InvrtrBatVCalibCoef", "RW",  "Battery voltage calibration coefficient",           1,         0,   "",      "mn",    "" ],    # 16384
  20010 : [ "InvrtrVCalibCoef",    "RW",  "Inverter voltage calibration coefficient",          1,         0,   "",      "mn",    "" ],    # 16384
  20011 : [ "GridVCalibCoef",      "RW",  "Grid voltage calibration coefficient",              1,         0,   "",      "mn",    "" ],    # 16384 
  20012 : [ "BusVCalibCoef",       "RW",  "Bus voltage calibration coefficient",               1,         0,   "",      "mn",    "" ],    # 16384
  20013 : [ "ControlACalibCoef",   "RW",  "Control Current calibration coefficient",           1,         0,   "",      "mn",    "" ],    # 16384
  20014 : [ "InvrtrACalibCoef",    "RW",  "Inverter Current calibration coefficient",          1,         0,   "",      "mn",    "" ],    # 16384
  20015 : [ "GridACalibCoef",      "RW",  "Grid Current calibration coefficient",              1,         0,   "",      "mn",    "" ],    # 16384
  20016 : [ "LoadACalibCoef",      "RW",  "Load Current calibration coefficient",              1,         0,   "",      "mn",    "" ],    # 16384

# Part 2.2 : Inverter Control Message : 20101 - 20143
  # Key : [  jsonName            regType   DisplayName ",                                  multCoef    Link   Unit  Instructions Remarks  Observations
  20101 : [ "InvrtrOffGridWrkOk",  "RW",  "Inverter offgrid work enable",                      1,         0,   "map",   {            
              0 : [ "OFF",                  "Shut down the inverter output when the grid is off." ],
              1 : [ "ON",                   "Turn on the inverter output when the grid is off." ]
              },                                                                                                                 "effective range : 0,1 the default value is 1" ],
  20102 : [ "InvrtrOutputVSet",    "RW",  "Inverter output voltage Set",                       0.1,       0,   "V",     "p",     "220.0V-240.0V  (2200-2400)  Set the output voltage amplitude." ],
  20103 : [ "InvrtrOutputHzSet",   "RW",  "Inverter output frequency Set",                     0.01,      0,   "Hz",    "p",     "50.00Hz/60.00Hz  5000/6000  Set the output frequency." ],
  20104 : [ "InvrtrSearchMode",    "RW",  "Inverter search mode enable",                       1,         0,   "map",   {            
              0 : [ "OFF",                  "If disabled, no matter connect load is low or high, the on/off status of inverter output will not be effected." ],
              1 : [ "ON",                   "If enable, the inverter begins search mode if the AC load connected is pretty low or not detected. The inverter’s “search” mode reduces stand-by energy consumption during no-load conditions." ] 
              },                                                                                                                 "effective range : 0,1 the default value is 0" ],
  20108 : [ "InvrtrDisToGridOK",   "RW",  "Inverter discharger to grid enable",                1,         0,   "map",   {            
              0 : [ "OFF",                  "Disable  Inveter discharging from battery to grid when the Inverter is connnectted to Grid" ], 
              1 : [ "ON",                   "Enable Inveter discharging from battery to grid when the Inverter is connnectted to Grid" ]   
              },                                                                                                                 "effective range : 0,1 the default value is 1" ],
  20109 : [ "OutSrcePriority",     "RW",  "Output source priority selection",                  1,         0,   "map",   {            
              1 : [ "SBU",                  "Solar energy provides power to the loads as first priority, If solar energy is not sufficient to power all connected loads, battery energy will supply power to the loads at the same time. Utility provides power to the loads only when battery voltage drops to either low-level warning voltage or the setting point in program 20118 (20) or solar and battery is not sufficient. The battery energy will supply power to the load in the condition of the utility is unavailable or the battery voltage is higher than the setting point in program 20119 (21) (when BLU is selected) or program 20118 (20) (when LBU is selected). If the solar is available, but the voltage is lower than the setting point in program 20118 (20), the utility will charge the battery until the battery voltage reaches the setting point in program 20118 (20) to protect the battery from damage." ],
              2 : [ "SUB",                  "Solar energy provides power to the loads as first priority, If solar energy is not sufficient to power all connected loads, Utility energy will supply power to the loads at the same time. The battery energy will supply power to the load only in the condition of the utility is unavailable. If the solar is unavailable, the utility will charge the battery until the battery voltage reaches the setting point in program 20119 (21). If the solar is available, but the voltage is lower than the setting point in program 20118 (20), the utility will charge the battery until the battery voltage reaches the setting point in program 20118 (20) to protect the battery from damage." ],
              3 : [ "UTI",                  "Utility will provide power to the loads as first priority. Solar and battery energy will provide power to the loads only when utility power is not available." ],
              4 : [ "SOL",                  "Solar energy provides power to the loads as first priority. If battery voltage has been higher than the setting point in program 20119 (21) for 5 minutes, and the solar energy has been available for 5 minutes too, the inverter will turn to battery mode, solar and battery will provide power to the loads at the same time. When the battery voltage drops to the setting point in program 20118 (20), the inverter will turn to bypass mode, utility provides power to the load only, and the solar will charge the battery at the same time." ]
              },                                                                                                                 "" ],    # refer to user's manual        
  20111 : [ "AcInVRange",          "RW",  "AC input voltage range",                            1,         0,   "map",   {            
              0 : [ "VDE4105",              "If selected, acceptable AC input voltage range will conform to VDE4105(184VAC-253VAC)" ], 
              1 : [ "UPS",                  "If selected, acceptable AC input voltage range will be within 170-280VAC." ],
              2 : [ "APL",                  "Default. If selected, acceptable AC input voltage range will be within 90-280VAC." ],
              3 : [ "GEN",                  "When the user uses the device to connect the generator, select the generator mode." ]      
              },                                                                                                                 "" ],    # refer to user's manual    
  20112 : [ "SolarUseAim",         "RW",  "Solar supply priority",                             1,         0,   "map",   {
              0 : [ "LBU",                  "Solar energy provides power to the loads as first priority. If the battery voltage is lower than the setting point in program 20, the solar energy will never supply to the load or feed into the grid, only charge the battery. If the battery voltage is higher than the setting point in program 20, the solar energy will supply to the load or feed into the grid or recharge the battery." ],                                                      
              1 : [ "BLU",                  "Solar energy provides power to charge battery as first priority. When the utility is available, if the battery voltage is lower than the setting point in program 21, the solar energy will never supply to the load, only charge the battery. If the battery voltage is higher than the setting point in program 21, the solar energy will supply to the load or recharge the battery. (default)" ] 
              },                                                                                                                 "" ],
  20113 : [ "InvrtrMaxDisA",       "RW",  "Inverter max discharger current",                   0.1,       0,   "A",     "p",     "" ],    # 0.1A（AC)  1.0A-17.4A（10-174） Set the max discharging current from Inverter
  20118 : [ "BatStopDisV",         "RW",  "Battery stop discharging voltage",                  0.1,       0,   "V",     "p",     "" ],    # 0.1V  440~580(44.0-58.0)V the default value is 46.0V  refer to user's manual
  20119 : [ "BatStopChargingV",    "RW",  "Battery stop charging voltage",                     0.1,       0,   "V",     "p",     "" ],    # 0.1V  440~580(44.0-58.0)V the default value is 54.0V  refer to user's manual
  20125 : [ "GridMaxChargrASet",   "RW",  "Grid max charger current set",                      0.1,       0,   "A",     "p",     "" ],    # 0.1A(DC)  10~800(1.0-80.0)A the default value is 60.0A  
  20127 : [ "InvrtrBatLowV",       "RW",  "Battery low voltage",                               0.1,       0,   "V",     "p",     "" ],    # 0.1V  400~480(40.0-48.0)V the default value is 40.8V    
  20128 : [ "InvrtrBatHighV",      "RW",  "Battery high voltage",                              0.1,       0,   "V",     "p",     "" ],    # 0.1V  580~600(58.0-60.0)V the default value is 60.0V    
  20132 : [ "MaxCombineChargrA",   "RW",  "Max Combine charger current",                       0.1,       0,   "A",     "p",     "" ],    # 0.1A(DC)  10~1400(1.0-140.0)A the default value is 60.0A    
  20142 : [ "SystemSetting",       "RW",  "System setting",                                    1,         0,   "bit",   {
               0 : "Auto restart when overload occurs",
               1 : "Auto restart when over temperature occurs",
               2 : "Overload bypass: When enabled, the unit will transfer to line mode if overload occurs in battery mode.",
               3 : "Auto turn page",
               4 : "GridBuzzEnable(only use by PV1800)",
               5 : "BuzzForbide(only use by PV1800)",
               6 : "Lcd backlight enable",
               7 : "RecordFaultForbid",
              },                                                                                                                 "" ],    # refer to the frame System setting bit   
  20143 : [ "ChargrSrcPriority",   "RW",  "Charger source priority",                           1,         0,   "map",  {
              0 : [ "SCO - Solar first",    "Solar energy will charge battery as first priority. Utility will charge battery only when solar energy is not available." ],                                                 
              2 : [ "SNU - Solar & Utility","Default. Solar energy and utility will charge battery at the same time." ],
              3 : [ "OSO - Only Solar",     "Solar energy will be the only charger source no matter utility is available or not." ] 
              },                                                                                                                 "To configure charger source priority. If this inverter/charger is working in Battery mode, only solar energy can charge battery. Solar energy will charge battery if it's available and sufficient." ], 

# Part 2.3 : Inverter Control Message : 20213 - 20214
  # Key : [  jsonName            regType   DisplayName ",                                  multCoef    Link   Unit  Instructions Remarks  Observations
  20213 : [ "RemoveAcc",           "RW",  "Remove the accumulated",                            1,         0,   "map",  {            
              0 : [ "No remove the accumulated data",   "" ],
              1 : [ "Remove the accumulated data",      "" ]
              },                                                                                                                 "The default value is 0; effective range:0,1" ],
  20214 : [ "ResetParam",          "RW",  "Reset the parameter",                               1,         0,   "map",  {            
              0 : [ "No effect",            "" ],                                                           
              1 : [ "Action",               "" ]
              },                                                                                                                 "The default value is 0; effective range:0,1" ],

# Part 3 : Inverter Display Message : 25201 - 25275
  # Key : [  jsonName            regType   DisplayName ",                                  multCoef    Link   Unit  Instructions Remarks  Observations
  25201 : [ "InvrtrWorkState",     "RO",  "Work state",                                        1,         0,   "map",  {
              0 : [ "Power On",             "The inverter is powering on." ],
              1 : [ "Self Test",            "The inverter is performing a self test." ],
              2 : [ "Off Grid",             "The inverter will provide output power from battery and PV power. Inverter power loads from PV energy. Inverter power loads from battery and PV energy. Inverter power loads from battery only." ],
              3 : [ "Grid-Tie",             "PV energy is charger PV is on into the battery and utility provide power to the AC load. PV is on PV is off" ],  
              4 : [ "Bypass",               "Error are caused by inside circuit error or external reasons such as over temperature, output short circuited and so on." ],
              5 : [ "Stop",                 "The inverter stop working if you turn off the inverter by the soft key or error has occurred in the condition of no grid." ],
              6 : [ "Grid Charging",        "PV energy and grid can charge batteries." ]
              },                                                                                                                 "" ],
  25202 : [ "AcVGrade",            "RO",  "AC voltage grade",                                  1,         0,    "V",    "p",     "" ],  
  25203 : [ "RatedVA",             "RO",  "Rated power",                                       1,         0,    "VA",   "p",     "PV1800 => VA / PH3000 => W" ],    # PV1800 VA/PH3000 W
  25205 : [ "InvrtrBatV",          "RO",  "Battery voltage",                                   0.1,       0,    "V",    "p",     "" ],
  25206 : [ "InvrtrV",             "RO",  "Inverter voltage",                                  0.1,       0,    "V",    "p",     "" ],
  25207 : [ "GridV",               "RO",  "Grid voltage",                                      0.1,       0,    "V",    "p",     "" ],
  25208 : [ "BusV",                "RO",  "BUS voltage",                                       0.1,       0,    "V",    "p",     "" ],
  25209 : [ "CtrlA",               "RO",  "Control current",                                   0.1,       0,    "A",    "p",     "" ], 
  25210 : [ "InvrtrA",             "RO",  "Inverter current",                                  0.1,       0,    "A",    "p",     "" ],
  25211 : [ "GridA",               "RO",  "Grid current",                                      0.1,       0,    "A",    "p",     "" ],
  25212 : [ "LoadA",               "RO",  "Load current",                                      0.1,       0,    "A",    "p",     "" ],
  25213 : [ "InvrtrW",             "RO",  "Inverter power(P)",                                 1,         0,    "W",    "mn",    "" ],
  25214 : [ "GridW",               "RO",  "Grid power(P)",                                     1,         0,    "W",    "mn",    "" ],
  25215 : [ "LoadW",               "RO",  "Load power(P)",                                     1,         0,    "W",    "mn",    "" ],
  25216 : [ "LoadPcent",           "RO",  "Load percent",                                      1,         0,    "%",    "p",     "" ],
  25217 : [ "InvrtrCxVA",          "RO",  "Inverter complex power(S)",                         1,         0,    "VA",   "mn",    "" ],
  25218 : [ "GridCxVA",            "RO",  "Grid complex power(S)",                             1,         0,    "VA",   "mn",    "" ],
  25219 : [ "LoadCxVA",            "RO",  "Load complex power(S)",                             1,         0,    "VA",   "mn",    "" ],
  25221 : [ "InvrtrReactWar",      "RO",  "Inverter reactive power(Q)",                        1,         0,    "var",  "mn",    "" ],
  25222 : [ "GridReactWar",        "RO",  "Grid reactive power(Q)",                            1,         0,    "var",  "mn",    "" ],
  25223 : [ "LoadReactWar",        "RO",  "Load reactive power(Q)",                            1,         0,    "var",  "mn",    "" ],
  25225 : [ "InvrtrHz",            "RO",  "Inverter frequency",                                0.01,      0,    "Hz",   "p",     "" ],
  25226 : [ "GridHz",              "RO",  "Grid frequency",                                    0.01,      0,    "Hz",   "p",     "" ],
  25229 : [ "InvrtrMaxNum",        "RO",  "Inverter max number",                               0.1,       0,    "",     "p",     "" ],
  25230 : [ "CombineType",         "RO",  "Combine type",                                      0.1,       0,    "",     "p",     "" ],
  25231 : [ "InvrtrNum",           "RO",  "Inverter number",                                   0.1,       0,    "",     "p",     "" ],
  25233 : [ "AcT",                 "RO",  "AC radiator temperature",                           1,         0,    "°C",   "p",     "" ],
  25234 : [ "TrT",                 "RO",  "Transformer temperature",                           1,         0,    "°C",   "p",     "" ],
  25235 : [ "DcT",                 "RO",  "DC radiator temperature",                           1,         0,    "°C",   "p",     "" ],
  25237 : [ "InvrtrRelayState",    "RO",  "Inverter relay state",                              0.1,       0,    "map",  { 
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  25238 : [ "GridRelayState",      "RO",  "Grid relay state",                                  0.1,       0,    "map",  { 
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  25239 : [ "LoadRelayState",      "RO",  "Load relay state",                                  0.1,       0,    "map",  { 
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  25240 : [ "NLineRelayState",     "RO",  "N_Line relay state",                                0.1,       0,    "map",  { 
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  25241 : [ "DcRelayState",        "RO",  "DC relay state",                                    0.1,       0,    "map",  { 
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  25242 : [ "EarthRelayState",     "RO",  "Earth relay state",                                 0.1,       0,    "map",  { 
              0 : [ "Disconnect",             "" ],
              1 : [ "Connect",                "" ]
              },                                                                                                                 "" ],
  25245 : [ "AccChargrWh",         "RO",  "Accumulated charger power",                  1000000,      25246,    "Wh",   "p",     "" ],    # 1000KWH
  25246 : [ "AccChargrWh2",        "RO",  "Accumulated charger power low",                  100,     -25245,    "Wh",   "p",     "" ],    # 0.1KWH  
  25247 : [ "AccDischargrWh",      "RO",  "Accumulated discharger power",               1000000,      25248,    "Wh",   "p",     "" ],    # 1000KWH 
  25248 : [ "AccDischargrWh2",     "RO",  "Accumulated discharger power low",               100,     -25247,    "Wh",   "p",     "" ],    # 0.1KWH
  25249 : [ "AccBuyWh",            "RO",  "Accumulated buy power",                      1000000,      25250,    "Wh",   "p",     "" ],    # 1000KWH 
  25250 : [ "AccBuyWh2",           "RO",  "Accumulated buy power low",                      100,     -25249,    "Wh",   "p",     "" ],    # 0.1KWH
  25251 : [ "AccSellWh",           "RO",  "Accumulated sell power",                     1000000,      25252,    "Wh",   "p",     "" ],    # 1000KWH 
  25252 : [ "AccSellWh2",          "RO",  "Accumulated sell power low",                     100,     -25251,    "Wh",   "p",     "" ],    # 0.1KWH  
  25253 : [ "AccLoadWh",           "RO",  "Accumulated load power",                     1000000,      25254,    "Wh",   "p",     "" ],    # 1000KWH 
  25254 : [ "AccLoadWh2",          "RO",  "Accumulated load power low",                     100,     -25253,    "Wh",   "p",     "" ],    # 0.1KWH
  25255 : [ "AccSelfUseWh",        "RO",  "Accumulated self use power",                 1000000,      25256,    "Wh",   "p",     "" ],    # 1000KWH 
  25256 : [ "AccSelfUseWh2",       "RO",  "Accumulated self use power low",                 100,     -25255,    "Wh",   "p",     "" ],    # 0.1KWH
  25257 : [ "AccPvSellWh",         "RO",  "Accumulated PV_sell power",                  1000000,      25258,    "Wh",   "p",     "" ],    # 1000KWH 
  25258 : [ "AccPvSellWh2",        "RO",  "Accumulated PV_sell power low",                  100,     -25257,    "Wh",   "p",     "" ],    # 0.1KWH  
  25259 : [ "AccGridChargrWh",     "RO",  "Accumulated grid_charger power",             1000000,      25260,    "Wh",   "p",     "" ],    # 1000KWH 
  25260 : [ "AccGridChargrWh2",    "RO",  "Accumulated grid_charger power low",             100,     -25259,    "Wh",   "p",     "" ],    # 0.1KWH  
  25261 : [ "ErrMsg1",             "RO",  "Error message 1",                                   1,         0,    "bit",  {
               0 : "Fan is locked when inverter is off",
               1 : "Inverter transformer over temperature",
               2 : "battery voltage is too high",
               3 : "battery voltage is too low",
               4 : "Output short circuited",
               5 : "Inverter output voltage is high",
               6 : "Overload time out",
               7 : "Inverter bus voltage is too high",
               8 : "Bus soft start failed",
               9 : "Main relay failed",
              10 : "Inverter output voltage sensor error",
              11 : "Inverter grid voltage sensor error",
              12 : "Inverter output current sensor error",
              13 : "Inverter grid current sensor error",
              14 : "Inverter load current sensor error",
              15 : "Inverter grid over current error"
              },                                                                                                                 "" ],    # Refer to frame Error message 1
  25262 : [ "ErrMsg2",             "RO",  "Error message 2",                                   1,         0,    "bit",  {
               0 : "Inverter radiator over temperature",
               1 : "Solar charger battery voltage class error",
               2 : "Solar charger current sensor error",
               3 : "Solar charger current is uncontrollable",
               4 : "Inverter grid voltage is low",
               5 : "Inverter grid voltage is high",
               6 : "Inverter grid under frequency",
               7 : "Inverter grid over frequency",
               8 : "Inverter over current protection error",
               9 : "Inverter bus voltage is too low",
              10 : "Inverter soft start failed",
              11 : "Over DC voltage in AC output",
              12 : "Battery connection is open",
              13 : "Inverter control current sensor error",
              14 : "Inverter output voltage is too low",
              },                                                                                                                 "" ],    # Refer to frame Error message 2
  25263 : [ "ErrMsg3",             "RO",  "Error message 3",                                   1,         0,    "bit",  {
              },                                                                                                                 "" ],    # Refer to frame Error message 3
  25265 : [ "WarnMsg1",            "RO",  "Warning message 1",                                 1,         0,    "bit",  {
               0 : "Fan is locked when inverter is on.",
               1 : "Fan2 is locked when inverter is on.",
               2 : "Battery is over-charged.",
               3 : "Low battery",
               4 : "Overload",
               5 : "Output power derating",
               6 : "Solar charger stops due to low battery.",
               7 : "Solar charger stops due to high PV voltage.",
               8 : "Solar charger stops due to over load.",
               9 : "Solar charger over temperature",
              10 : "PV charger communication error ",
              },                                                                                                                 "" ],    # Refer to frame Warning message 1
  25266 : [ "WarnMsg2",            "RO",  "Warning message 2",                                 1,         0,    "bit",  {
              },                                                                                                                 "" ],    # Refer to frame Warning message 2
  25269 : [ "InvrtrSerNum",        "RO",  "Serial number",                                     1,     25270,    "",     "p",     "" ],
  25270 : [ "InvrtrSerNum2",       "RO",  "Serial number Low",                                 1,    -25269,    "",     "p",     "" ],
  25271 : [ "InvrtrHardVer2",      "RO",  "Inverter Hardware version 2",                       1,         0,    "",     "ver",   "" ],    # 1.00.00 
  25272 : [ "InvrtrSoftVer2",      "RO",  "Inverter Software version 2",                       1,         0,    "",     "ver",   "" ],    # 1.00.00 
  25273 : [ "BatW",                "RO",  "Battery power",                                     1,         0,    "W",    "mn",    "" ],
  25274 : [ "BatA",                "RO",  "Battery current",                                   1,         0,    "A",    "mn",    "" ],
  25275 : [ "BatSoc",              "RO",  "Batt soc",                                          1,         0,    "%",    "p",     "" ],    # 1 % 
  25277 : [ "RatedW",              "RO",  "Rated Power W",                                     1,         0,    "",     "p",     "" ],    #
  25278 : [ "CommProtocol",        "RO",  "Communication Protocol Edition",                    1,         0,    "",     "p",     "" ],    #
  25279 : [ "ArrowFlag",           "RO",  "ArrowFlag",                                         1,         0,    "",     "p",     "" ],    #
}


FLUX = {

  'variable' : {
    'registers' : [

      'PvV',#Tension Panneau Voltaique
      'PvRelay',#Relais PV
      'MpptState',#État MPPT

      'LoadRelayState',#État du relais de la charge
      'ChargrBatV',#Tension de la batterie
      'ChargrA',#Courant du chargeur
      'ChargrW',#Puissance du chargeur
      'LoadW',#Puissance de la charge
      'ChargrBatVGrade',# Niveau de tension de la batterie
      'ChargrSrcPriority',#Priorité de la source de charge
      'LoadPcent',#Charge en pourcentage
      'ChargingState',#État de charge
      'BatRelay',#Relais de batterie

      'RadiatorT',#Température du radiateur
      'TrT',#Température du transformateur

      'ErrMsg',#Message d'erreur
      'WarnMsg',#Erreur du ventilateur

      'GridRelayState',#État du relais du réseau
      'GridW',#Puissance du réseau
      'GridV',#Tension du réseau
      'GridA',#Courant du réseau

      'InvrtrWorkState',#État de fonctionnement de l'onduleur
      'InvrtrBatV',#Tension de la batterie de l'onduleur
      'InvrtrV',#Tension de l'onduleur
      'InvrtrA',#Courant de l'onduleur
      'InvrtrW',#Puissance de l'onduleur

      
    ]
  },

  'fixe' : {
    'registers' : [
      'ChargrMachineType',
      'ChargrHardVersion',
      'ChargrSoftVersion',
      'BatType',#Type de batterie
      'BatAH',#Capacité de la batterie
      'ChargrWorkState',
      'ChargrBatLowV',
      'ChargrBatHighV',
      'MaxChargrA',
      'FloatV',
      'AbsorpV',
      'RatedA',#Courant nominal
      'RatedVA',#Puissance nominale
    ]},

  'client_var' : {

    'registers' : [

    'PvV',#Tension Panneau Voltaique
    'GridW',#Puissance du réseau
    'BatW',#Puissance Batterie
    'LoadW',#Puissance de la charge
    'ChargrW',



    'ErrMsg',#Message d'erreur
    'ErrMsg1',#Message d'erreur
    'ErrMsg2',#Message d'erreur
    'ErrMsg3',#Message d'erreur
    'WarnMsg',#Erreur du ventilateur
    'WarnMsg1',#Erreur du ventilateur'
    'WarnMsg2',#Erreur du ventilateur'
    ]}
}
