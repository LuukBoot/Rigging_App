
# Rigging app 
## Project Description 
This app checks the rigging and the crane according to the DNV standards. According to the DNV standerd the skew load factor is a standerd value. With the help of a python script it is possible to calculate this more in detail. After the calculations are done, with the help of the viktor program an automatic word document will be generated. The skew load factor is explained in the skewload.md document

First the rigging checks were made in an excel sheet, with the help of this app it will be more user friendly. 


## How to install and run the project
Dit moet ik nog uitvogelen aan de hand van de documentatie van viktor



## How to use the project 
Ik moet nog een handleiding maken, die komt hier te staan

## App layout 
Hier moet app layout komen

## Workflowdiagram 
In this chapter the workflow diagram is described, see below the the total workflow diagram
![This is a image](/Images_read_me/Workflow.jpg)

In the upper part of the figure the input of the application  is shown and  at the left the data bases for rigging equipment/ constants is shown. Both these database are excel sheets and the data in these files can easily be changed. With the help of the module openpyxl the data from the excel sheet is transformed to usefull data. 

<br/><br/>
The frontend of the app consists of 5 different tabs, check next chapter what the parameters are of each tab. All the params and the data from the excel sheet are passed to the communication class. The first thing the class does is changing the params in to useful data, in which way it is stored can be seen in the next chapter. When all the data is transformed, all the caluculations are done. These are:

- The cog envelope (Class: Calc_COG_env)
- Load distributie/ Cog shift factor (Class: Calc_load_dis))
- Tilt factor (Class: Tilt factor)
- Calculations of the factors that are descibed in next chapter: tab_3 (Class: Calc_factors)
- Calculated the rigging checks and unity check(Class: Calc_rigging)
- Caluclated crane checks and unity check(Class: Calc_crane)

All the data from the parameters and the data from the results from the calulations are attributed from the communication class, so it can be used in other methods. With the help of the property method the data can be retrieved, so it can be shown in 3 different tabs( see part under communcation class):

- First tab:
    - Ouput load distributie[t]
    - Output load distributie[%]
    - Output all factors 
- Second tab: Checks rigging
- Third tab: Checks crane 



<br/><br/>
Both the skew load analysis and the make word document are not in the communication class, because every time a params is changed in one of the 5 tabs. The communcation class will be activated and those two actions take a lot of time, this is why it is done with the help of buttons. When the skew load analysis button is pressed, first it gets the data from the communication class and  it will anlaysis the skew load factor, when the analysis is done the result will be stored in a CSV file, so it can be retrieved when making the word document. 

<br/><br/>
When the word document button is activated, it takes all data and results from the calculations from the communcation class, also the file params. These are params such as the date/the project no/ company name.  With the help of the jinja notations, the results and data are transformed in a readable rigging check documentation, this word document can be downloaded via the internet and can be changed where necessary. 

### Input 
The front off the app is made with the help of the viktor program, in total there are 5 different input apps: See below:
#### Tab 1
In tab 1 the general information is entered:



- Number of lifting points 
- Coardinates of lifting points 
- COG point 
- Lift object geometry 
- Lift object weight 
- Coardinates of lifting points

With the help of the method make_data_general the data is stored in the structure, that is shown below:

```
Data_general={"Lift_points": [nx[float(point_x),float(point_y),float(point_z)]],
              "Obj_geo": [float(length),float(width),float(height],
              "COG": [float(COG_x),float(COG_y),float(COG_z],
              "LW": float(weight of liftobject)}
```
In de lift points, the n is equal to number of lifting points

#### Tab 2
In tab 2, the values for the Factors, sling safety factor and the skew load factor are entered. In section 1the parameters for the factors are entered, those are:

- Answer weight continency factor
- Answer COG shift factor crane
- Answer COG shift factor rigging
- Answer dynamic amplication factor
- Answer YAW factor
- Angles Tilt factor



With the help of the method make_general factors the data is stored in a diactionary structure, that is shown below:

```
Data_general_factor={"WCF":str(answer),
                        "COGCrane":str(answer),
                        "COG_envelope":str(answer),
                        "DAF":str(answer),
                        "YAW":str(answer),
                        "TEF":[float(Roll angle), float(Pitch angle)]}

```
In section 2 the values for the sling safetry factor are entered, the params are:

- Anwer Lift factor
- Answer Material factor
- Answer Consequence factor
- Answer Wear/application factor

With the help of the method make_data_SSF_factor factors the data is stored in a array with a number of dictionaries that depends on the number of sling safety factors, see below code snippet:

```
Data_sling_safetry=[{"Lift_factor":float(answer),
                     "Consequence_factor":float(answer),
                     "material_factor":str(answer,
                     "Wear_application_factor":str(answer}]

```

The answers for the skew load factor are entered in section 3, see other page.
 
#### Tab 3
In tab 3, the values for the rigging check are entered

- Name of the rigging point
- Material of the sling/grommet
- Which points are connected 
- Rigging weight above the lifting point
- Sling angle with the transverse
- Sling angle with the longitudinal 
- Sling safety factor 
- Termination factor 
- Skew load factor 
- Sldf factor 
- Type sling:
    - Amount of parts 
    - ID(SWL and diameter)
- Connection upper side sling/grommet:
    - Type 
    - Diameter 
    - SWL 
- Connection lower side sling/grommet:
    - Type 
    - Diameter 
    - SWL 

With the help of the method make_data_rigging factors the data is stored in a array with a number of dictionaries that depends on the rigging points that needs to be checked, see below code snippet:

```
Data_rigging=[{"Name": str(rigging_point_name),
               "Materal": str(Material sling/grommet),
               "Points": list(points connected to the rigging),
               "RWP": float(rigging weight),
               "Angle_1": float(transvere_angle),
               "Angle_2": float(longitudinal_angle),
               "TRF_ans": str(answer TRF factor)
               "SSF_ans": str(Sling safety factor),
               "SKL": [str(answer skl), int(the sling from the analyes)],
               "SLDF" : str(ans sling load distribution factor),
               "sling":[str(id_number),str(type),float(swl),float(diameter),float(n_parts)],
               "Connection_upper":[str(type),float(diameter),float(swl],
               "Connection_lower":[str(type),float(diameter),float(swl]
               }]

```

#### Tab 4
In tab 3, the values for the crane check are entered

- Which crane lifts the lifting point
- Which hoist lifts the lifting point
- The capacity of the hoist 
- The offlead angle of the hoists 

With the help of the method make_data_cranes the data is stored in the a dictionary see code snippet below:

```
data_crane{str(Crane_name):{"DDF": float(DDF_factor),
                            str(hoist): "Data":[float(Capacity),float(off_lead),float(RW)],
                                        "Points": list(points that are lifted by hoist)}

```

If there are multiple cranes used the, there will be two crane names in the keys of the dictionary data_cran, there is a max of two cranes that can be used. If there are multiple hoist used, there will be a hoist added in the diactionary data_crane[Crane_name], with the right info.

## Recommendations
When there are made many more extensions to the app and the app gets slow it is recommended to change the structure of the app in such a way that when a parameters is changed not all calculations in the communcation class have to be done. For now the app is still fast enough so it is not necessary to change the structure of the app. 